"""Seed data loader. Populates database from data/seed/ files for demo mode.

Usage: python -m backend.db.seed
Idempotent: truncates tables before loading.
"""

import json
from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import text

from backend.db.models import Base, IndicatorValue, TopologyState
from backend.db.session import init_db, create_tables, get_session_factory

SEED_DIR = Path(__file__).parent.parent.parent / "data" / "seed"
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"


def load_seed_data(database_url: str | None = None):
    """Load all seed data into the database. Truncates existing data first."""
    engine = init_db(database_url)
    create_tables(engine)
    Session = get_session_factory()
    session = Session()

    try:
        # Truncate all tables
        for table in ["alerts", "forecasts", "domain_scores", "indicator_values", "topology_state"]:
            session.execute(text(f"DELETE FROM {table}"))
        session.commit()
        print("Tables cleared.")

        # Load electricity flows
        _load_electricity_flows(session)

        # Load gas flows
        _load_gas_flows(session)

        # Load GDELT events
        _load_gdelt(session)

        # Load sanctions counts
        _load_sanctions(session)

        # Load static indicators
        _load_static(session)

        # Load topology state from config
        _load_topology_state(session)

        session.commit()
        print("Seed data loaded successfully.")

    except Exception as e:
        session.rollback()
        print(f"Error loading seed data: {e}")
        raise
    finally:
        session.close()


def _load_electricity_flows(session):
    df = pd.read_csv(SEED_DIR / "entso_e_flows.csv")
    records = []
    for _, row in df.iterrows():
        # Flow as indicator for the destination country
        records.append(IndicatorValue(
            indicator_id=f"flow_{row['interconnector_id']}",
            country_id=row["to_country"],
            timestamp=datetime.strptime(row["date"], "%Y-%m-%d"),
            raw_value=row["flow_mw"],
            normalized_value=None,  # computed by scoring engine
            source="entso_e",
            data_quality="current",
        ))
    session.bulk_save_objects(records)
    print(f"  Electricity flows: {len(records)} records")


def _load_gas_flows(session):
    df = pd.read_csv(SEED_DIR / "entsog_flows.csv")
    records = []
    for _, row in df.iterrows():
        records.append(IndicatorValue(
            indicator_id=f"flow_{row['point_id']}",
            country_id=row["to_area"],
            timestamp=datetime.strptime(row["date"], "%Y-%m-%d"),
            raw_value=row["flow_mcm"],
            normalized_value=None,
            source="entsog",
            data_quality="current",
        ))
    session.bulk_save_objects(records)
    print(f"  Gas flows: {len(records)} records")


def _load_gdelt(session):
    df = pd.read_csv(SEED_DIR / "gdelt_events.csv")
    records = []
    for _, row in df.iterrows():
        ts = datetime.strptime(row["week_start"], "%Y-%m-%d")
        for country in ["FI", "EE", "LV", "LT"]:
            records.append(IndicatorValue(
                indicator_id="gdelt_event_intensity",
                country_id=country,
                timestamp=ts,
                raw_value=row["event_count"],
                source="gdelt",
                data_quality="current",
            ))
            records.append(IndicatorValue(
                indicator_id="gdelt_tone_avg",
                country_id=country,
                timestamp=ts,
                raw_value=row["avg_tone"],
                source="gdelt",
                data_quality="current",
            ))
    session.bulk_save_objects(records)
    print(f"  GDELT events: {len(records)} records")


def _load_sanctions(session):
    df = pd.read_csv(SEED_DIR / "sanctions_counts.csv")
    records = []
    for _, row in df.iterrows():
        ts = datetime.strptime(row["date"], "%Y-%m-%d")
        for country in ["FI", "EE", "LV", "LT"]:
            records.append(IndicatorValue(
                indicator_id="sanctions_entity_count",
                country_id=country,
                timestamp=ts,
                raw_value=row["eu_entities_count"],
                source="opensanctions",
                data_quality="current",
            ))
            records.append(IndicatorValue(
                indicator_id="shadow_fleet_count",
                country_id=country,
                timestamp=ts,
                raw_value=row["shadow_fleet_estimate"],
                source="static",
                data_quality="current",
            ))
    session.bulk_save_objects(records)
    print(f"  Sanctions: {len(records)} records")


def _load_static(session):
    df = pd.read_csv(SEED_DIR / "static_indicators.csv")
    records = []
    for _, row in df.iterrows():
        ts = datetime(int(row["year"]), 12, 31)
        for col in ["defense_spending_gdp_pct", "reserve_to_active_ratio", "nato_exercises_count"]:
            records.append(IndicatorValue(
                indicator_id=col,
                country_id=row["country_id"],
                timestamp=ts,
                raw_value=row[col],
                source="static",
                data_quality="current",
            ))
    session.bulk_save_objects(records)
    print(f"  Static indicators: {len(records)} records")


def _load_topology_state(session):
    with open(CONFIG_DIR / "topology.json") as f:
        topo = json.load(f)

    records = []
    for ic in topo["nodes"]["interconnectors"]:
        records.append(TopologyState(
            edge_id=ic["id"],
            status="active",
            updated_at=datetime.utcnow(),
        ))
    session.bulk_save_objects(records)
    print(f"  Topology state: {len(records)} edges")


if __name__ == "__main__":
    load_seed_data()
