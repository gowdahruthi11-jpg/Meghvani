# Meghvani Phase 7A: Existing Architecture & Integration Mapping

> **CRITICAL BOUNDARY NOTICE**:  
> **Phase 7A is an integration verification and demonstration phase.**  
> It does not alter existing ML models, does not modify probability calibration, does not claim operational skill, does not activate production dispatches, and connects only deterministic, mock-simulated pipelines (`is_operational = false`, `external_dispatch = false`).

---

## 1. System Inventory

Meghvani is an integrated hyperlocal monsoon onset/break prediction and farmer decision-support system built across Phases 1 through 6B.

### A. FastAPI Backend Architecture
- **Framework**: FastAPI with Pydantic v2 schemas and SQLAlchemy 2.0 ORM.
- **Database**: SQLite database (`meghvani.db`) with automated schema migrations (`run_migrations`) and Alembic version tracking.
- **Configuration**:
  - `config/event_thresholds.yaml`: Configured prototype event benchmarks (onset, false onset, break spells, heavy rain, dry spell).
  - `config/agronomic_rules.yaml`: 11 agronomic rules (6 VALIDATED, 2 REVIEW_REQUIRED, 3 UNVALIDATED).
  - `config/agronomic_sources.yaml`: Institutional provenance metadata (ICAR-CRIDA, Dr. PDKV Akola).

### B. Database Entity Models (`backend/app/models/`)
1. [`Block`](file:///backend/app/models/block.py): Hyperlocal block definitions in Vidarbha (Nagpur Rural, Wardha East, Amravati Central).
2. [`Village`](file:///backend/app/models/village.py): Village mapping with PIN codes and geo-coordinates (Kalmeshwar, Mohpa, Seloo).
3. [`Crop`](file:///backend/app/models/crop.py): Major Kharif crops (Soybean, Cotton, Pigeonpea, Maize, etc.).
4. [`Farmer`](file:///backend/app/models/farmer.py): Farmer profile with consent gate, preferred language, PIN, village, and communication preferences.
5. [`WeatherObservation`](file:///backend/app/models/weather.py): Daily block-scale rainfall and meteorological readings.
6. [`FarmerObservation`](file:///backend/app/models/farmer_observation.py): Crowd ground-truth observations (`RAIN`, `DRY`, `HEAVY_RAIN`) with validation metadata.
7. [`AlertLog`](file:///backend/app/models/alert_log.py): Comprehensive audit trail of simulated dispatches, channel plans, and fallback occurrences.

### C. Existing API Endpoints (`backend/app/api/`)
- `/api/health`: System health and subsystem status.
- `/api/blocks`, `/api/villages`, `/api/crops`, `/api/farmers`: Master data and profile management.
- `/api/registration`: Conversational state machine registration via simulated missed-call / SMS.
- `/api/weather`: Current and historical block weather observations.
- `/api/historical`: Historical event timeline and monsoon diagnostics (Phases 2 & 2.1).
- `/api/prediction`: Supervised prediction dataset metrics and distributions (Phase 3A).
- `/api/forecast`: Probabilistic baseline inference and raw prototype probabilities (Phases 3B, 3B.1, 4A).
- `/api/advisory`: Prototype decision evaluation and rule matching with source traceability (Phases 4B, 5A, 5B, 5C).
- `/api/alerts`: Alert preview, multi-channel simulation, and officer audit trail (Phase 6A).
- `/api/observations`: Farmer observation ingestion, validation against reference rainfall, and research summaries (Phase 6B).

### D. Core Scientific & Algorithmic Modules
- **Historical Pipeline** (`backend/app/historical/`): Event detection rules, lockout debouncing, rainfall ceilings.
- **Predictive ML Baseline** (`backend/app/ml/`): `LogisticRegressionBaseline` trained on rolling 3d/5d/7d/14d/30d antecedent rainfall features, evaluating probability of false onset ($P(\text{False Onset } 7\text{d})$).
- **Probability Calibration Framework** (`backend/app/ml/calibration.py`): Explicit status `INSUFFICIENT_CALIBRATION_DATA` acknowledging demo dataset constraints (single calendar year, 6 positives).
- **Prototype Decision Engine** (`backend/app/ml/decision_engine.py`): Evaluates risk thresholds (`SOW_NOW` for $p < 0.30$, `SOW_PART_NOW` for $0.30 \le p < 0.60$, `WAIT` for $p \ge 0.60$).
- **Advisory Rule Engine & Provenance** (`backend/app/advisory/`): Strict separation between institutional source requirements (e.g. 75–100 mm sowing moisture) and Meghvani prototype decision thresholds. Strictly enforces **NO VALIDATED RULE = NO ADVICE**.
- **Vernacular Message Layer** (`backend/app/advisory/message_generator.py`): Formats actionable advisories into Marathi (`mr`), Hindi (`hi`), and English (`en`) for SMS, WhatsApp, and Voice.
- **Communication Simulation Layer** (`backend/app/communication/`): Multi-channel routing (`INFO` $\to$ SMS, `IMPORTANT` $\to$ SMS + WhatsApp, `HIGH` $\to$ Voice + SMS), automatic Voice/WhatsApp $\to$ SMS fallback, 24h duplicate suppression, and privacy masking.
- **Farmer Observation & Validation Subsystem** (`backend/app/observations/`): Validates qualitative crowd reports against reference weather observations, reporting non-pejorative agreement metrics while strictly guaranteeing **no automatic model retraining**.

### E. Frontend Application (`frontend/src/`)
- Modern React/TypeScript application with TailwindCSS and Lucide icons.
- Pages: Overview, Historical Analysis, Prediction Dataset, Baseline Model, Farmer Registration, Alert Center, Observations & Feedback, Officer Dashboard, System Status.

---

## 2. Modules Connected in Phase 7A Demonstration

Phase 7A unifies these existing modular subsystems into a single, cohesive, deterministic end-to-end demonstration pipeline for SIH evaluation:

```text
[1] FARMER PROFILE
    Existing Model: Farmer (Active=True, Consent=True, Lang=Marathi, Crop=Soybean, Block=Nagpur Rural)
         ↓
[2] FORECAST REPLAY
    Deterministic Non-Operational Replay (source="DEMO_REPLAY", mode="HISTORICAL_REPLAY", prob=0.20)
         ↓
[3] PROTOTYPE DECISION
    Existing Engine: PrototypeDecisionEngine (evaluates prob=0.20 -> Decision: SOW_NOW)
         ↓
[4] VALIDATED AGRONOMIC RULE
    Existing Engine: AdvisoryRuleEngine (matches validated PDKV/ICAR Soybean sowing rule)
         ↓
[5] MARATHI ADVISORY MESSAGE
    Existing Generator: AdvisoryMessageGenerator (generates vernacular Marathi farmer advisory)
         ↓
[6] SIMULATED ALERT ROUTING
    Existing Service: AlertRouter (routes SOW_NOW as INFO -> Mock SMS channel, external_dispatch=False)
         ↓
[7] ALERT AUDIT LOG
    Existing Model: AlertLog (persists dispatch record with masked phone, status=SIMULATED_SENT)
         ↓
[8] FARMER OBSERVATION
    Existing API: POST /api/observations (farmer reports RAIN, source=FARMER)
         ↓
[9] OBSERVATION VALIDATION
    Existing Service: ObservationValidator (compares observation with reference rainfall -> AGREEMENT)
         ↓
[10] OFFICER AUDIT TRAIL
    Existing Dashboard: Officer view displays complete unbroken end-to-end chain
```

---

## 3. Explicit Boundaries & Safeguards

1. **Deterministic Demo Replay**: Forecast inputs carry `source = "DEMO_REPLAY"`, `mode = "HISTORICAL_REPLAY"`, and `scientific_status = "NON_OPERATIONAL_DEMO"`. Production ML model files are completely isolated.
2. **Zero External Dispatches**: Mock communication providers always return `external_dispatch: false`. No telecom or WhatsApp APIs are invoked.
3. **No Retraining Pipeline**: Farmer observations terminate in analytical audit logs; they never alter model weights or calibration tables.
4. **Complete Traceability**: Every advisory message explicitly preserves institutional source citations alongside Meghvani prototype decision thresholds.
