# Meghvani Phase 8B: Changelog & Scientific Audit Report

**Date:** October 3, 2026  
**Status:** Completed & Validated  
**Test Suite:** 341/341 Passed (Backend) • Production Bundle Built Cleanly (Frontend `npm run build`)

---

## 1. Executive Summary

Phase 8B executes critical scientific governance, rigorous in-season model evaluation, economic loss-based decision calibration, and engineering hygiene for **Meghvani**—a monsoon false-onset prediction and agronomic decision-support system for smallholder farmers in Vidarbha, Maharashtra.

All six non-negotiable invariants were strictly maintained:
1. **Zero Future Leakage:** Features at $T$ use only $t \le T$; targets look strictly into $(T, T+h]$.
2. **No Validated Rule = No Advice:** Agronomic recommendations are deterministically mapped to verified ICAR/PDKV scientific rules.
3. **Observation Quarantine:** Farmer ground observations never enter model training or retraining.
4. **Isolated Telecommunications:** `is_operational = false` and external telecom dispatch remains disabled (all communication routes through mock simulators).
5. **No Fabricated Skill:** Honest statistical reporting; undefined metrics return `None` with reason codes.
6. **Raw Data Immutability:** `data/raw/**` remained untouched. All 321 prior tests plus 20 new tests pass (341 total).

---

## 2. Detailed Task Breakdown

### Task 1: Single Source of Truth for Thresholds & Blocks
- **Created [config/event_definitions.yaml](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/config/event_definitions.yaml)**: Canonical definitions for:
  - Monsoon Onset: $20.0\text{ mm}$ cumulative over 3 consecutive days with 30-day lockout debounce.
  - False Onset: Lookahead window of 30 days containing $\ge 7$ consecutive dry days ($<2.5\text{ mm/day}$).
  - Dry Spell: $\ge 7$ consecutive days with $<2.5\text{ mm/day}$.
  - Heavy Rainfall: $\ge 64.5\text{ mm/day}$ (official IMD threshold).
  - In-Season Evaluation Window: May 25 to July 31.
- **Created [config/blocks.yaml](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/config/blocks.yaml)**: Canonical block registry:
  - `BLK001: Nagpur Rural (Nagpur)`
  - `BLK002: Wardha East (Wardha)`
  - `BLK003: Amravati Central (Amravati)`
- **Configuration & Ingestion Wiring**: Updated [backend/app/config.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/config.py), [backend/app/historical/event_detector.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/historical/event_detector.py), [backend/app/database/seed.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/database/seed.py), [backend/app/historical/spatial_mapping.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/historical/spatial_mapping.py), and [frontend/src/components/Footer.tsx](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/frontend/src/components/Footer.tsx).
- **Verification**: [tests/test_canonical_definitions.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/tests/test_canonical_definitions.py) (4 tests).

---

### Task 2: In-Season Evaluation (May 25 – July 31)
- **Module**: [backend/app/ml/in_season_evaluation.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/ml/in_season_evaluation.py) and runner [scripts/run_phase_8b_in_season.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/scripts/run_phase_8b_in_season.py).
- **Effective Sample Size Calculation**:
  - Spatial cross-correlation between blocks: $r = 0.6226$.
  - Temporal lag-1 autocorrelation: $\rho_1 = 0.2855$.
  - Nominal sample size: $N = 1224$ (3 blocks $\times$ 68 days $\times$ 6 years).
  - Effective sample size:
    $$N_{\text{eff}} = N \cdot \left(\frac{1 - \rho_1}{1 + \rho_1}\right) \cdot \left(\frac{1}{1 + (K - 1)r}\right) = 1224 \cdot 0.5558 \cdot 0.4454 \approx 303$$
- **Baselines Implemented**:
  1. *DayOfYearClimatologyBaseline*: Historical probability of false onset within $\pm 5$ days of target day-of-year across training years.
  2. *PersistenceBaseline*: Conditioned on ongoing dry-spell streak at prediction date $T$.
- **Empirical Findings (Honest Science)**:
  - Model In-Season Brier Score: `0.1271` (95% CI: `[0.0824, 0.1812]`).
  - Climatology Baseline Brier Score: `0.0096`.
  - Persistence Baseline Brier Score: `0.0096`.
  - Brier Skill Score ($BSS$): `-12.2250` (95% CI: `[-17.8540, -7.5732]`).
  - **Conclusion**: The prototype classifier does not demonstrate positive skill over climatology in the restricted 25 May–31 July sowing window, due to extreme in-season class imbalance (1.14% positive rate). Quarantined as a non-operational research demonstration.
- **Artifacts**: [docs/phase_8b_in_season_report.md](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/docs/phase_8b_in_season_report.md), [data/processed/historical/phase_8b_metrics.json](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/data/processed/historical/phase_8b_metrics.json).
- **Verification**: [tests/test_phase_8b_in_season.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/tests/test_phase_8b_in_season.py) (5 tests).

---

### Task 3: Label Sensitivity Analysis
- **Module**: [backend/app/ml/label_sensitivity.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/ml/label_sensitivity.py) and runner [scripts/run_phase_8b_label_sensitivity.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/scripts/run_phase_8b_label_sensitivity.py).
- **Swept Parameter Grid (27 Combinations)**:
  - Onset thresholds: `15.0 mm`, `20.0 mm`, `25.0 mm`
  - Dry spell durations: `5 days`, `7 days`, `10 days`
  - Lookahead windows: `14 days`, `21 days`, `30 days`
- **Key Findings**:
  - Dry spell threshold is the primary driver of label frequency: 5-day dry spells produce 8–18 false onsets per year, 7-day produces 2–6 events, and 10-day produces 0–2 events.
  - Onset threshold (15 vs 25 mm) primarily shifts the detected onset date earlier or later by 2–5 days without substantially altering overall label count.
- **Artifact**: [docs/phase_8b_label_sensitivity.md](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/docs/phase_8b_label_sensitivity.md).
- **Verification**: [tests/test_phase_8b_label_sensitivity.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/tests/test_phase_8b_label_sensitivity.py) (1 test).

---

### Task 4: Loss-Based Decision Thresholds
- **Configuration**: [config/decision_costs.yaml](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/config/decision_costs.yaml) with documented crop economics for Vidarbha rainfed agriculture (Sources: PDKV Akola, ICAR-CICR, CACP):
  - Soybean: Reseeding cost ₹4,800/ha; Delay cost ₹800/ha $\implies P^* = 0.167$, Buffer band: $[0.133, 0.200]$.
  - Cotton: Reseeding cost ₹6,500/ha; Delay cost ₹1,200/ha $\implies P^* = 0.185$, Buffer band: $[0.148, 0.222]$.
  - Pigeonpea (Tur): Reseeding cost ₹3,800/ha; Delay cost ₹650/ha $\implies P^* = 0.171$, Buffer band: $[0.137, 0.205]$.
  - Generic: Reseeding cost ₹5,000/ha; Delay cost ₹1,000/ha $\implies P^* = 0.200$, Buffer band: $[0.160, 0.240]$.
- **Engine Extension**: [backend/app/ml/decision_engine.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/ml/decision_engine.py):
  - Added `get_loss_based_thresholds(crop_id)`.
  - Added `sweep_cost_ratios(...)` and `run_retrospective_decision_analysis(...)`.
  - Preserved backward compatibility for default static thresholds.
- **Fixture Labeling**: [backend/app/services/demo_service.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/services/demo_service.py) explicitly tagged with `is_fixture: true` and `fixture_type: "STATIC_DEMO_REPLAY"`.
- **Verification**: [tests/test_phase_8b_decision_thresholds.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/tests/test_phase_8b_decision_thresholds.py) (6 tests).

---

### Task 5: Engineering Hygiene & Governance
- **Python 3.12 Pinning**:
  - Updated [backend/Dockerfile](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/Dockerfile) to `FROM python:3.12-slim`.
  - Created root [.python-version](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/.python-version) pinning `3.12.8`.
  - Created root multi-stage [Dockerfile](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/Dockerfile) building frontend and running backend on Python 3.12.
  - Verified [docker-compose.yml](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/docker-compose.yml).
- **Continuous Integration**:
  - Created [.github/workflows/ci.yml](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/.github/workflows/ci.yml) testing Python 3.12 backend, Alembic migrations, pytest suite, and Node 20 frontend `npm run build`.
- **Database Schema Migration**:
  - Created Alembic migration [backend/alembic/versions/003_phase8b_alert_logs_provenance.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/alembic/versions/003_phase8b_alert_logs_provenance.py).
  - Updated [backend/app/models/alert_log.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/models/alert_log.py) and [backend/app/database/migrations.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/database/migrations.py) with:
    - `model_version` (VARCHAR 50)
    - `rule_id` (VARCHAR 100)
    - `rule_version` (VARCHAR 50)
    - `threshold_config_hash` (VARCHAR 64)
- **Officer Administrative Security (`X-API-Key`)**:
  - Created [backend/app/auth.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/backend/app/auth.py) implementing `verify_officer_api_key`.
  - Added `/api/alerts/dispatch` endpoint protected by `verify_officer_api_key`.
  - Protected administrative endpoints (`/api/alerts/simulate`, `/api/alerts/history`, `/api/demo/*`).
- **Verification**: [tests/test_phase_8b_engineering_hygiene.py](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/tests/test_phase_8b_engineering_hygiene.py) (4 tests).

---

### Task 6: Frontend Polish & Accessibility
- **Dynamic Blocks API**: Queried dynamically from `GET /api/blocks` (eliminating hardcoded blocks in UI components).
- **Officer Dashboard Upgrades** ([frontend/src/pages/OfficerDashboard.tsx](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/frontend/src/pages/OfficerDashboard.tsx)):
  - Hero Decision Card: Displays loss-based rationale ($P^* \approx 0.17$), `SOW_NOW` / `WAIT` / `SOW_PART_NOW`, and prominent Non-Operational / DEMO_REPLAY badges.
  - False-Onset Risk Widget: Probability with 95% bootstrap confidence interval or honest "Not enough data" badge with reason codes.
  - 4 Status Cards: (1) Sowing Window Monitoring, (2) Model Calibration Skill ($BSS = -12.22$), (3) Provenance & ICAR/PDKV Rules, (4) Isolated Telecom Gateway.
  - 21-Day Rainfall Bar Chart ([frontend/src/components/RecentRainfallChart.tsx](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/frontend/src/components/RecentRainfallChart.tsx)): 21 daily observations with highlighted dry spell days ($<2.5\text{ mm/day}$) and dry-streak tracking.
- **Farmer Communication Preview Panel** ([frontend/src/components/FarmerMessageCard.tsx](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/frontend/src/components/FarmerMessageCard.tsx)):
  - Multilingual tabs: Marathi (मराठी), Hindi (हिंदी), and English.
  - Web Speech API integration: Regional voice readout (`mr-IN`, `hi-IN`, `en-IN`) with active audio state.
  - Mobile Accessibility: Touch targets expanded to $\ge 44\text{px}$ (`min-h-[44px]`).
- **API Client Security**: Updated [frontend/src/services/api.ts](file:///c:/Users/Acer/Desktop/MEGHVANI_Hrit/meghvani/frontend/src/services/api.ts) with `X-API-Key` header and `dispatchAlert` caller.
- **Build Verification**: `npm run build` executed successfully (`tsc && vite build` built in 16s with 0 errors).

---

## 3. Test Pass Count Summary

| Test Module | Tests | Status |
|:---|:---:|:---:|
| `test_advisory_engine.py` | 20 | PASS |
| `test_baseline_model.py` | 24 | PASS |
| `test_canonical_definitions.py` (New Phase 8B) | 4 | PASS |
| `test_communication_and_alerts.py` | 5 | PASS |
| `test_communication_simulation.py` | 23 | PASS |
| `test_crops.py` | 1 | PASS |
| `test_database.py` | 1 | PASS |
| `test_decision_engine.py` | 20 | PASS |
| `test_end_to_end_demo.py` | 17 | PASS |
| `test_farmer_advisory.py` | 19 | PASS |
| `test_farmer_observation_loop.py` | 25 | PASS |
| `test_farmers.py` | 5 | PASS |
| `test_historical_pipeline.py` | 29 | PASS |
| `test_location.py` | 5 | PASS |
| `test_observations.py` | 3 | PASS |
| `test_phase_7b_no_leakage.py` | 4 | PASS |
| `test_phase_7b_validation.py` | 20 | PASS |
| `test_phase_7c_imd_integration.py` | 15 | PASS |
| `test_phase_8a_calibration.py` | 16 | PASS |
| `test_phase_8a_rolling_origin.py` | 9 | PASS |
| `test_phase_8b_decision_thresholds.py` (New Phase 8B) | 6 | PASS |
| `test_phase_8b_engineering_hygiene.py` (New Phase 8B) | 4 | PASS |
| `test_phase_8b_in_season.py` (New Phase 8B) | 5 | PASS |
| `test_phase_8b_label_sensitivity.py` (New Phase 8B) | 1 | PASS |
| `test_prediction_pipeline.py` | 19 | PASS |
| `test_probability_calibration.py` | 15 | PASS |
| `test_registration.py` | 2 | PASS |
| `test_source_register.py` | 21 | PASS |
| `test_weather.py` | 3 | PASS |
| **Total Backend Tests** | **341** | **ALL PASS** |
| **Frontend Production Build** | **1** | **PASS (`npm run build`)** |

---

## 4. Open Research Questions & Next Steps

1. **In-Season Classifier Architecture**: Since standard logistic regression on ERA5-derived tabular features does not outperform constant climatology ($BSS = -12.22$) during 25 May–31 July, research into subseasonal dynamical NWP indices (MJO phase, monsoon trough latitude, soil moisture anomalies) will be needed for genuine predictive skill.
2. **PostgreSQL / PostGIS Migration**: When scaling beyond local SQLite to operational regional deployments, execute Alembic migrations on managed PostGIS instances as architected in `docker-compose.yml`.
3. **Field Validation Trial**: Validate vernacular SMS/IVR phrasing with smallholder farmer focus groups in Wardha and Amravati to test comprehension and actionable trust.
