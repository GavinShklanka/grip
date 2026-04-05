"""Demo seed runner — populates DB with all indicator data, scoring, composite, and forecast on startup."""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.db.models import IndicatorValue, DomainScore
from backend.ingestion.entso_e import EntsoeIngestionModule
from backend.ingestion.entsog import EntsogIngestionModule
from backend.scoring import ScoringOrchestrator
from backend.scoring.escalation_composite import EscalationComposite

logger = logging.getLogger(__name__)
SEED_DIR = Path(__file__).parent.parent.parent / "data" / "seed"


def _load_csv_indicators(db: Session, path: Path, col_map: dict, source: str, ts_col: str = "date"):
    if not path.exists():
        return 0
    df = pd.read_csv(path)
    if ts_col in df.columns:
        df = df.rename(columns={ts_col: "timestamp"})
    elif ts_col == "year":
        df = df.rename(columns={"year": "timestamp"})
        df["timestamp"] = pd.to_datetime(df["timestamp"].astype(str) + "-01-01")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    rows = []
    for _, row in df.iterrows():
        c_id = row.get("country_id")
        targets = [c_id] if c_id and pd.notna(c_id) else ["EE", "FI", "LV", "LT"]
        for target_c in targets:
            for col, ind_id in col_map.items():
                if col in row.index and pd.notna(row[col]):
                    val = float(row[col])
                    if len(targets) > 1 and target_c != "EE":
                        val = val * float(np.random.uniform(0.8, 1.2))
                    rows.append(IndicatorValue(
                        indicator_id=ind_id, country_id=target_c,
                        timestamp=row["timestamp"], raw_value=val,
                        source=source
                    ))
    if rows:
        db.bulk_save_objects(rows)
        db.commit()
    return len(rows)


def seed_demo_data(db: Session):
    """Full demo seed pipeline: ingest → score → composite → forecast."""
    count = db.query(IndicatorValue).count()
    if count > 0:
        print("GRIP: Database already seeded. Skipping.")
        return

    start_dt = datetime(2022, 1, 1)
    end_dt = datetime(2026, 12, 31)

    logger.info("Seeding ENTSO-E flows...")
    entsoe = EntsoeIngestionModule()
    entsoe.run(db, start_dt, end_dt)

    logger.info("Seeding ENTSOG flows...")
    entsog = EntsogIngestionModule()
    entsog.run(db, start_dt, end_dt)

    logger.info("Seeding GDELT events...")
    _load_csv_indicators(db, SEED_DIR / "gdelt_events.csv",
                         {"event_count": "gdelt_event_intensity", "avg_tone": "gdelt_tone_avg",
                          "conflict_events": "diplomatic_incident_count"},
                         "gdelt", ts_col="week_start")

    logger.info("Seeding sanctions data...")
    _load_csv_indicators(db, SEED_DIR / "sanctions_counts.csv",
                         {"eu_entities_count": "sanctions_entity_count",
                          "shadow_fleet_estimate": "shadow_fleet_count"},
                         "sanctions", ts_col="date")

    logger.info("Seeding static indicators...")
    _load_csv_indicators(db, SEED_DIR / "static_indicators.csv",
                         {"defense_spending_gdp_pct": "defense_spending_gdp_pct",
                          "reserve_to_active_ratio": "reserve_to_active_ratio",
                          "nato_exercises_count": "nato_exercises_count"},
                         "static", ts_col="year")

    # Telecom + submarine cable
    telecom_rows = []
    for d in pd.date_range(start_dt, end_dt, freq="W"):
        for target_c in ["EE", "FI", "LV", "LT"]:
            for ind_id, val in [
                ("telecom_cable_status", 0.8), 
                ("submarine_cable_exposure", 0.75),
                ("telecom_cables_offline", 0.0),
                ("corridor_alternative_available", 1.0)
            ]:
                v = val * float(np.random.uniform(0.8, 1.2)) if target_c != "EE" and val > 0 else val
                telecom_rows.append(IndicatorValue(
                    indicator_id=ind_id, country_id=target_c, timestamp=d,
                    raw_value=v, source="static"
                ))
    db.bulk_save_objects(telecom_rows)
    db.commit()

    logger.info("Running domain scoring engine...")
    orch = ScoringOrchestrator(db)
    scored = orch.run_scoring(start_dt, end_dt)
    logger.info(f"  Generated {scored} domain score records.")

    logger.info("Computing escalation composite...")
    comp = EscalationComposite(db)
    comp_count = comp.update_database(start_dt, end_dt)
    logger.info(f"  Generated {comp_count} composite records.")

    logger.info("Running risk model forecast features...")
    from backend.ml.features import FeatureEngineer
    
    fe = FeatureEngineer(db)
    # Just generate features so inference can pick it up via API
    features_df = fe.generate_features(end_dt - pd.Timedelta(days=30), end_dt)
    if not features_df.empty:
        logger.info("  Features correctly bound inside DB window.")

    logger.info("Running alert rules...")
    # Generate mock alerts for recent anomalies (use existing scores)
    alerts = db.execute(select(DomainScore).where(DomainScore.score > 80)).scalars().all()
    for a in alerts:
        a.anomaly_flag = True
    db.commit()

    logger.info("Demo seed complete.")
