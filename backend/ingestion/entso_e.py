"""ENTSO-E data ingestion module."""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

try:
    from entsoe import EntsoePandasClient
except ImportError:
    EntsoePandasClient = None

from backend.config import get_settings
from backend.ingestion.base import IngestionModule
from backend.db.models import IndicatorValue

logger = logging.getLogger(__name__)


class EntsoeIngestionModule(IngestionModule):
    """Fetches and derives hourly electricity flows for Baltic-Nordic interconnectors."""

    def __init__(self):
        self.settings = get_settings()
        self.client = None
        if not self.settings.demo_mode and self.settings.entsoe_api_key and EntsoePandasClient:
            self.client = EntsoePandasClient(api_key=self.settings.entsoe_api_key)

        self.pairs = [
            ("FI", "EE", ["estlink_1", "estlink_2"]),
            ("EE", "LV", ["ee_lv_electric"]),
            ("LV", "LT", ["lv_lt_electric"]),
            ("SE_4", "LT", ["nordbalt"]),
            ("PL", "LT", ["litpol_link"]),
        ]

    @property
    def source_name(self) -> str:
        return "entso_e"

    def fetch(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        if self.settings.demo_mode:
            logger.info("DEMO_MODE=True: Loading ENTSO-E offline seed.")
            seed_path = Path(__file__).parent.parent.parent / "data" / "seed" / "entso_e_flows.csv"
            if seed_path.exists():
                df = pd.read_csv(seed_path)
                df = df.rename(columns={"date": "timestamp"})
                return df
            return pd.DataFrame()

        if not self.client:
            logger.error("ENTSO-E client not initialized. Check API key.")
            return pd.DataFrame()

        import pytz
        tz = pytz.timezone("Europe/Brussels")
        start_tz = pd.Timestamp(start_date).tz_localize("UTC").tz_convert(tz)
        end_tz = pd.Timestamp(end_date).tz_localize("UTC").tz_convert(tz)

        frames = []
        for (c_from, c_to, link_ids) in self.pairs:
            try:
                flow_fwd = self.client.query_crossborder_flows(c_from, c_to, start=start_tz, end=end_tz)
                if isinstance(flow_fwd, pd.Series):
                    flow_fwd = flow_fwd.to_frame(name="flow_mw")
                flow_fwd["from_country"] = c_from.split("_")[0]
                flow_fwd["to_country"] = c_to.split("_")[0]
                flow_fwd["interconnector_id"] = link_ids[0]
                # Default mock nominal capability if via live API
                flow_fwd["capacity_mw"] = 500.0  
                
                frames.append(flow_fwd)
            except Exception as e:
                logger.error(f"Failed fetching ENTSO-E flow {c_from}-{c_to}: {e}")

        if not frames:
            return pd.DataFrame()

        df = pd.concat(frames)
        df = df.reset_index().rename(columns={"index": "timestamp"})
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
            
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        if df["timestamp"].dt.tz is not None:
            df["timestamp"] = df["timestamp"].dt.tz_convert("UTC").dt.tz_localize(None)
            
        result_rows = []
        
        # Aggregate by timestamp for derived metrics
        dates = df["timestamp"].unique()
        
        for ts in dates:
            df_ts = df[df["timestamp"] == ts]
            
            # 1. estlink_utilization (Estlink 1 + 2 for FI -> EE)
            df_estlink = df_ts[df_ts["interconnector_id"].str.contains("estlink")]
            if not df_estlink.empty:
                flow_sum = df_estlink["flow_mw"].sum()
                
                # Compute AVAILABLE capacity (only sum capacity of links actually online)
                # Being conservative: if flow is > 0, it's considered online.
                # Strictly to handle the offline drop, we only count cap if flow > 0 or it's a stable period.
                # Actually, an explicit rule: if flow == 0 but capacity is defined, it is a forced outage for our seed.
                df_online = df_estlink[df_estlink["flow_mw"] > 0]
                available_cap_sum = df_online["capacity_mw"].sum()
                
                if available_cap_sum == 0:
                    utilization = 1.0 # Absolute stress if 0 capacity is available
                else:
                    utilization = flow_sum / available_cap_sum
                    
                result_rows.append({
                    "indicator_id": "estlink_utilization",
                    "country_id": "EE",
                    "region_id": None,
                    "timestamp": ts,
                    "raw_value": float(utilization),
                    "source": self.source_name,
                    "data_quality": "current",
                })
                    
            # 2. interconnectors_offline (Count of edges with 0 flow when they should have flow)
            # Simplistic static evaluation: if capacity > 0 but flow == 0
            for country in df_ts["to_country"].unique():
                df_c = df_ts[df_ts["to_country"] == country]
                offline_count = sum((df_c["flow_mw"] == 0) & (df_c["capacity_mw"] > 0))
                result_rows.append({
                    "indicator_id": "interconnectors_offline",
                    "country_id": country,
                    "region_id": None,
                    "timestamp": ts,
                    "raw_value": float(offline_count),
                    "source": self.source_name,
                    "data_quality": "current",
                })
                
                # 3. electricity_import_ratio
                # Proxy: net_imports / assumption(1000MW generic consumption for EE/LT/LV)
                gross_imports = df_c["flow_mw"].sum()
                consumption_assumption = 1000.0 if country in ["EE", "LV", "LT"] else 8000.0
                eir = gross_imports / consumption_assumption
                result_rows.append({
                    "indicator_id": "electricity_import_ratio",
                    "country_id": country,
                    "region_id": None,
                    "timestamp": ts,
                    "raw_value": float(eir),
                    "source": self.source_name,
                    "data_quality": "current",
                })
                
        df_indicators = pd.DataFrame(result_rows)
        
        # 4. cross_border_flow_anomaly (Z-score 30 day rolling)
        new_rows = []
        for country in df_indicators["country_id"].unique():
            df_country = df[df["to_country"] == country].groupby("timestamp")["flow_mw"].sum().reset_index()
            if df_country.empty:
                continue
            df_country = df_country.sort_values("timestamp").set_index("timestamp")
            
            # Calculate 30-day rolling mean/std mapping accurately natively back
            rolling_mean = df_country["flow_mw"].rolling("30D", min_periods=1).mean()
            rolling_std = df_country["flow_mw"].rolling("30D", min_periods=1).std().replace(0, np.nan)
            
            z_scores = (df_country["flow_mw"] - rolling_mean) / rolling_std
            z_scores = z_scores.fillna(0.0) # Avoid unbound NaNs in stable periods
            
            for ts, z_val in z_scores.items():
                new_rows.append({
                    "indicator_id": "cross_border_flow_anomaly",
                    "country_id": country,
                    "region_id": None,
                    "timestamp": ts,
                    "raw_value": float(abs(z_val)),
                    "source": self.source_name,
                    "data_quality": "current",
                })
                
        # 5. days_since_last_disruption
        days_rows = []
        for country in df["to_country"].unique():
            df_country = df[df["to_country"] == country].sort_values("timestamp")
            last_disrupt = None
            for _, row in df_country.iterrows():
                # We consider flow_mw == 0 and capacity_mw > 0 as a disruption event
                if row.get("flow_mw", 1) == 0 and row.get("capacity_mw", 0) > 0:
                    last_disrupt = row["timestamp"]
                
                if last_disrupt is None:
                    days = 100.0  # Cap the max days arbitrarily to 100 for normalization bounds
                else:
                    days = float((row["timestamp"] - last_disrupt).days)
                    
                days_rows.append({
                    "indicator_id": "days_since_last_disruption", 
                    "country_id": country, 
                    "region_id": None, 
                    "timestamp": row["timestamp"], 
                    "raw_value": days, 
                    "source": self.source_name, 
                    "data_quality": "current"
                })
                
        df_indicators = pd.concat([df_indicators, pd.DataFrame(new_rows), pd.DataFrame(days_rows)], ignore_index=True)
        return df_indicators

    def load(self, df: pd.DataFrame, session: Session) -> int:
        if df.empty:
            return 0
            
        objects = []
        for _, row in df.iterrows():
            obj = IndicatorValue(**row.to_dict())
            objects.append(obj)

        session.bulk_save_objects(objects)
        session.commit()
        return len(objects)
