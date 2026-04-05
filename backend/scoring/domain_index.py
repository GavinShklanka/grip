"""Domain scoring engine."""

import logging
import pandas as pd
import numpy as np

from backend.utils.normalization import min_max_normalize, invert_score, z_score

logger = logging.getLogger(__name__)


def compute_domain_scores(indicators_df: pd.DataFrame, config: dict, target_freq: str = "D") -> pd.DataFrame:
    """Core engine translating raw indicators into canonical domain scores.
    
    Pure mathematical sequence. No DB interaction inside this engine.
    
    Parameters
    ----------
    indicators_df : pd.DataFrame
        DataFrame with columns: ['indicator_id', 'country_id', 'timestamp', 'raw_value']
    config : dict
        The parsed domains.json dictionary.
    target_freq : str
        Resampling frequency.
        
    Returns
    -------
    pd.DataFrame
        Computed domain scores with columns: [country_id, timestamp, domain_id, score, velocity, data_coverage, anomaly_flag]
    """
    if indicators_df.empty:
        logger.info("No indicator data to score.")
        return pd.DataFrame()
        
    df = indicators_df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    domains = config.get("domains", [])
    countries = df["country_id"].dropna().unique()
    
    output_rows = []
    
    for country in countries:
        df_c = df[df["country_id"] == country].copy()
        df_c = df_c.drop_duplicates(subset=["timestamp", "indicator_id"])
        
        df_pivot = df_c.pivot(
            index="timestamp",
            columns="indicator_id",
            values="raw_value"
        ).resample(target_freq).ffill()
        
        for domain in domains:
            domain_id = domain["id"]
            indicators = domain["indicators"]
            
            score_components = []
            weight_components = []
            
            total_domain_weight = sum(ind["weight"] for ind in indicators)
            if total_domain_weight == 0:
                continue
                
            for ind in indicators:
                ind_id = ind["id"]
                if ind_id in df_pivot.columns:
                    s = df_pivot[ind_id].copy()
                    
                    if ind.get("normalization") == "minmax":
                        s = min_max_normalize(s)
                        
                    if ind.get("direction") == "lower_is_worse":
                        s = invert_score(s)
                        
                    w = ind["weight"]
                    score_components.append(s * w)
                    # For coverage calculation, note when an indicator is realistically mapped
                    weight_components.append(pd.Series(np.where(s.notna(), w, 0.0), index=s.index))
                    
            if not score_components:
                continue
                
            df_score_sum = pd.concat(score_components, axis=1).sum(axis=1)
            df_weight_sum = pd.concat(weight_components, axis=1).sum(axis=1)
            
            df_coverage = df_weight_sum / total_domain_weight
            
            # Linear penalty implementation
            df_final = df_score_sum
            
            # Velocity & Anomaly
            df_velocity = df_final.diff()
            if target_freq == "D":
                df_velocity_smoothed = df_velocity.rolling(window=7, min_periods=1).mean()
            else:
                df_velocity_smoothed = df_velocity
                
            vel_z = z_score(df_velocity_smoothed)
            df_anomaly = vel_z > 2.0
            
            for timestamp, val in df_final.items():
                if pd.isna(val):
                    continue
                    
                cov = df_coverage.loc[timestamp]
                vel = df_velocity_smoothed.loc[timestamp]
                anom = df_anomaly.loc[timestamp]
                
                output_rows.append({
                    "country_id": country,
                    "timestamp": timestamp,
                    "domain_id": domain_id,
                    "score": float(val),
                    "velocity": float(vel) if pd.notna(vel) else 0.0,
                    "data_coverage": float(cov),
                    "anomaly_flag": bool(anom)
                })
                
    return pd.DataFrame(output_rows)
