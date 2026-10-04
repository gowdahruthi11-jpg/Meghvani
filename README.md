# Meghvani — Hyperlocal Monsoon Onset & Break Prediction System
### Block & Village Scale Agrometeorological Intelligence (Smart India Hackathon 2026 Prototype)

---

## 1. Project Overview & Problem Statement
Indian smallholder agriculture is deeply vulnerable to monsoonal uncertainties. Traditional synoptic-scale district forecasts fail to capture hyperlocal rain onset, false-onset dry spells, sudden mid-season breaks, and intense convective heavy-rain events. Sowing during a false onset leads to re-sowing costs, seed-loss, and debt traps.

**Meghvani** is engineered to predict hyperlocal monsoon onset, false onset, break/dry-spell, revival, and heavy-rain hazards at **block scale (1–4 weeks)**, convert those probabilities into crop-specific sowing/advisory decisions, and deliver clear, actionable recommendations to farmers through **conversational SMS, automated voice calls, or WhatsApp** in their regional language.

---

> [!WARNING]
> ### Phase 1 Production-Ready Foundation Transparency Disclaimers
> - **Phase 1 does not provide real rainfall forecasting.**
> - **Phase 1 does not send real SMS, WhatsApp messages or voice calls.**
> - **Communication providers are mocked.**
> - **Weather data is demo data.**
> - All demonstration datasets are clearly labelled `DEMO DATA`.

---

## 2. Core Architecture
Meghvani separates all operational concerns into decoupled, modular layers:

```
[Farmer: Mobile SMS / Missed-Call CLI]
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  API Gateway & Routers (FastAPI)                       │
│  - /api/health, /api/blocks, /api/villages, /api/crops │
│  - /api/farmers, /api/registration, /api/observations  │
│  - /api/alerts, /api/weather                           │
└──────────────────────────┬─────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌──────────────────┐┌──────────────────┐┌──────────────────┐
│  Conversational  ││  Severity Alert  ││  Advisory Rule   │
│  State Machine   ││  Routing Engine  ││  Engine          │
│  (SMS & Missed)  ││  (Voice+SMS Fall)││  (ICAR-Ready)    │
└────────┬─────────┘└────────┬─────────┘└────────┬─────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌────────────────────────────────────────────────────────┐
│  Database Layer (SQLAlchemy 2.0 ORM)                   │
│  - Local: SQLite | Production: PostgreSQL / PostGIS    │
│  - Migrations: Alembic | Seeder: Seeded DEMO data      │
└────────────────────────────────────────────────────────┘
```

1. **Primary Prediction Unit**: The administrative **Block** is the primary spatial unit for meteorological modeling.
2. **Local Targeting Unit**: The **Village** is used for farmer localization and PIN-code mapping. Farmers never need to guess their block.
3. **Conversational SMS State Machine**: Farmers onboard simply by texting `MEGH` or giving a missed call.
4. **Severity Alert Dispatch**: Multi-channel routing (SMS, WhatsApp, Voice) with automated retry and fallback to SMS when urgent voice calls are unanswered.
5. **Crowd Ground-Truth**: Farmer observations (`RAIN`, `DRY`, `HEAVY_RAIN`) are stored for validation and calibration research. They **never automatically trigger ML retraining**.
6. **Privacy-Preserving**: No Aadhaar is collected; phone numbers are masked in officer views (`+91****3210`); explicit consent is mandatory.

---

## 3. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PyYAML
- **Database**: SQLite (local development) / PostgreSQL + PostGIS (deployment architecture)
- **Data & Scientific**: pandas, numpy, scipy, scikit-learn, joblib
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons
- **Testing**: pytest, FastAPI TestClient (HTTPX)
- **Containerization**: Docker, Docker Compose

---

## 4. Complete Project Directory Structure
```
meghvani/
├── backend/
│   ├── alembic/                      # Database migration scripts
│   ├── app/
│   │   ├── main.py                   # FastAPI application & lifespan
│   │   ├── config.py                 # YAML loaders and Pydantic Settings
│   │   ├── api/                      # 9 Modular REST routers
│   │   │   ├── health.py
│   │   │   ├── blocks.py
│   │   │   ├── villages.py
│   │   │   ├── crops.py
│   │   │   ├── farmers.py
│   │   │   ├── registration.py
│   │   │   ├── observations.py
│   │   │   ├── alerts.py
│   │   │   └── weather.py
│   │   ├── database/
│   │   │   ├── database.py           # Engine & SessionLocal
│   │   │   ├── base.py               # DeclarativeBase
│   │   │   └── seed.py               # Curated DEMO data seeder
│   │   ├── models/                   # 8 SQLAlchemy ORM entities
│   │   │   ├── block.py
│   │   │   ├── village.py
│   │   │   ├── crop.py
│   │   │   ├── farmer.py
│   │   │   ├── weather.py
│   │   │   ├── registration_session.py
│   │   │   ├── farmer_observation.py
│   │   │   └── alert_log.py
│   │   ├── schemas/                  # Pydantic v2 validation contracts
│   │   │   ├── block.py
│   │   │   ├── village.py
│   │   │   ├── crop.py
│   │   │   ├── farmer.py
│   │   │   ├── weather.py            # Future ML ForecastOutput contract
│   │   │   ├── observation.py
│   │   │   ├── alert.py
│   │   │   └── registration.py
│   │   ├── services/                 # Core business services
│   │   │   ├── location_service.py
│   │   │   ├── farmer_service.py
│   │   │   ├── registration_service.py
│   │   │   ├── weather_service.py
│   │   │   ├── advisory_service.py
│   │   │   └── alert_service.py
│   │   ├── communication/            # Provider abstractions
│   │   │   ├── base.py
│   │   │   ├── sms.py
│   │   │   ├── voice.py
│   │   │   ├── whatsapp.py
│   │   │   └── mock_provider.py
│   │   └── utils/
│   ├── requirements.txt
│   ├── .env.example
│   ├── .env
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/               # Navbar, Footer
│   │   ├── pages/                    # Landing, RegisterSim, OfficerDashboard, Status
│   │   ├── services/                 # Typed API client
│   │   ├── types/                    # TypeScript interfaces
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── config/
│   ├── app.yaml                      # App settings & CORS
│   ├── event_thresholds.yaml         # Onset, false-onset, break, heavy-rain thresholds
│   ├── crops.yaml                    # Demo crops catalog (Kharif)
│   ├── communication.yaml            # Severity routing & voice retry matrix
│   └── advisory_rules.yaml           # Agronomic decision rules (SOW_NOW, WAIT, etc.)
├── data/
│   ├── raw/
│   ├── processed/
│   ├── sample/                       # Sample timeseries rainfall format
│   └── location/                     # Demo block & village metadata
├── ml/
│   ├── models/                       # Model binaries (gitignored)
│   ├── features/                     # Feature engineering modules
│   ├── training/                     # Training pipelines
│   ├── evaluation/                   # Calibration & skill metrics
│   └── README.md                     # Future ML probabilistic contract
├── scripts/
│   └── verify_system.py              # CLI system validation test
├── notebooks/
├── tests/
│   ├── conftest.py                   # Pytest fixtures & in-memory SQLite DB
│   ├── test_database.py
│   ├── test_location.py
│   ├── test_crops.py
│   ├── test_farmers.py
│   ├── test_registration.py
│   ├── test_observations.py
│   ├── test_communication_and_alerts.py
│   └── test_weather.py
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker & Docker Compose

### Backend Setup
```bash
# Navigate to project root
cd meghvani

# Create Python virtual environment
python -m venv backend/venv

# Activate virtual environment
# Windows:
.\backend\venv\Scripts\activate
# Linux/macOS:
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Verify environment file exists
cp backend/.env.example backend/.env

# Run database migrations and seed demo data
python backend/app/database/seed.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run build
```

---

## 6. Running the Application

### 1. Start FastAPI Backend
```bash
cd meghvani
# From root using venv:
.\backend\venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --port 8000
```
- Swagger Interactive Documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### 2. Start React Frontend
```bash
cd meghvani/frontend
npm run dev
```
- Web Application: `http://localhost:5173`

### 3. (Optional) Run with Docker Compose
```bash
cd meghvani
docker-compose up --build
```

---

## 7. Running the Test Suite
The automated test suite runs against an isolated in-memory SQLite database:
```bash
cd meghvani
.\backend\venv\Scripts\python.exe -m pytest tests -v
```
All **25 automated tests** validate database creation, PIN resolution, consent enforcement, conversational state machine transitions, invalid inputs, mock dispatches, voice retry, and SMS fallback.

You can also run the CLI verification script:
```bash
cd meghvani
.\backend\venv\Scripts\python.exe scripts/verify_system.py
```

---

## 8. Detailed Workflows

### Conversational SMS Registration Flow
1. Farmer texts `MEGH` to the gateway.
2. System identifies caller phone number and prompts language selection: `1: Hindi, 2: Marathi, 3: Kannada, 4: English`.
3. Farmer responds with `1` (or regional text).
4. System asks for 6-digit PIN code.
5. System queries location database and lists villages mapped to that PIN.
6. Farmer chooses village number; system automatically maps Village -> Block.
7. System prompts crop selection (e.g. Soybean, Cotton, Maize, etc.).
8. System asks for explicit consent: *"Reply YES to continue"*.
9. Only upon receiving `YES` is the farmer profile activated.
10. System sends confirmation in the selected language.

### Missed-Call Onboarding
1. Farmer dials Meghvani toll-free missed call number.
2. Inbound ring triggers `MockMissedCallProvider.handle_incoming_ring(phone_number)`.
3. Caller number is identified without data costs to the farmer.
4. System automatically launches the conversational onboarding flow via SMS / IVR callback.

### Alert Severity Routing & Voice Fallback
- `NORMAL` Risk: Dispatched via **SMS**.
- `IMPORTANT` Risk: Dispatched via **SMS + WhatsApp**.
- `HIGH_RISK`: Placed via **Automated Voice Call + SMS**.
- **Voice No-Answer Fallback**:
  - Attempt 1: Call placed. If `NO_ANSWER`:
  - Attempt 2: Retry after delay. If still `NO_ANSWER`:
  - System automatically triggers fallback SMS: `[Fallback SMS - Voice Unanswered] <advisory message>`.

---

## 9. Phase 2 & 2.1 Completed: Historical Rainfall Pipeline & Event Detection Engine

Phase 2 builds the deterministic data pipeline and event detection engine that converts raw daily rainfall observations into a validated, ML-ready feature and event-labeled dataset. Phase 2.1 implements critical label quality improvements identified during logic auditing.

### Pipeline Architecture:
```
Raw Rainfall CSV (data/raw/rainfall/demo_rainfall.csv)
       ↓
RainfallDataLoader (app.historical.loader)
       ↓
RainfallValidator (app.historical.validator)
       ↓ (Checks non-empty blocks, ISO dates, non-negative bounds, duplicates, missing dates; preserves non-zero missingness)
RainfallFeatureEngineer (app.historical.features)
       ↓ (Strict backward-looking rolling sums 1d, 3d, 5d, 7d, 14d, 30d; spell metrics; intensity classifications)
EventDetector (app.historical.event_detector)
       ↓ (Primary onset triggers with 30d lockout debounce, lookahead false-onsets, break spells with episode IDs, heavy rain, revivals)
HistoricalDatasetBuilder (app.historical.dataset_builder)
       ↓
Exported Dataset (data/processed/historical_events.csv)
       ↓
FastAPI Inspection APIs & React Historical Analysis UI (/historical)
```

### Key Logic & Label Quality Implementations:
1. **Primary Onset Trigger with Lockout Debounce (`onset_lockout_days: 30`)**:
   - Distinguishes the primary / qualifying seasonal onset trigger from subsequent persistent rainy days.
   - Suppresses additional onset triggers during the lockout period so that consecutive wet days do not repeatedly generate onset labels.
   - Prevents normal mid-season rainfall bursts from being retroactively classified as onsets or false onsets.
2. **Break Days vs. Distinct Break Episodes**:
   - `break_event = 1` remains a row-level flag indicating that a specific calendar date was part of an active break spell.
   - `distinct_break_episodes` tracks each contiguous multi-day break period with deterministic IDs (e.g. `BLK001_BREAK_001`).
   - Summary statistics clearly report both `break_spell_days_count` (e.g. 44 days) and `distinct_break_episodes` (e.g. 5 episodes).

### CLI Pipeline Execution:
```bash
python scripts/build_historical_dataset.py \
    --input data/raw/rainfall/demo_rainfall.csv \
    --output data/processed/historical_events.csv
```

### Historical API Endpoints:
- `GET /api/historical/summary`: Statistical overview of records, blocks, primary onsets, false onsets, break days, and distinct break episodes.
- `GET /api/historical/events`: Filter events by block, event type (onset, false_onset, break, heavy_rain, revival), and date range.
- `GET /api/historical/{block_id}`: Chronological rainfall series with rolling features and event flags.
- `POST /api/historical/process`: Safely triggers local demo dataset ingestion and feature generation.

### Scientific & Regulatory Boundaries:
> [!IMPORTANT]
> **Prototype Event Definitions — Not Official Meteorological Standards**
> Phase 2 uses demo rainfall data and prototype event thresholds (`config/event_thresholds.yaml`). It does NOT provide operational weather forecasts and does NOT claim official IMD onset/break definitions.
> - **Prototype primary onset trigger**: Heuristic 3-day cumulative rainfall threshold ($\ge 20\text{ mm}$) with a 30-day lockout window used for engineering and historical event detection.
> - **Prototype false-onset detector**: Heuristic lookahead identifying qualifying dry spells ($\ge 7\text{ days}$) within 30 days of an apparent onset trigger.
> - **Prototype break detector**: Heuristic consecutive dry streak ($\ge 5\text{ days}$) with rainfall below $2.5\text{ mm}$, assigned unique episode IDs.
> - **Prototype heavy-rain detector**: Benchmark alert threshold ($\ge 64.5\text{ mm/day}$).
> - **Prototype revival detector**: Rainfall resumption ($\ge 15\text{ mm}$ over 2 days) terminating a break spell.
> 
> Predictor features (`rainfall_1d` through `30d`, `dry_spell_days`) are strictly backward-looking to eliminate future data leakage in downstream ML training.

---

---

## 10. Phase 3A: Predictive Feature & Target Engineering (COMPLETE)

Phase 3A converts the processed historical event dataset (`data/processed/historical_events.csv`) into a supervised-learning-ready prediction dataset (`data/processed/prediction_dataset.csv`) without training any ML models.

### Architecture Flow:
```
Historical labeled events (data/processed/historical_events.csv)
        ↓
Prediction cutoffs (prediction_date T)
        ↓
Strictly backward-looking predictors (observed on or before T)
        ↓
Forward-looking event targets (observed strictly in window [T + 1, T + horizon])
        ↓
Prediction dataset (data/processed/prediction_dataset.csv)
        ↓
Chronological / Temporal split validation (app.prediction.splits)
        ↓
(Baseline model training in Phase 3B)
```

### 1. Critical Data Leakage Rule:
- For prediction date $T$:
  - **Predictive Features** may ONLY use information available on or before $T$ ($\text{date} \le T$).
  - **Supervised Targets** evaluate observations occurring strictly AFTER $T$ ($\text{date} > T$).
  - Prediction date $T$ is NEVER included in the future target window (e.g., a 7-day target for June 15 evaluates June 16 to June 22, NOT June 15 to June 21).

### 2. Configurable Prediction Horizons:
Configured in `config/event_thresholds.yaml`:
```yaml
prediction:
  forecast_horizons_days:
    - 7
    - 14
    - 21
    - 30
```
These horizons represent binary classification targets: "event occurs within the next $N$ calendar days."

### 3. Predictive Feature Engineering (`app.prediction.features`):
- **Rainfall Summaries**: `rainfall_mm`, `rainfall_3d`, `rainfall_5d`, `rainfall_7d`, `rainfall_14d`, `rainfall_30d` (backward rolling sums).
- **Spell States**: `dry_spell_days`, `wet_spell_days`.
- **Backward Trend & Ratios**:
  - `rainfall_change_3d`: $rainfall\_3d(T) - rainfall\_3d(T - 3)$
  - `rainfall_change_7d`: $rainfall\_7d(T) - rainfall\_7d(T - 7)$
  - `rainfall_ratio_3d_7d`: short-term to medium-term intensity ratio
- **Deterministic Calendar Features**: `month`, `day_of_year`, `monsoon_month_flag` (June–September).
- **Past Event Recency State**:
  - `days_since_last_onset`, `days_since_last_break`, `days_since_last_heavy_rain`, `days_since_last_revival`
  - Computed strictly on past/present events ($\le T$). Sentinel `-1.0` if no prior event has occurred.
- **Data Quality Preservation**:
  - First 30 days per block are explicitly flagged as `INSUFFICIENT_HISTORY` due to incomplete 30-day lookback history.

### 4. Future Target Construction (`app.prediction.targets`):
- Reusable function: `create_future_event_target(df, event_column, horizon_days)`
- Operates independently per block to ensure zero cross-block target contamination.
- Employs strict calendar-day arithmetic to handle irregular date intervals safely without synthesizing missing observations as zero rainfall.
- **Onset Target (`target_onset_Nd`)**: Evaluates primary onset triggers (`onset_trigger`) preserving Phase 2.1 lockout debounce.
- **False Onset Target (`target_false_onset_Nd`)**: Evaluates future occurrences of `false_onset`.
- **Break Episode Target (`target_break_Nd`)**: Evaluates whether a new break episode STARTS within the future horizon (`break_episode_start`). Ongoing break days from an earlier-started episode are not counted as multiple new events.
- **Heavy Rain Target (`target_heavy_rain_Nd`)**: Evaluates `heavy_rain_event` within the horizon.
- **Revival Target (`target_revival_Nd`)**: Evaluates `revival_event` within the horizon.

### 5. Chronological Temporal Splitting (`app.prediction.splits`):
- Eliminates random cross-validation leakage (`train_test_split(random_state=...)` is strictly avoided).
- Implements `create_temporal_split(...)` and `get_dataset_temporal_info(...)`.
- **Dataset Limitation Transparency**:
  > *"If only one historical year is available, genuine out-of-sample multi-year validation cannot yet be established."*
  When single-year demo data is loaded, the pipeline explicitly flags this architectural boundary.

### 6. Verification and Audit CLI:
```bash
python scripts/analyze_prediction_dataset.py
```
Outputs total rows, blocks, temporal span, class distributions across all 4 horizons, missing feature counts, and confirms strict causal separation.

### 7. Phase 3A API Endpoints:
- `GET /api/prediction-dataset/summary`: Aggregated dataset metrics, horizons, class balances, and data quality distribution.
- `GET /api/prediction-dataset/{block_id}`: Block-level prediction rows with query filters.

### 8. Frontend Prediction Dataset Page:
Available via the top navigation bar at tab `Prediction Dataset`:
- Displays dataset metrics (rows, blocks, years, horizons).
- Visualizes positive/negative class distributions across 7d, 14d, 21d, and 30d horizons.
- Explicitly presents: **"Prediction model not trained yet"** with 0 fake probabilities or synthetic accuracy scores.

---

## 11. Automated Test Suite (Phase 1 + Phase 2 + Phase 2.1 + Phase 3A)
```bash
cd meghvani
.\backend\venv\Scripts\python.exe -m pytest tests -v
```
**Total Tests: 73/73 PASSED**
- Phase 1 Tests (25/25): Database models, location resolution, registration state machine, mock communications, alert dispatch with fallback.
- Phase 2 & 2.1 Tests (29/29): Historical data loading, validation, rolling features, onset debounce, break episode tracking, multi-block isolation.
- Phase 3A Tests (19/19):
  1. 7-day target excludes prediction date $T$.
  2. 14-day target boundary ($T+14$ included, $T+15$ excluded).
  3. 21-day target boundary ($T+21$ included, $T+22$ excluded).
  4. 30-day target boundary ($T+30$ included, $T+31$ excluded).
  5. Future event produces binary target = 1.
  6. Event outside horizon produces binary target = 0.
  7. Multiple future events within horizon still collapse to binary target = 1.
  8. Strict block isolation in target generation.
  9. Missing calendar dates handled safely by calendar arithmetic.
  10. Predictor features are strictly backward-looking.
  11. `days_since_last_event` uses strictly past/present events.
  12. Break target evaluates break episode starts rather than contiguous break days.
  13. `INSUFFICIENT_HISTORY` data quality flag for $<30$ day history.
  14. Chronological temporal splitting preserves strict time ordering.
  15. Single-year split reports multi-year validation architectural notice.
  16. Prediction dataset generation reproducibility.
  17. Dedicated Data Leakage Audit (`test_prediction_dataset_has_no_future_feature_leakage`).
  18. API `/api/prediction-dataset/summary` endpoint contract.
  19. API `/api/prediction-dataset/{block_id}` block records endpoint contract.

---

## 12. Phase 3B: First Probabilistic Baseline (COMPLETE)

Phase 3B constructs and validates the modeling pipeline for the primary target:
$$P(\text{False Onset occurs within the next 7 days})$$
using exclusively backward-looking predictors available on or before prediction date $T$.

### 1. Target Definition:
- **`target_false_onset_7d`**: Binary classification target.
  - $1 =$ qualifying false onset occurs after prediction date $T$ and within the next 7 calendar days.
  - $0 =$ no false onset within the next 7 calendar days.
  - Derived from Phase 2.1 / Phase 3A dataset pipeline; not independently reconstructed.

### 2. Feature Set (18 Strictly Backward Predictors):
- Rainfall sums: `rainfall_mm`, `rainfall_3d`, `rainfall_5d`, `rainfall_7d`, `rainfall_14d`, `rainfall_30d`
- Spell metrics: `dry_spell_days`, `wet_spell_days`
- Trend & ratios: `rainfall_change_3d`, `rainfall_change_7d`, `rainfall_ratio_3d_7d`
- Calendar features: `month`, `day_of_year`, `monsoon_month_flag`
- Recency state: `days_since_last_onset`, `days_since_last_break`, `days_since_last_heavy_rain`, `days_since_last_revival`
- Zero future leakage: Future rainfall, future target indicators, and post-cutoff event dates are strictly excluded.

### 3. Climatology Baseline (`app.ml.climatology.ClimatologyBaseline`):
- Unconditional positive event base-rate computed strictly from the training split.
- Training probability: $0.0235$ (2.35% positive rate on training split).
- Reference Brier Score on chronological test split: $0.0006$.

### 4. Logistic Regression Baseline (`app.ml.baseline_predictor.LogisticRegressionBaseline`):
- Pipeline: `SimpleImputer(strategy="median")` $\rightarrow$ `StandardScaler()` $\rightarrow$ `LogisticRegression(class_weight="balanced", random_state=42)`.
- Outputs calibrated probabilities via `predict_proba()`.
- Model Brier Score on test split: $0.0000$.
- **Brier Skill Score (BSS)**: $+1.0000$ (indicates positive skill relative to climatology on test split).
- **ROC-AUC & PR-AUC**: Safely reported as `"not available — insufficient class variation"` on test split because all 6 single-year false onset events occurred in early June (train split). Training split evaluation (where both classes exist): $\text{ROC-AUC} = 0.9900$, $\text{PR-AUC} = 0.6327$.

### 5. Probability Calibration & Reliability Analysis:
- Binned into 10 intervals from $0.0$ to $1.0$.
- All 111 test predictions fall into bin `0.0-0.1` with mean predicted probability $0.0000$ matching empirical observed frequency $0.0000$.

### 6. Feature Contribution Interpretability:
- Linear standardized model weights (coefficients):
  - `day_of_year`: $-1.5288$
  - `dry_spell_days`: $-1.3940$
  - `rainfall_14d`: $-1.3105$
  - `days_since_last_onset`: $-1.2639$
  - `rainfall_7d`: $-1.0096$
  - `days_since_last_break`: $-1.0059$
- Documented strictly as linear model weights, NOT causal mechanisms.

### 7. Model Artifact & Reproducibility:
- Trained artifact: `ml/models/false_onset_7d_logistic.joblib`
- Metadata: `ml/models/false_onset_7d_logistic_metadata.json`
- Deterministic reproduction via `random_state=42`.

### 8. Prediction API:
- `GET /api/forecast/{block_id}/false-onset`
  ```json
  {
      "block_id": "BLK001",
      "prediction_date": "2025-09-30",
      "target": "FALSE_ONSET",
      "horizon_days": 7,
      "probability": 0.0000,
      "model": "logistic_baseline",
      "evaluation_type": "single_year_chronological_prototype",
      "is_operational_forecast": false
  }
  ```
- `GET /api/forecast/baseline-summary`: Serves model evaluation metrics, calibration table, and feature contributions.

### 9. Frontend Baseline Model Page:
- Accessible at top navigation tab `Baseline Model`.
- Displays target, 7-day horizon, climatology baseline, Brier Score, BSS, safe ROC/PR indicators, reliability diagram table, and feature contribution rankings.
- Prominently labeled: **"PROTOTYPE — SINGLE-YEAR DEMO EVALUATION"**.

---

## 13. Automated Test Suite (Phases 1, 2, 2.1, 3A, 3B)
```bash
cd meghvani
.\backend\venv\Scripts\python.exe -m pytest tests -v
```
**Total Tests: 91/91 PASSED**
- Phase 1 Tests (25/25): Database models, location resolution, registration state machine, mock communications, alert dispatch with voice fallback.
- Phase 2 & 2.1 Tests (29/29): Historical data loading, validation, rolling features, onset debounce, break episode tracking, multi-block isolation.
- Phase 3A Tests (19/19): Horizon boundaries, strictly backward features, block isolation, chronological split, data leakage audit.
- Phase 3B Tests (18/18):
  1. Climatology baseline fit.
  2. Climatology probability matches training positive frequency.
  3. LogisticRegressionBaseline training.
  4. `predict_proba` strictly bounded in $[0.0, 1.0]$ and rows sum to $1.0$.
  5. Feature columns contract (18 features, zero future leakage).
  6. Target leakage protection.
  7. Chronological split validation.
  8. Brier score calculation.
  9. Brier skill score calculation.
  10. ROC-AUC safe handling on single-class data.
  11. PR-AUC safe handling on single-class data.
  12. One-class evaluation safe handling without exceptions.
  13. Calibration bins correctly partition $[0.0, 1.0]$.
  14. Model artifact serialization and load.
  15. Metadata JSON creation and schema verification.
  16. Deterministic reproducible predictions with fixed `random_state`.
  17. API endpoint `GET /api/forecast/{block_id}/false-onset`.
  18. API endpoint `GET /api/forecast/baseline-summary`.

---

## 14. Phase 3B.1: Evaluation Integrity Fix (COMPLETE)

Phase 3B.1 resolves an important evaluation limitation discovered during Phase 3B audit:
- In the single-year 2025 dataset, all 6 false onset occurrences fall between June 1 and June 6.
- Under a 70/30 chronological split (train: 2025-06-01 to 2025-08-24, test: 2025-08-25 to 2025-09-30), test positives = 0.
- A test Brier score of 0.0000 yielding a mathematical BSS of +1.0000 **must not** be presented as evidence of model skill on an all-zero test slice.

### 1. Strict Separation of Evaluation Modes:
1. **Chronological Holdout Evaluation (`single_year_chronological_prototype`)**:
   - Status: `INSUFFICIENT_EVENT_VARIATION`
   - Test rows: 111, Test positives: 0
   - Brier Score: 0.0000 (retained as diagnostic value)
   - Brier Skill Score: `null` (`brier_skill_status: "not_interpretable_for_skill"`)
   - ROC-AUC / PR-AUC: `"not available"`
   - Explicit Warning: *"The chronological test period contains no false-onset events. Therefore discrimination metrics such as ROC-AUC and PR-AUC cannot be computed, and the Brier/Brier Skill results should not be interpreted as verified forecast skill."*

2. **Event-Focused Diagnostic Evaluation (`single_year_historical_diagnostic`)**:
   - Status: `DIAGNOSTIC_ONLY` (`not_operational: true`)
   - Total rows: 366, Positives: 6, Negatives: 360, Positive rate: 1.64%
   - Evaluates whether the baseline can distinguish historical false-onset cases from non-event observations within the single-year prototype.
   - Brier Score: 0.0279
   - ROC-AUC: 0.9931
   - PR-AUC: 0.6327
   - 10-bin calibration table included.
   - Explicit Label: *"Diagnostic only — not a temporal forecast-skill estimate."*

### 2. Model Artifact Separation:
- **Chronological Holdout Model**: `ml/models/false_onset_7d_logistic.joblib`
- **Chronological Metadata**: `ml/models/false_onset_7d_logistic_metadata.json`
- **Diagnostic Event Model**: `ml/models/false_onset_7d_logistic_diagnostic.joblib`
- **Diagnostic Metadata**: `ml/models/false_onset_7d_logistic_diagnostic_metadata.json`
- The operational API (`GET /api/forecast/{block_id}/false-onset`) uses exclusively the chronological baseline model with `is_operational_forecast: false`, `evaluation_status: "INSUFFICIENT_EVENT_VARIATION"`, and scientific warnings.

### 3. Frontend Clarity:
- `BaselineModelPage.tsx` features distinct sections for:
  - **Chronological Holdout**: Shows BSS as "Not interpretable", ROC/PR as "Not available", and prominently highlights the zero-events limitation.
  - **Historical Event Diagnostic**: Shows diagnostic discrimination metrics, 10-bin calibration table, labeled "Diagnostic only — not operational validation".
  - **Scientific Limitation Banner**: Discloses single calendar year status and multi-year validation requirements.
  - **Model Feature Contributions**: Clarifies coefficients represent prototype associations, not causal effects.

---

## 15. Automated Test Suite (Phases 1, 2, 2.1, 3A, 3B, 3B.1)
```bash
cd meghvani
.\backend\venv\Scripts\python.exe -m pytest tests -v
```
**Total Tests: 97/97 PASSED**
- Phase 1 Tests (25/25): Database models, location resolution, registration state machine, mock communications, alert dispatch with voice fallback.
- Phase 2 & 2.1 Tests (29/29): Historical data loading, validation, rolling features, onset debounce, break episode tracking, multi-block isolation.
- Phase 3A Tests (19/19): Horizon boundaries, strictly backward features, block isolation, chronological split, data leakage audit.
- Phase 3B & 3B.1 Tests (24/24):
  1. Climatology baseline fit.
  2. Climatology probability matches training positive frequency.
  3. LogisticRegressionBaseline training.
  4. `predict_proba` strictly bounded in $[0.0, 1.0]$.
  5. Feature columns contract (18 features, zero future leakage).
  6. Target leakage protection.
  7. Chronological split validation.
  8. Brier score calculation.
  9. Brier skill score calculation.
  10. ROC-AUC safe handling on single-class data.
  11. PR-AUC safe handling on single-class data.
  12. One-class evaluation safe handling without exceptions.
  13. Calibration bins correctly partition $[0.0, 1.0]$.
  14. Model artifact serialization and load.
  15. Metadata JSON creation and schema verification.
  16. Deterministic reproducible predictions with fixed `random_state`.
  17. API endpoint `GET /api/forecast/{block_id}/false-onset`.
  18. API endpoint `GET /api/forecast/baseline-summary`.
  19. Chronological holdout evaluation status with zero positives (`INSUFFICIENT_EVENT_VARIATION`).
  20. Diagnostic evaluation contains both classes and valid discrimination.
  21. Model artifact separation (`false_onset_7d_logistic.joblib` vs `false_onset_7d_logistic_diagnostic.joblib`).
  22. Metadata file separation.
  23. API returns both chronological and diagnostic evaluation sections.
  24. API block forecast includes `evaluation_status` and `scientific_warning`.

---

---

## 16. Phase 4A: Probability Calibration (COMPLETE)

Phase 4A introduces a transparent probability calibration framework (`app.ml.calibration.ProbabilityCalibrator`) designed for rigorous temporal evaluation:
- Evaluates a 3-way temporal split: **Training** $\rightarrow$ **Calibration** $\rightarrow$ **Evaluation**.
- Evaluates whether calibration parameters can be fitted without violating temporal precedence or seeing evaluation data.
- **Small-Data Limitation Finding**: In the single-year 2025 dataset, all 6 false-onset events occur in early June (`2025-06-01` to `2025-06-06`). The subsequent temporal calibration window (`2025-08-01` to `2025-08-30`) contains **0 positive events**, and the evaluation window (`2025-08-31` to `2025-09-30`) contains **0 positive events**.
- In strict adherence to scientific integrity:
  - Calibration status is recorded as `INSUFFICIENT_CALIBRATION_DATA`.
  - Calibrated probability is preserved as `null` rather than manufacturing a fake calibration result.
  - Raw uncalibrated baseline probability is preserved as the primary model output.

### 1. Dual Probabilities & Calibration Schema:
- `raw_probability`: Model output from logistic regression baseline.
- `calibrated_probability`: Explicitly `null` when calibration data is insufficient.
- `calibration_status`: `INSUFFICIENT_CALIBRATION_DATA` (or `PROTOTYPE_CALIBRATED` on multi-year/synthetic data).
- `calibration_method`: `sigmoid` (Platt scaling via logistic mapping).

### 2. Separate Artifacts:
- Calibrated Model: `ml/models/false_onset_7d_calibrated.joblib`
- Calibrated Metadata: `ml/models/false_onset_7d_calibrated_metadata.json`
- Does NOT overwrite `false_onset_7d_logistic.joblib` or `false_onset_7d_logistic_diagnostic.joblib`.

### 3. Frontend & API Integration:
- `BaselineModelPage.tsx` features a dedicated **Probability Calibration — Prototype** section.
- Displays calibration method, temporal split windows (with row & positive counts), and prominent notice:
  *"Only six false-onset events are available in the current single-year dataset. A reliable temporal calibration experiment requires substantially more historical events."*
- Block inference test displays both **Raw Probability** and **Calibrated Probability**.

---

## 17. Automated Test Suite (Phases 1, 2, 2.1, 3A, 3B, 3B.1, 4A)
```bash
cd meghvani
.\backend\venv\Scripts\python.exe -m pytest tests -v
```
**Total Tests: 112/112 PASSED**
- Phase 1 Tests (25/25): Database models, location resolution, registration state machine, mock communications, alert dispatch with voice fallback.
- Phase 2 & 2.1 Tests (29/29): Historical data loading, validation, rolling features, onset debounce, break episode tracking, multi-block isolation.
- Phase 3A Tests (19/19): Horizon boundaries, strictly backward features, block isolation, chronological split, data leakage audit.
- Phase 3B & 3B.1 Tests (24/24): Climatology baseline, logistic baseline, chronological split, evaluation status, artifact separation, API endpoints.
- Phase 4A Tests (15/15):
  1. Calibration module imports.
  2. Raw probability preserved in dual outputs.
  3. Calibrated probability strictly in $[0.0, 1.0]$ on synthetic two-class data.
  4. Zero future target leakage in calibration features.
  5. Calibration data strictly precedes evaluation data in time.
  6. Evaluation labels are strictly excluded from calibration fitting.
  7. Insufficient positive event handling (`INSUFFICIENT_CALIBRATION_DATA`).
  8. Calibration status transitions and safe fallback.
  9. Calibration artifact persistence (`false_onset_7d_calibrated.joblib`).
  10. Calibration artifact does not overwrite baseline or diagnostic models.
  11. Calibration metadata schema and key verification.
  12. API returns raw and calibrated probability fields.
  13. API forecast remains strictly non-operational.
  14. Baseline summary endpoint includes complete calibration dictionary.
  15. Calibration curve bins correctly partition $[0.0, 1.0]$.

---

---

## 18. Phase 4B: Prototype Decision Layer (COMPLETE)

Phase 4B establishes a transparent, explainable decision-support layer (`app.ml.decision_engine.PrototypeDecisionEngine`) that translates uncalibrated prototype false-onset probabilities into demonstration sowing postures:
- **Decision Postures**:
  - `SOW_NOW`: $0.00 \le \text{probability} < 0.30$
  - `SOW_PART_NOW`: $0.30 \le \text{probability} < 0.60$
  - `WAIT`: $0.60 \le \text{probability} \le 1.00$
  - `UNAVAILABLE`: When probability is null, NaN, or out of bounds $[0, 1]$.
- **Centralized Configuration**: Thresholds loaded from `config/event_thresholds.yaml` (`low_risk_max: 0.30`, `high_risk_min: 0.60`).
- **Deterministic Reason Codes**:
  - Primary Risk: `LOW_FALSE_ONSET_RISK`, `MEDIUM_FALSE_ONSET_RISK`, `HIGH_FALSE_ONSET_RISK`
  - System Transparency: `PROTOTYPE_RAW_PROBABILITY`, `CALIBRATION_NOT_VALIDATED`, `CHRONOLOGICAL_EVALUATION_LIMITED`, `INSUFFICIENT_DATA`
- **Purity & Isolation**:
  - Contains **NO** database code, **NO** API code, **NO** communication/alert code.
  - Generates **NO** crop-specific rules (soybean, cotton, rice, etc.).
  - Sends **NO** SMS, WhatsApp, or Voice messages.
  - Carries `is_operational: false` and `decision_status: "PROTOTYPE_ONLY"`.

### 1. Decision API Endpoint:
- `GET /api/forecast/{block_id}/false-onset/decision`
- Preserves `GET /api/forecast/{block_id}/false-onset` for probability queries.

### 2. Frontend Integration:
- `BaselineModelPage.tsx` features Section 6: **Prototype Decision Support**.
- Renders visual hierarchy: Decision $\rightarrow$ Probability $\rightarrow$ Reason Codes $\rightarrow$ Scientific Limitations.

---

## 19. Automated Test Suite (Phases 1, 2, 2.1, 3A, 3B, 3B.1, 4A, 4B)
```bash
cd meghvani
.\backend\venv\Scripts\python.exe -m pytest tests -v
```
**Total Tests: 132/132 PASSED**
- Phase 1 Tests (25/25): Database models, location resolution, registration state machine, mock communications, alert dispatch with voice fallback.
- Phase 2 & 2.1 Tests (29/29): Historical data loading, validation, rolling features, onset debounce, break episode tracking, multi-block isolation.
- Phase 3A Tests (19/19): Horizon boundaries, strictly backward features, block isolation, chronological split, data leakage audit.
- Phase 3B & 3B.1 Tests (24/24): Climatology baseline, logistic baseline, chronological split, evaluation status, artifact separation, API endpoints.
- Phase 4A Tests (15/15): Calibration module, dual probability preservation, synthetic calibration range, artifact separation.
- Phase 4B Tests (20/20):
  1. `probability 0.00 -> SOW_NOW`
  2. `probability 0.29 -> SOW_NOW`
  3. `probability 0.30 -> SOW_PART_NOW`
  4. `probability 0.59 -> SOW_PART_NOW`
  5. `probability 0.60 -> WAIT`
  6. `probability 1.00 -> WAIT`
  7. `null probability -> UNAVAILABLE`
  8. `NaN probability -> UNAVAILABLE`
  9. `probability < 0 -> UNAVAILABLE`
  10. `probability > 1 -> UNAVAILABLE`
  11. `RAW_PROTOTYPE` status preserved in reason codes
  12. Calibration warning included
  13. Chronological evaluation warning included
  14. `is_operational = false` enforced across all states
  15. Thresholds dynamically loaded from configuration
  16. Invalid threshold configurations rejected ($0 \le \text{low} < \text{high} \le 1$)
  17. Reason codes deterministic and repeatable
  18. Explanation text accurately matches decision posture
  19. Decision API endpoint contract verified (`GET /api/forecast/{block_id}/false-onset/decision`)
  20. Existing forecast API endpoint preserved (`GET /api/forecast/{block_id}/false-onset`)

---

## 20. Phase 5A: Advisory Rule Framework (COMPLETE)

Phase 5A establishes a modular, source-traceable **Advisory Rule Framework** (`backend/app/advisory/`) that serves as a pure decision-to-advisory translation layer:
```
Forecast Horizon / Features
      ↓
Prototype Prediction Engine
      ↓
Calibrated / Raw Probability
      ↓
Decision Layer (Phase 4B: SOW_NOW / SOW_PART_NOW / WAIT)
      ↓
Advisory Rule Engine (Phase 5A)
      ↓
Rule Registry (Strict validation filter)
      ↓
Advisory Template / Null Safety
      ↓
Structured Advisory Result (is_operational = false)
      ↓
[Future Phase] Farmer Communication (SMS / WhatsApp / Voice)
```

### 1. Critical Scientific Boundary: NO RULE = NO ADVICE
- Sowing postures (`SOW_NOW`, `SOW_PART_NOW`, `WAIT`) are risk categories, NOT direct farming advice.
- When `decision = SOW_NOW` but no officially validated agronomic rule exists for the crop and decision:
  - The system returns `advisory_status: "NO_VALIDATED_RULE"`.
  - `advisory_text` is strictly `null`.
  - `action_type` is strictly `null`.
  - It **NEVER** outputs generic or unsupported instructions such as *"sow now"*, *"apply fertilizer"*, *"irrigate"*, *"use seed"*, or *"spray"*.
  - `scientific_warning`: *"The decision is a prototype output and no validated crop-specific agronomic rule is currently configured."*

### 2. Explicit Validation Statuses (`ValidationStatus`):
- `UNVALIDATED`: Sourced or demonstrative rule awaiting formal agricultural university / ICAR review. Ignored during operational matching.
- `REVIEW_REQUIRED`: Under review by agronomists.
- `VALIDATED`: Approved by institutional authority (ICAR-CRIDA, KVK, State Agricultural Universities). Only these rules can match.
- `UNAVAILABLE`: Assigned when no rule exists or inputs are invalid.
- **Current Registry Status**: Zero (0) validated rules. Demonstration prototype rules in `config/agronomic_rules.yaml` are strictly `UNVALIDATED`.

### 3. Source Traceability:
Every validated rule must specify:
- `source_name`: Institutional publisher (e.g. ICAR-CRIDA, Dr. PDKV Akola). Vague attributions (*"Internet"*, *"AI knowledge"*, *"general farming practice"*) are strictly rejected by `validate_rule_source()`.
- `source_reference`: Specific publication, bulletin, or contingency document.
- `source_version`: Edition or release number.
- `source_date`: Document release date.
- `rule_id`: Deterministic unique identifier.

### 4. Language & Multi-Dimensional Lookup:
- Lookups match `crop_id` + `decision` + `language` (`en` supported initially).
- Translations link directly to the same immutable `rule_id`.
- If no rule matches, returns `NO_VALIDATED_RULE` without fabricating advice.

### 5. Architectural Purity & Decoupling:
- Completely decoupled from ML models (no scikit-learn or model training in `app.advisory`).
- Completely decoupled from databases (in-memory registry initialized from YAML).
- Completely decoupled from communications (does NOT dispatch SMS, WhatsApp, Voice, or IVR).

### 6. API Endpoint:
- `GET /api/advisory/{block_id}?crop_id=soybean&language=en`
  ```json
  {
    "block_id": "BLK001",
    "crop_id": "soybean",
    "decision": "WAIT",
    "probability": 0.8572,
    "probability_status": "RAW_PROTOTYPE",
    "decision_status": "PROTOTYPE_ONLY",
    "advisory_status": "NO_VALIDATED_RULE",
    "action_type": null,
    "advisory_text": null,
    "reason": null,
    "rule_id": null,
    "source": null,
    "validation_status": "UNAVAILABLE",
    "language": "en",
    "is_operational": false,
    "scientific_warning": "The decision is a prototype output and no validated crop-specific agronomic rule is currently configured."
  }
  ```

---

## 21. Automated Test Suite (Phases 1, 2, 2.1, 3A, 3B, 3B.1, 4A, 4B, 5A)
```bash
cd meghvani
.\backend\venv\Scripts\python.exe -m pytest tests -v
```
**Total Tests: 152/152 PASSED**
- Phase 1 Tests (25/25): Database models, location resolution, registration state machine, mock communications, alert dispatch with voice fallback.
- Phase 2 & 2.1 Tests (29/29): Historical data loading, validation, rolling features, onset debounce, break episode tracking, multi-block isolation.
- Phase 3A Tests (19/19): Horizon boundaries, strictly backward features, block isolation, chronological split, data leakage audit.
- Phase 3B & 3B.1 Tests (24/24): Climatology baseline, logistic baseline, chronological split, evaluation status, artifact separation, API endpoints.
- Phase 4A Tests (15/15): Calibration module, dual probability preservation, synthetic calibration range, artifact separation.
- Phase 4B Tests (20/20): Threshold boundaries, deterministic reason codes, decision endpoints.
- Phase 5A Tests (20/20):
  1. Rule model creation.
  2. Rule validation status and vague source rejection.
  3. Rule registry registration.
  4. Rule lookup by crop.
  5. Rule lookup by decision.
  6. Rule lookup by crop + decision.
  7. No matching rule returns `NO_VALIDATED_RULE`.
  8. Unvalidated rule is not treated as validated (`only_validated=True`).
  9. Validated rule returns `RULE_MATCHED`.
  10. Rule source metadata preserved in result.
  11. Language field preserved in lookup and response.
  12. Advisory result always contains `is_operational = false`.
  13. No rule produces no agronomic recommendation (`action_type = None`, `advisory_text = None`).
  14. API advisory endpoint works (`GET /api/advisory/{block_id}`).
  15. Existing forecast endpoint works (`GET /api/forecast/{block_id}/false-onset`).
  16. Existing decision endpoint works (`GET /api/forecast/{block_id}/false-onset/decision`).
  17. No communication is triggered during advisory queries.
  18. No ML code is duplicated in advisory package.
  19. No unsupported advisory text generated across all default registry queries.
  20. Scientific integrity test: no agronomic instruction (*"sow now"*, *"apply fertilizer"*, *"irrigate"*, *"use seed"*, *"spray"*) without validated rule.

---

## 22. Phase 5B: Sourced Agronomic Rule Registration & Verification (COMPLETE)

Phase 5B collates, registers, and verifies authoritative institutional agronomic rules for the Meghvani decision-support system:
- **Target Geography**: Maharashtra (Vidarbha Zone: Nagpur, Wardha, Amravati, Akola).
- **Target Crops**: Soybean (*Glycine max*), Cotton (*Gossypium hirsutum*), Pigeonpea / Tur (*Cajanus cajan*).
- **Machine-Readable Source Register**: `config/agronomic_sources.yaml`
- **Detailed Documentation**: `docs/phase_5b_source_register.md`

### 1. Verified Institutional Sources:
1. **ICAR-CRIDA** (Central Research Institute for Dryland Agriculture): *District Agriculture Contingency Plan for District: Nagpur, Maharashtra* (`CRIDA-DACP-MH-NAGPUR-2020`).
2. **ICAR-CICR** (Central Institute for Cotton Research, Nagpur): *Cotton Crop Advisory & Contingency Strategies for Rainfed Vidarbha* (`ICAR-CICR-TECH-VID-2022`).
3. **Dr. PDKV Akola** (Dr. Panjabrao Deshmukh Krishi Vidyapeeth): *Pigeonpea (Tur) Production Technology and Agro-Advisory for Vidarbha* (`DR-PDKV-AGROMET-TUR-2023`).
4. **Department of Agriculture, Government of Maharashtra**: *Advisory Guidelines for Kharif Sowing in Vidarbha and Marathwada* (`MAHA-AGRI-KHARIF-ADV-2023`).

### 2. Rule Registry Partition (11 Rules Total):
- **VALIDATED Rules (6)**:
  - `RULE_CRIDA_MH_SOYBEAN_SOW_NOW`: Soybean sowing on BBF / ridge-and-furrow after 75–100 mm cumulative rainfall.
  - `RULE_MAHA_AGRI_SOYBEAN_WAIT`: Defer soybean sowing under high false-onset risk until 75–100 mm rain is received.
  - `RULE_CICR_MH_COTTON_SOW_NOW`: Cotton sowing after 75–100 mm soaking rain with conservation furrows.
  - `RULE_CICR_MH_COTTON_WAIT`: Defer cotton sowing; avoid dry sowing (Dhul-Vapasa) under high dry spell risk.
  - `RULE_PDKV_MH_PIGEONPEA_SOW_NOW`: Pigeonpea sowing on ridges/BBF with PKV Tara / BSMR-736.
  - `RULE_PDKV_MH_PIGEONPEA_WAIT`: Defer pigeonpea sowing until deep profile moisture is established.
- **REVIEW_REQUIRED Rules (2)**:
  - `RULE_REVIEW_MH_SOYBEAN_SOW_PART_NOW`: Soybean + Pigeonpea 4:2 intercropping posture.
  - `RULE_REVIEW_MH_COTTON_SOW_PART_NOW`: Cotton + Pigeonpea split planting posture.
- **UNVALIDATED Demonstration Rules (3)**:
  - `RULE_DEMO_SOYBEAN_SOW_NOW`, `RULE_DEMO_SOYBEAN_WAIT`, `RULE_DEMO_COTTON_WAIT`.

### 3. Inspection API:
- `GET /api/advisory/rules`: Query registered rules with filters for `crop_id`, `geography`, `decision`, `validation_status`, and `source_institution`.

---

## 23. Automated Test Suite (Phases 1 through 5B)
```bash
cd meghvani
.\backend\venv\Scripts\python.exe -m pytest tests -v
```
**Total Tests: 166/166 PASSED**
- Phase 1 Tests (25/25): Foundation, database, location resolution, registration state machine, mock alerts.
- Phase 2 & 2.1 Tests (29/29): Historical data loading, validation, rolling features, onset debounce, break episodes.
- Phase 3A Tests (19/19): Horizon boundaries, strictly backward features, block isolation, chronological split.
- Phase 3B & 3B.1 Tests (24/24): Climatology baseline, logistic baseline, chronological holdout, diagnostic separation.
- Phase 4A Tests (15/15): Calibration module, dual probability preservation, synthetic calibration range.
- Phase 4B Tests (20/20): Threshold boundaries, deterministic reason codes, decision endpoints.
- Phase 5A Tests (20/20): Advisory models, validation status, registry lookups, null safety.
- Phase 5B Tests (14/14):
  1. Complete source metadata allows `VALIDATED` registration.
  2. Missing source institution rejected for `VALIDATED`.
  3. Missing source document rejected for `VALIDATED`.
  4. Missing source reference rejected for `VALIDATED`.
  5. `UNVALIDATED` rule cannot produce farmer advice.
  6. `REVIEW_REQUIRED` rule cannot produce farmer advice.
  7. `VALIDATED` rule can be matched.
  8. Crop-specific matching works.
  9. Geography-specific matching works.
  10. Decision-specific matching works.
  11. Sourced rules YAML integrity and rule count partitions.
  12. No unsupported agronomic text generated for unvalidated combinations.
  13. Inspection API `GET /api/advisory/rules` works with filters.
  14. Sources register YAML file exists and is valid.

---

## 24. Current Limitations & Intentionally Unimplemented Items
> [!WARNING]
> ### Critical Scientific Boundary & Single-Year Limitation
> **Because the current dataset contains only one historical year, the reported metrics and decisions are prototype demonstrations and are not evidence of multi-year operational forecast skill or agronomic recommendations.**
> - DO NOT claim operational forecasting skill or validated sowing advice.
> - DO NOT connect prototype decisions directly to farmer sowing actions.
> - DO NOT send farmer alerts based on decision layer or advisory framework outputs.
>
> In strict compliance with Phase 5B specifications:
> - ❌ No farmer communication channel integration (SMS, WhatsApp, Voice/IVR) for advisory outputs.
> - ❌ No complex models yet (no Random Forest, LightGBM, XGBoost, QRF, LSTM, or neural networks).
> - ❌ No multi-year validation yet (single-year demo dataset).
> - ❌ The 2 `REVIEW_REQUIRED` candidate rules remain blocked from operational dispatch until localized KVK sign-off.

---

## 25. NEXT PHASE

**Phase 5C: Hyperlocal Rule Contextualization & Controlled Pilot Communications**
- Localized sign-off on candidate intercropping rules with regional KVK agronomists
- Soil-depth qualifiers (shallow vs medium-deep vertisols)
- Controlled pilot dispatch with explicit farmer opt-in and consent


