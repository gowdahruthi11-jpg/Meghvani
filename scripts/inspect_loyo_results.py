import json
from pathlib import Path

path = Path("docs/phase_7b_validation_run_output.json")
with open(path, "r", encoding="utf-8") as f:
    d = json.load(f)

print("=== MULTI-YEAR AGGREGATE HORIZONS ===")
for h in ["7d", "14d", "21d", "30d"]:
    h_data = d["horizons"].get(h, {})
    agg = h_data.get("aggregate_metrics", {})
    print(f"Horizon {h:4s}: Brier={agg.get('pooled_brier_score')} | BSS={agg.get('pooled_brier_skill_score')} | ROC_AUC={agg.get('pooled_roc_auc')} | PR_AUC={agg.get('pooled_pr_auc')} | Pos={agg.get('total_positive_events')}/{agg.get('total_evaluation_samples')}")

print("\n=== YEAR-WISE BREAKDOWN (7-Day Horizon) ===")
print(f"{'Year':<6} | {'Samples':<8} | {'Pos':<5} | {'Neg':<6} | {'Brier':<8} | {'BSS':<8} | {'ROC_AUC':<8} | {'PR_AUC':<8} | {'Status':<10}")
print("-" * 85)
for yr in d["horizons"]["7d"]["year_wise_results"]:
    print(f"{yr['evaluation_year']:<6} | {yr['evaluation_rows']:<8} | {yr['positive_events']:<5} | {yr['negative_events']:<6} | {yr['brier_score']:<8} | {yr['brier_skill_score']:<8} | {yr['roc_auc']:<8} | {yr['pr_auc']:<8} | {yr['status']:<10}")

print("\n=== BLOCK BREAKDOWN (7-Day Horizon) ===")
print(f"{'Block':<8} | {'Samples':<8} | {'Pos':<5} | {'Brier':<8} | {'BSS':<8} | {'ROC_AUC':<8} | {'PR_AUC':<8} | {'Status':<10}")
print("-" * 75)
for blk, b_data in d["blocks"].items():
    print(f"{blk:<8} | {b_data.get('total_samples', 0):<8} | {b_data.get('positive_events', 0):<5} | {b_data.get('brier_score'):<8} | {b_data.get('brier_skill_score'):<8} | {b_data.get('roc_auc'):<8} | {b_data.get('pr_auc'):<8} | {b_data.get('status'):<10}")

print("\n=== CONTINGENCY & RELIABILITY (7-Day Aggregate) ===")
agg_7d = d["horizons"]["7d"]["aggregate_metrics"]
print("Pooled Contingency at prototype threshold 0.35:", agg_7d.get("pooled_contingency"))
