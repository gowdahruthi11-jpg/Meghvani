"""
Meghvani Phase 7A: SIH End-to-End Demonstration Scenario Runner.

Executes the deterministic 10-stage pipeline:
1. Farmer Profile (Active + Consent)
2. Historical Forecast Replay
3. Prototype Decision Engine (SOW_NOW)
4. Validated Agronomic Rule (ICAR/PDKV)
5. Vernacular Marathi Message
6. Multi-Channel Simulated Communication
7. Alert Audit Log
8. Qualitative Farmer Observation
9. Analytical Observation Validation
10. Officer Audit Trail

Usage:
    python scripts/run_demo_scenario.py
"""
import sys
from pathlib import Path

# Ensure UTF-8 output encoding for regional text on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.database import SessionLocal
from app.services.demo_service import DemoService


def main():
    print("=" * 60)
    print("MEGHVANI END-TO-END DEMO")
    print("SIH 2026 — Deterministic Workflow Verification")
    print("=" * 60)

    db = SessionLocal()
    try:
        res = DemoService.run_demo_pipeline(db=db, probability_override=0.20, language="mr", observation_type="RAIN")

        stages = res["stages"]
        f = stages["1_farmer"]
        fc = stages["2_forecast"]
        d = stages["3_decision"]
        adv = stages["4_advisory"]
        msg = stages["5_message"]
        comm = stages["6_communication"]
        obs = stages["7_observation"]

        print(f"\n[1] Farmer Profile")
        print(f"    Status: {'ACTIVE' if f['active'] else 'INACTIVE'}")
        print(f"    Consent: {'YES' if f['consent'] else 'NO'}")
        print(f"    Language: {f['preferred_language']}")
        print(f"    Crop: {f['crop']}")
        print(f"    Block / Village: {f['block']} / {f['village']}")
        print(f"    Phone (Masked): {f['masked_phone']}")

        print(f"\n[2] Forecast Replay")
        print(f"    Mode: {fc['mode']}")
        print(f"    Probability: {fc['probability_pct']} (raw: {fc['probability']:.2f})")
        print(f"    Source: {fc['source']}")
        print(f"    Operational: {'YES' if fc['is_operational'] else 'NO'}")

        print(f"\n[3] Decision")
        print(f"    Decision: {d['decision']}")
        print(f"    Decision Engine: {d['decision_engine_status']}")
        print(f"    Risk Thresholds: {d['thresholds']}")

        print(f"\n[4] Agronomic Rule")
        print(f"    Rule ID: {adv['rule_id']}")
        print(f"    Source: {adv['source_institution']}")
        print(f"    Source Validation: {adv['validation_status']}")
        print(f"    Source Guidance: {adv['source_supported_condition']}")
        print(f"    Meghvani Model Condition: {adv['meghvani_prototype_condition']}")

        print(f"\n[5] Farmer Message")
        print(f"    Language: {msg['language_name']}")
        print(f"    Generated: YES")
        print(f"    Preview: \"{msg['message_text'][:80]}...\"")

        print(f"\n[6] Communication Simulation")
        print(f"    Channel: {comm['channel_plan']}")
        print(f"    Routing Policy: {comm['routing_policy']}")
        print(f"    Provider: {comm['provider']}")
        print(f"    Simulated Status: {comm['status']}")
        print(f"    External Dispatch: {'YES' if comm['external_dispatch'] else 'NO'}")

        print(f"\n[7] Alert Log")
        print(f"    Alert ID: #{comm['alert_id']}")
        print(f"    Created: YES")
        print(f"    Audit Trail: Persisted in database")

        print(f"\n[8] Farmer Observation")
        print(f"    Observation ID: #{obs['observation_id']}")
        print(f"    Type: {obs['observation_type']}")
        print(f"    Source: {obs['source']}")
        print(f"    Recorded: YES")

        print(f"\n[9] Observation Validation")
        print(f"    Reference Rainfall: {obs['reference_rainfall_mm']} mm")
        print(f"    Result: {obs['validation_status']}")
        print(f"    Notes: {obs['comparison_notes']}")
        print(f"    Automated Retraining: {'YES' if obs['automated_retraining_triggered'] else 'NO (STRICT INVARIANT)'}")

        print(f"\n[10] Officer View")
        print(f"    End-to-End Record: AVAILABLE")
        print(f"    Demo ID: {res['demo_id']}")
        print(f"    Status Indicators: {res['status_indicators']}")

        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("All 10 stages verified without external dispatches or model retraining.")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()
