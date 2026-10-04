"""
Meghvani Phase 7B: Multi-Year Scientific Validation Runner.

Executes scientific validation across historical monsoon years.
If multi-year data are unavailable (< 2 complete years), executes safely
and outputs BLOCKED_PENDING_MULTIYEAR_DATA.
"""
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.ml.multiyear_validation import MultiYearScientificValidator
from app.historical.multiyear_ingestion import STATUS_BLOCKED, STATUS_READY


def main():
    print("=" * 60)
    print("MEGHVANI PHASE 7B: MULTI-YEAR SCIENTIFIC VALIDATION")
    print("=" * 60)

    validator = MultiYearScientificValidator()
    summary = validator.generate_full_validation_summary()

    cov = summary["data_coverage"]
    status = summary["validation_status"]

    print("\nDATA COVERAGE AUDIT")
    print("-" * 40)
    print(f"Historical Years Available : {cov['historical_years']}")
    print(f"Complete Monsoon Years     : {cov['complete_years']}")
    print(f"Incomplete Years           : {cov['incomplete_years']}")
    print(f"Available Years List       : {cov['available_years_list']}")
    print(f"Monitored Blocks           : {cov['blocks_count']} ({', '.join(cov['block_ids'])})")
    print(f"Total Observations         : {cov['total_observations']}")
    print(f"Missing Dates Count        : {cov['missing_dates_count']}")
    print(f"Duplicate Records Count    : {cov['duplicate_records_count']}")
    print(f"Date Continuity Check      : {'PASS (Continuous)' if cov['date_continuity'] else 'FAIL (Gaps)'}")

    print("\nVALIDATION STATUS")
    print("-" * 40)
    print(f"STATUS                     : {status}")
    print(f"STATEMENT                  : {summary['statement']}")

    if summary.get("provenance"):
        prov = summary["provenance"]
        print("\nPROVENANCE RECORD")
        print("-" * 40)
        print(f"Dataset Name               : {prov['dataset_name']}")
        print(f"Provider                   : {prov['provider']}")
        print(f"Source Reference           : {prov['source_url_or_reference']}")
        print(f"Coverage Range             : {prov['coverage_start']} to {prov['coverage_end']}")
        print(f"Verification Status        : {prov['verification_status']}")
        if prov.get("checksum_sha256"):
            print(f"SHA-256 Checksum           : {prov['checksum_sha256']}")

    print("\nTARGET HORIZONS SUMMARY")
    print("-" * 40)
    for h, res in summary.get("horizons", {}).items():
        h_status = res.get("validation_status", res.get("status", "N/A"))
        print(f"Horizon {h.upper():<5} : Status = {h_status}")

    print("\nBLOCK-LEVEL STATUS")
    print("-" * 40)
    for b_id, b_res in summary.get("blocks", {}).items():
        print(f"Block {b_id:<8} : Status = {b_res.get('status', 'N/A')} (Samples: {b_res.get('total_samples', 0)}, Events: {b_res.get('positive_events', 0)})")

    print("\nLEAVE-ONE-YEAR-OUT (LOYO) EVALUATION")
    print("-" * 40)
    loyo = summary.get("loyo_7d", {})
    for yr_res in loyo.get("year_wise_results", []):
        print(f"Year {yr_res.get('evaluation_year')} : Status = {yr_res.get('status')} | Eval Rows = {yr_res.get('evaluation_rows')} | Pos Events = {yr_res.get('positive_events')} | Brier = {yr_res.get('brier_score')} | BSS = {yr_res.get('brier_skill_score')}")

    print("\n" + "=" * 60)
    if status == STATUS_BLOCKED:
        print("RESULT: BLOCKED_PENDING_MULTIYEAR_DATA")
        print("Phase 7B infrastructure is complete, but scientific")
        print("multi-year validation is blocked pending verified")
        print("multi-year historical data.")
    else:
        print(f"RESULT: {status}")
    print("=" * 60)

    # Save summary report artifact
    report_path = PROJECT_ROOT / "docs" / "phase_7b_validation_run_output.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved machine-readable run output to: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
