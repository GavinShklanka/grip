"""
Generate static JSON files from all GRIP API endpoints.
Run this with the backend server running on localhost:8000.

Usage:
  1. Start backend: DEMO_MODE=true uvicorn backend.main:app --port 8000
  2. Wait for seed to complete (~4 min first time)
  3. Run: python scripts/generate_static_api.py
"""

import requests
import json
import os
import sys
import time

BASE = "http://127.0.0.1:8000"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "api")

def fetch_and_save(path, filename):
    """Fetch an endpoint and save the JSON response."""
    try:
        r = requests.get(f"{BASE}{path}", timeout=30)
        r.raise_for_status()
        data = r.json()
        filepath = os.path.join(OUTPUT_DIR, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        size = len(json.dumps(data, default=str))
        print(f"  ✓  {path} -> {filename} ({size:,} bytes)")
        return data
    except Exception as e:
        print(f"  ✗  {path}: {e}")
        return None

def fetch_and_save_post(path, payload, filename):
    """POST to an endpoint and save the JSON response."""
    try:
        r = requests.post(f"{BASE}{path}", json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        filepath = os.path.join(OUTPUT_DIR, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  ✓  POST {path} -> {filename}")
        return data
    except Exception as e:
        print(f"  ✗  POST {path}: {e}")
        return None

def wait_for_backend():
    """Wait for the backend to be healthy."""
    print("Waiting for backend to be ready...")
    for i in range(120):
        try:
            r = requests.get(f"{BASE}/health", timeout=5)
            if r.status_code == 200:
                print("Backend is ready!\n")
                return True
        except:
            pass
        time.sleep(2)
        if i % 10 == 0 and i > 0:
            print(f"  Still waiting... ({i * 2}s)")
    print("ERROR: Backend did not become ready after 4 minutes")
    return False

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not wait_for_backend():
        sys.exit(1)

    print("=" * 60)
    print("Generating static API snapshot")
    print("=" * 60)

    # ── Health ──
    print("\n[1/8] Health")
    fetch_and_save("/health", "health.json")

    # ── State endpoints ──
    print("\n[2/8] State")
    scores = fetch_and_save("/api/state/scores", "state/scores.json")
    fetch_and_save("/api/state/margins", "state/margins.json")
    fetch_and_save("/api/state/alerts", "state/alerts.json")

    # Per-country scores
    for country in ["FI", "EE", "LV", "LT"]:
        fetch_and_save(f"/api/state/scores/{country}", f"state/scores_{country}.json")

    # ── Topology ──
    print("\n[3/8] Topology")
    fetch_and_save("/api/topology/graph", "topology/graph.json")
    fetch_and_save("/api/topology/outages", "topology/outages.json")

    # ── Scenarios ──
    print("\n[4/8] Scenarios")
    prebuilt = fetch_and_save("/api/scenario/prebuilt", "scenario/prebuilt.json")
    if prebuilt:
        scenarios = prebuilt.get("scenarios", prebuilt) if isinstance(prebuilt, dict) else prebuilt
        if isinstance(scenarios, list):
            for scenario in scenarios:
                sid = scenario.get("id", scenario.get("scenario_id", "unknown"))
                # Fetch the scenario definition
                scenario_def = fetch_and_save(
                    f"/api/scenario/prebuilt/{sid}",
                    f"scenario/prebuilt_{sid}.json"
                )
                # Run the scenario via POST and save the result
                if scenario_def:
                    overrides = scenario_def.get("overrides", [])
                    payload = {"scenario_id": sid, "overrides": overrides}
                    fetch_and_save_post(
                        "/api/scenario/run",
                        payload,
                        f"scenario/result_{sid}.json"
                    )

    # ── Forecast ──
    print("\n[5/8] Forecast")
    fetch_and_save("/api/forecast/risk", "forecast/risk.json")
    fetch_and_save("/api/forecast/alerts", "forecast/alerts.json")
    fetch_and_save("/api/forecast/backtest", "forecast/backtest.json")

    # ── Meta ──
    print("\n[6/8] Meta")
    fetch_and_save("/api/meta/assumptions", "meta/assumptions.json")
    fetch_and_save("/api/meta/data-quality", "meta/data-quality.json")
    fetch_and_save("/api/meta/system-status", "meta/system-status.json")

    # ── Provenance (per-country per-domain) ──
    print("\n[7/8] Provenance")
    domains = [
        "energy_dependence", "infrastructure_vulnerability", "supply_route_disruption",
        "sanctions_pressure", "geopolitical_tension", "alliance_alignment",
        "comms_logistics_stress", "strategic_readiness", "escalation_risk"
    ]
    for country in ["FI", "EE", "LV", "LT"]:
        for domain in domains:
            fetch_and_save(
                f"/api/meta/provenance/{domain}/{country}",
                f"meta/provenance_{domain}_{country}.json"
            )

    # ── Summary ──
    print("\n[8/8] Summary")
    total_files = 0
    total_bytes = 0
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for f in files:
            total_files += 1
            total_bytes += os.path.getsize(os.path.join(root, f))

    print(f"\n{'=' * 60}")
    print(f"Static API snapshot complete!")
    print(f"  Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print(f"  Total files: {total_files}")
    print(f"  Total size: {total_bytes / 1024:.1f} KB")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
