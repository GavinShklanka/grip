"""Phase 1 smoke tests. Validates foundation: configs, seed data, fixtures, schema."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
SEED_DIR = ROOT / "data" / "seed"


# --- Config integrity tests ---

class TestTopologyConfig:
    def test_loads_valid_json(self, topology_config):
        assert "nodes" in topology_config
        assert "interconnectors" in topology_config["nodes"]

    def test_has_focus_countries(self, topology_config):
        countries = topology_config["nodes"]["countries"]
        focus = [c for c in countries if c["type"] == "focus"]
        assert len(focus) == 4
        focus_ids = {c["id"] for c in focus}
        assert focus_ids == {"FI", "EE", "LV", "LT"}

    def test_has_interconnectors(self, topology_config):
        ics = topology_config["nodes"]["interconnectors"]
        assert len(ics) >= 9  # 6 electric + 3 gas
        ids = {ic["id"] for ic in ics}
        assert "estlink_1" in ids
        assert "estlink_2" in ids
        assert "balticconnector" in ids
        assert "litpol_link" in ids

    def test_all_edges_have_capacity(self, topology_config):
        for ic in topology_config["nodes"]["interconnectors"]:
            has_elec = "capacity_mw" in ic and ic["capacity_mw"] > 0
            has_gas = "capacity_mcm_day" in ic and ic["capacity_mcm_day"] > 0
            assert has_elec or has_gas, f"{ic['id']} missing capacity"

    def test_reserve_requirement_defined(self, topology_config):
        assert topology_config["reserve_requirement_mw"] == 1500


class TestDomainsConfig:
    def test_loads_valid_json(self, domains_config):
        assert "domains" in domains_config
        assert "composite" in domains_config

    def test_has_eight_domains(self, domains_config):
        assert len(domains_config["domains"]) == 8

    def test_weights_sum_to_one_per_domain(self, domains_config):
        for domain in domains_config["domains"]:
            total = sum(ind["weight"] for ind in domain["indicators"])
            assert abs(total - 1.0) < 0.001, f"{domain['id']} weights sum to {total}"

    def test_composite_weights_sum_to_one(self, domains_config):
        total = sum(d["weight_in_composite"] for d in domains_config["domains"])
        assert abs(total - 1.0) < 0.001, f"Composite weights sum to {total}"

    def test_each_domain_has_min_three_indicators(self, domains_config):
        for domain in domains_config["domains"]:
            assert len(domain["indicators"]) >= 3, f"{domain['id']} has {len(domain['indicators'])} indicators"


class TestThresholdsConfig:
    def test_loads(self, thresholds_config):
        assert "domain_thresholds" in thresholds_config
        assert "margin_thresholds_mw" in thresholds_config
        assert "risk_model_thresholds" in thresholds_config


# --- Seed data tests ---

class TestSeedData:
    def test_electricity_flows_exist(self, seed_electricity_flows):
        assert len(seed_electricity_flows) > 9000
        assert set(seed_electricity_flows["interconnector_id"].unique()) == {
            "estlink_1", "estlink_2", "nordbalt", "litpol_link",
            "ee_lv_electric", "lv_lt_electric"
        }

    def test_estlink2_zero_during_outage(self, seed_electricity_flows):
        df = seed_electricity_flows
        outage = df[(df["interconnector_id"] == "estlink_2") & (df["date"] == "2024-12-25")]
        assert len(outage) == 1
        assert outage.iloc[0]["flow_mw"] == 0.0

    def test_balticconnector_zero_during_outage(self, seed_gas_flows):
        df = seed_gas_flows
        outage = df[(df["point_id"] == "balticconnector") & (df["date"] == "2023-10-10")]
        assert len(outage) == 1
        assert outage.iloc[0]["flow_mcm"] == 0.0

    def test_disruption_events_count(self, disruption_events):
        events = disruption_events["events"]
        assert len(events) == 12
        energy_events = [e for e in events if e["is_energy_interconnector"]]
        assert len(energy_events) == 6

    def test_gas_flows_exist(self, seed_gas_flows):
        assert len(seed_gas_flows) > 6000

    def test_gdelt_exists(self, seed_gdelt):
        assert len(seed_gdelt) > 200


# --- Database fixture tests ---

class TestDatabaseFixtures:
    def test_engine_creates_tables(self, test_engine):
        from sqlalchemy import inspect
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()
        assert "indicator_values" in tables
        assert "domain_scores" in tables
        assert "forecasts" in tables
        assert "alerts" in tables
        assert "topology_state" in tables

    def test_sample_indicators_load(self, sample_indicator_values):
        from backend.db.models import IndicatorValue
        count = sample_indicator_values.query(IndicatorValue).count()
        assert count > 0

    def test_sample_scores_load(self, sample_domain_scores):
        from backend.db.models import DomainScore
        count = sample_domain_scores.query(DomainScore).count()
        assert count > 0


# --- Scenario config tests ---

class TestScenarios:
    def test_all_scenarios_load(self):
        scenario_dir = CONFIG_DIR / "scenarios"
        scenarios = list(scenario_dir.glob("*.json"))
        assert len(scenarios) == 6
        for s in scenarios:
            with open(s, encoding="utf-8") as f:
                data = json.load(f)
            assert "id" in data
            assert "overrides" in data
            assert len(data["overrides"]) > 0

    def test_estlink2_scenario_structure(self, estlink2_scenario):
        assert estlink2_scenario["id"] == "estlink2_severance"
        assert len(estlink2_scenario["overrides"]) == 1
        assert estlink2_scenario["overrides"][0]["edge_id"] == "estlink_2"
        assert estlink2_scenario["overrides"][0]["status"] == "offline"
