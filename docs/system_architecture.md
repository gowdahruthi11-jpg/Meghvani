# 🌧️ Meghvani — Complete System Architecture

> **Hyperlocal Monsoon Onset & Break Prediction System**  
> Block & Village Scale Agrometeorological Intelligence · Smart India Hackathon 2026 Prototype

---

## 1. High-Level System Overview

**Meghvani** is a full-stack agrometeorological decision-support system that:

1. **Ingests** historical daily rainfall data at block level
2. **Detects** monsoon lifecycle events (onset, false-onset, break, heavy rain, revival)
3. **Engineers** strictly causal predictive features (zero future leakage)
4. **Trains** probabilistic ML models for event prediction
5. **Translates** probabilities → sowing postures → crop-specific validated advisories
6. **Delivers** advisories to farmers via SMS / WhatsApp / Voice in regional language

---

## 2. Layered Architecture Map

```
╔══════════════════════════════════════════════════════════════════╗
║                      FARMER INTERFACE LAYER                      ║
║  SMS ("MEGH") │ Missed Call │ WhatsApp │ IVR Voice              ║
╚═══════════════════════════╦══════════════════════════════════════╝
                            │
╔═══════════════════════════▼══════════════════════════════════════╗
║                      FRONTEND LAYER (React)                      ║
║  Vite + React 18 + TypeScript + Tailwind CSS + Lucide Icons      ║
║                                                                  ║
║  Pages:                                                          ║
║  ┌─────────────────────┐  ┌────────────────────────────────┐    ║
║  │ LandingPage         │  │ OfficerDashboard               │    ║
║  │ FarmerRegistration  │  │ AlertCenterPage                │    ║
║  │ HistoricalAnalysis  │  │ ScientificValidationPage       │    ║
║  │ PredictionDataset   │  │ BaselineModelPage              │    ║
║  │ ForecastPage        │  │ ExplainableAIPage              │    ║
║  │ AdvisoriesPage      │  │ SIHDemoPage                    │    ║
║  │ ObservationFeedback │  │ LiveMapPage                    │    ║
║  │ MonsoonPrediction   │  │ DataModelPage / SystemStatus   │    ║
║  └─────────────────────┘  └────────────────────────────────┘    ║
╚═══════════════════════════╦══════════════════════════════════════╝
                            │  HTTP / REST  (Vite Proxy → :8000)
╔═══════════════════════════▼══════════════════════════════════════╗
║                   API GATEWAY LAYER (FastAPI)                    ║
║  17 REST Routers under /api prefix                               ║
║                                                                  ║
║  /health  /blocks  /villages  /crops  /farmers  /registration    ║
║  /observations  /alerts  /weather  /historical  /prediction      ║
║  /forecast  /advisory  /demo  /validation  /calibration          ║
║  /rolling-origin                                                 ║
╚══╦════════╦═══════════╦═════════════╦════════════════════════════╝
   │        │           │             │
   ▼        ▼           ▼             ▼
┌──────┐ ┌──────┐ ┌──────────┐ ┌──────────────┐
│Conver│ │Severity│ │Advisory │ │ ML / Science │
│sation│ │Alert  │ │Rule     │ │ Layer        │
│State │ │Router │ │Engine   │ │              │
│Machine│ └──────┘ └──────────┘ └──────────────┘
└──────┘
   │                              │
   ▼                              ▼
╔══════════════════════════════════════════════════════════════════╗
║               DATABASE LAYER (SQLAlchemy 2.0 ORM)               ║
║  Development: SQLite  │  Production: PostgreSQL + PostGIS        ║
║  Migrations: Alembic  │  Seeder: DEMO data                      ║
╚══════════════════════════════════════════════════════════════════╝
   │
   ▼
╔══════════════════════════════════════════════════════════════════╗
║             COMMUNICATION PROVIDER LAYER (Mocked)               ║
║  SMS │ WhatsApp │ Voice │ Missed-Call (MockProvider in Phase 1)  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2, Uvicorn |
| **ORM / Database** | SQLAlchemy 2.0, Alembic migrations |
| **DB (Dev)** | SQLite (`meghvani.db`) |
| **DB (Prod)** | PostgreSQL + PostGIS |
| **Data / Science** | pandas, numpy, scipy, scikit-learn, joblib |
| **Config** | PyYAML (`config/*.yaml`) |
| **Frontend** | React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons |
| **Testing** | pytest, FastAPI TestClient (HTTPX) |
| **Containerization** | Docker, Docker Compose |

---

## 4. Project Directory Structure

```
meghvani/
├── backend/
│   ├── alembic/                      # Database migration scripts
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry point & lifespan
│   │   ├── config.py                 # YAML loaders + Pydantic Settings
│   │   ├── auth.py                   # Authentication utilities
│   │   │
│   │   ├── api/                      # 17 REST API routers
│   │   │   ├── health.py             # GET /api/health
│   │   │   ├── blocks.py             # GET /api/blocks
│   │   │   ├── villages.py           # GET /api/villages
│   │   │   ├── crops.py              # GET /api/crops
│   │   │   ├── farmers.py            # CRUD /api/farmers
│   │   │   ├── registration.py       # POST /api/registration (SMS state machine)
│   │   │   ├── observations.py       # POST /api/observations (crowd ground-truth)
│   │   │   ├── alerts.py             # POST /api/alerts (severity routing)
│   │   │   ├── weather.py            # GET /api/weather
│   │   │   ├── historical.py         # GET /api/historical/*
│   │   │   ├── prediction.py         # GET /api/prediction-dataset/*
│   │   │   ├── forecast.py           # GET /api/forecast/*
│   │   │   ├── advisory.py           # GET /api/advisory/*
│   │   │   ├── demo.py               # GET /api/demo/*
│   │   │   └── validation.py         # GET /api/validation, /calibration, /rolling-origin
│   │   │
│   │   ├── database/
│   │   │   ├── database.py           # Engine & SessionLocal factory
│   │   │   ├── base.py               # DeclarativeBase
│   │   │   ├── migrations.py         # Runtime migration runner
│   │   │   └── seed.py               # DEMO data seeder
│   │   │
│   │   ├── models/                   # 9 SQLAlchemy ORM entities
│   │   │   ├── block.py              # Block (spatial unit for meteorology)
│   │   │   ├── village.py            # Village (PIN-code mapped, farmer localization)
│   │   │   ├── crop.py               # Crop catalog
│   │   │   ├── farmer.py             # Farmer profile (privacy-preserving)
│   │   │   ├── weather.py            # Weather observations
│   │   │   ├── registration_session.py # SMS state machine sessions
│   │   │   ├── farmer_observation.py # Crowd observations (RAIN/DRY/HEAVY_RAIN)
│   │   │   └── alert_log.py          # Dispatched alert records
│   │   │
│   │   ├── schemas/                  # Pydantic v2 validation contracts
│   │   │   ├── block.py, village.py, crop.py, farmer.py
│   │   │   ├── weather.py, observation.py, alert.py, registration.py
│   │   │
│   │   ├── services/                 # Core business logic services
│   │   │   ├── location_service.py   # Block/Village PIN-code resolution
│   │   │   ├── farmer_service.py     # Farmer CRUD & consent checks
│   │   │   ├── registration_service.py # Conversational state machine
│   │   │   ├── weather_service.py    # Weather data management
│   │   │   ├── advisory_service.py   # Advisory orchestration
│   │   │   └── alert_service.py      # Alert dispatch with fallback
│   │   │
│   │   ├── communication/            # Multi-channel provider abstractions
│   │   │   ├── base.py               # Abstract provider interface
│   │   │   ├── sms.py                # SMS channel
│   │   │   ├── voice.py              # Voice / IVR channel
│   │   │   ├── whatsapp.py           # WhatsApp channel
│   │   │   └── mock_provider.py      # Mock (Phase 1 development)
│   │   │
│   │   ├── historical/               # Phase 2: Rainfall pipeline
│   │   │   ├── loader.py             # CSV ingestion
│   │   │   ├── validator.py          # Data quality checks
│   │   │   ├── features.py           # Backward-looking rolling features
│   │   │   ├── event_detector.py     # Onset / break / heavy-rain detection
│   │   │   └── dataset_builder.py    # Final labeled dataset export
│   │   │
│   │   ├── prediction/               # Phase 3A: Prediction feature & target engineering
│   │   │   ├── features.py           # 18 causal predictors
│   │   │   ├── targets.py            # Future event binary targets
│   │   │   └── splits.py             # Chronological temporal splitting
│   │   │
│   │   ├── ml/                       # Phase 3B–8B: Machine learning pipeline
│   │   │   ├── baseline_predictor.py # Logistic Regression baseline
│   │   │   ├── climatology.py        # Unconditional climatology baseline
│   │   │   ├── calibration.py        # Platt scaling probability calibration
│   │   │   ├── decision_engine.py    # Probability → sowing posture
│   │   │   ├── evaluation.py         # Brier Score, BSS, ROC/PR-AUC
│   │   │   ├── model_loader.py       # joblib artifact loading
│   │   │   ├── rolling_origin.py     # Rolling-origin cross-validation
│   │   │   ├── multiyear_validation.py # Multi-year out-of-sample validation
│   │   │   ├── in_season_evaluation.py # In-season event evaluation
│   │   │   └── label_sensitivity.py  # Label threshold sensitivity analysis
│   │   │
│   │   ├── advisory/                 # Phase 5A–5B: Advisory rule framework
│   │   │   # In-memory rule registry, validation status, source traceability
│   │   │
│   │   └── observations/             # Farmer crowd-truth submission
│   │
│   ├── requirements.txt
│   ├── .env / .env.example
│   └── Dockerfile
│
├── frontend/
│   └── src/
│       ├── pages/                    # 18 React page components
│       ├── components/               # Shared UI (Navbar, Footer, etc.)
│       ├── services/                 # Typed Axios/Fetch API client
│       ├── types/                    # TypeScript interfaces
│       ├── App.tsx                   # Router & layout
│       └── index.css                 # Global styles
│
├── config/                           # YAML configuration files
│   ├── app.yaml                      # App settings & CORS
│   ├── event_thresholds.yaml         # Onset, false-onset, break, heavy-rain thresholds
│   ├── event_definitions.yaml        # Event definitions
│   ├── crops.yaml                    # Kharif crop catalog
│   ├── blocks.yaml                   # Block metadata
│   ├── communication.yaml            # Severity routing & voice retry matrix
│   ├── advisory_rules.yaml           # Demo agronomic decision rules
│   ├── agronomic_rules.yaml          # Full rule registry (validated + unvalidated)
│   ├── agronomic_sources.yaml        # Source institution register
│   └── decision_costs.yaml           # Decision cost weights
│
├── data/
│   ├── raw/rainfall/                 # Raw daily rainfall CSV
│   ├── processed/                    # historical_events.csv, prediction_dataset.csv
│   ├── sample/                       # Sample timeseries format
│   └── location/                     # Block & village metadata
│
├── ml/
│   ├── models/                       # Trained model artifacts (.joblib + _metadata.json)
│   ├── features/                     # Feature engineering modules
│   ├── training/                     # Training pipelines
│   └── evaluation/                   # Calibration & skill metrics
│
├── scripts/                          # CLI utilities
├── tests/                            # 166+ automated tests
├── notebooks/                        # Jupyter exploration
├── docker-compose.yml
└── README.md
```

---

## 5. Data Flow Architecture (End-to-End)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION PIPELINE (Phase 2)                │
│                                                                     │
│  Raw Rainfall CSV (data/raw/rainfall/demo_rainfall.csv)             │
│         ↓ RainfallDataLoader                                        │
│         ↓ RainfallValidator (non-neg, ISO dates, duplicates)        │
│         ↓ RainfallFeatureEngineer                                   │
│           • Rolling sums: 1d, 3d, 5d, 7d, 14d, 30d                │
│           • Spell metrics: dry_spell_days, wet_spell_days           │
│           • Intensity classifications                                │
│         ↓ EventDetector                                             │
│           • Onset trigger (30-day lockout debounce)                 │
│           • False-onset detection (lookahead dry spell ≥ 7d)        │
│           • Break spells w/ episode IDs (dry streak ≥ 5d, <2.5mm)  │
│           • Heavy rain flags (≥ 64.5 mm/day)                       │
│           • Revival (≥ 15mm over 2d ending break)                  │
│         ↓ HistoricalDatasetBuilder                                  │
│  Output: data/processed/historical_events.csv                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│               PREDICTIVE FEATURE ENGINEERING (Phase 3A)            │
│                                                                     │
│  For each Prediction Date T:                                        │
│  • Features: STRICTLY backward-looking (date ≤ T)                  │
│    - rainfall_mm, 3d, 5d, 7d, 14d, 30d                             │
│    - dry_spell_days, wet_spell_days                                 │
│    - rainfall_change_3d/7d, ratio_3d_7d                             │
│    - month, day_of_year, monsoon_month_flag                        │
│    - days_since_last_onset/break/heavy_rain/revival                 │
│  • Targets: STRICTLY forward-looking (date > T)                    │
│    - target_onset_Nd, target_false_onset_Nd                        │
│    - target_break_Nd, target_heavy_rain_Nd, target_revival_Nd      │
│    - Horizons: 7d, 14d, 21d, 30d                                   │
│  • Chronological temporal split (no random shuffling)              │
│  Output: data/processed/prediction_dataset.csv                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                    ML MODEL PIPELINE (Phase 3B–4B)                  │
│                                                                     │
│  Climatology Baseline ──────────────────────────────────┐          │
│  (unconditional positive event base-rate)               │          │
│                                                         ▼          │
│  Logistic Regression Baseline                    Brier Skill Score  │
│  (SimpleImputer → StandardScaler → LogReg)       BSS = model vs    │
│  18 strictly backward predictors                 climatology        │
│         ↓                                                          │
│  Probability Calibration (Phase 4A)                                │
│  • Platt scaling (sigmoid) on 3-way temporal split                 │
│  • raw_probability + calibrated_probability (or null if insuff.)   │
│         ↓                                                          │
│  Decision Engine (Phase 4B)                                        │
│  • SOW_NOW      (probability < 0.30)                               │
│  • SOW_PART_NOW (0.30 ≤ probability < 0.60)                        │
│  • WAIT         (probability ≥ 0.60)                               │
│  • UNAVAILABLE  (null/NaN/out-of-range)                            │
│  Artifacts: ml/models/*.joblib + *_metadata.json                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                  ADVISORY RULE FRAMEWORK (Phase 5A–5B)              │
│                                                                     │
│  Decision Posture + crop_id + language                             │
│         ↓ Rule Registry lookup (in-memory, from YAML)              │
│         ↓ Validation filter: ONLY VALIDATED rules match            │
│                                                                     │
│  Validated Rules (6):                                              │
│  • RULE_CRIDA_MH_SOYBEAN_SOW_NOW                                   │
│  • RULE_MAHA_AGRI_SOYBEAN_WAIT                                     │
│  • RULE_CICR_MH_COTTON_SOW_NOW                                     │
│  • RULE_CICR_MH_COTTON_WAIT                                        │
│  • RULE_PDKV_MH_PIGEONPEA_SOW_NOW                                  │
│  • RULE_PDKV_MH_PIGEONPEA_WAIT                                     │
│                                                                     │
│  NO VALIDATED RULE → advisory_text = null (strict null safety)     │
│  Output: Structured Advisory Result (is_operational = false)        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│              FARMER COMMUNICATION LAYER (Phase 1 — Mocked)         │
│                                                                     │
│  Severity-Based Routing (config/communication.yaml):               │
│  • NORMAL     → SMS only                                           │
│  • IMPORTANT  → SMS + WhatsApp                                     │
│  • HIGH_RISK  → Voice Call + SMS (with retry & fallback)           │
│                                                                     │
│  Voice Fallback Protocol:                                          │
│  Attempt 1 → NO_ANSWER → Attempt 2 → NO_ANSWER → Fallback SMS     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Database Schema (ORM Entities)

```
┌────────────────┐         ┌────────────────┐
│     Block      │ 1────── │    Village     │
│ ─────────────  │         │ ─────────────  │
│ id (PK)        │         │ id (PK)        │
│ block_name     │         │ village_name   │
│ district       │         │ pin_code       │
│ state          │         │ block_id (FK)  │
│ latitude       │         └───────┬────────┘
│ longitude      │                 │
└────────┬───────┘                 │
         │                         │
         │        ┌────────────────▼───────┐
         │        │       Farmer            │
         │        │ ──────────────────────  │
         │        │ id (PK)                │
         │        │ phone_masked           │ (privacy)
         │        │ language               │
         │        │ village_id (FK)        │
         │        │ crop_id (FK)           │
         │        │ consent_given          │
         │        │ is_active              │
         │        └───────────┬────────────┘
         │                    │
         ├── WeatherData ◄─── │ (block_id FK)
         │   (daily rainfall) │
         │                    │
         ├── RegistrationSession ◄─── (phone, state machine)
         │
         ├── FarmerObservation ◄─── (RAIN/DRY/HEAVY_RAIN crowd data)
         │
         └── AlertLog ◄─── (dispatched alerts, channel, severity, status)

┌────────────────┐
│      Crop      │
│ ─────────────  │
│ id (PK)        │
│ crop_name      │
│ crop_type      │
│ kharif_season  │
└────────────────┘
```

---

## 7. API Endpoint Catalogue

### Core Data APIs
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health check |
| `GET` | `/api/blocks` | List all blocks |
| `GET` | `/api/villages` | List villages (filter by PIN) |
| `GET` | `/api/crops` | Kharif crop catalog |
| `GET/POST` | `/api/farmers` | Farmer CRUD |
| `POST` | `/api/registration` | SMS state machine step |
| `POST` | `/api/observations` | Submit farmer crowd-truth |
| `POST` | `/api/alerts` | Dispatch severity alert |
| `GET` | `/api/weather` | Block weather data |

### Historical Pipeline APIs
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/historical/summary` | Dataset stats overview |
| `GET` | `/api/historical/events` | Filter by block/type/date |
| `GET` | `/api/historical/{block_id}` | Block rainfall + events |
| `POST` | `/api/historical/process` | Trigger ingestion pipeline |

### ML / Prediction APIs
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/prediction-dataset/summary` | Dataset metrics & class balance |
| `GET` | `/api/prediction-dataset/{block_id}` | Block prediction rows |
| `GET` | `/api/forecast/{block_id}/false-onset` | Raw probability output |
| `GET` | `/api/forecast/{block_id}/false-onset/decision` | Sowing posture |
| `GET` | `/api/forecast/baseline-summary` | Full model evaluation & calibration |

### Advisory APIs
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/advisory/{block_id}?crop_id=&language=` | Crop-specific advisory |
| `GET` | `/api/advisory/rules` | Query rule registry |

### Validation & Science APIs
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/validation/*` | Multi-year validation results |
| `GET` | `/api/calibration/*` | Probability calibration status |
| `GET` | `/api/rolling-origin/*` | Rolling-origin CV results |
| `GET` | `/api/demo/*` | End-to-end SIH demo scenarios |

---

## 8. ML Model Artifact Registry

| Artifact | Purpose | Status |
|---|---|---|
| `false_onset_7d_logistic.joblib` | Chronological holdout baseline | `INSUFFICIENT_EVENT_VARIATION` |
| `false_onset_7d_logistic_metadata.json` | Chronological metadata | Active |
| `false_onset_7d_logistic_diagnostic.joblib` | Diagnostic (full-year) evaluation | ROC-AUC: 0.9931 |
| `false_onset_7d_logistic_diagnostic_metadata.json` | Diagnostic metadata | Active |
| `false_onset_7d_calibrated.joblib` | Platt-calibrated model | `INSUFFICIENT_CALIBRATION_DATA` |
| `false_onset_7d_calibrated_metadata.json` | Calibration metadata | Active |

---

## 9. Event Detection Logic

| Event | Detection Rule | Config Key |
|---|---|---|
| **Onset Trigger** | 3-day cumulative rainfall ≥ 20 mm, 30-day lockout debounce | `onset_trigger_mm`, `onset_lockout_days` |
| **False Onset** | Onset trigger followed by ≥ 7 dry days within 30 days | `false_onset_dry_days` |
| **Break Spell** | ≥ 5 consecutive days with rainfall < 2.5 mm (unique episode IDs) | `break_min_days`, `break_max_rain_mm` |
| **Heavy Rain** | Daily rainfall ≥ 64.5 mm | `heavy_rain_threshold_mm` |
| **Revival** | ≥ 15 mm over 2 days after a break spell | `revival_threshold_mm`, `revival_days` |

---

## 10. SMS Registration State Machine

```
   Farmer sends "MEGH"
          │
          ▼
   [STATE: LANGUAGE_SELECTION]
   "Reply 1:Hindi 2:Marathi 3:Kannada 4:English"
          │  Farmer replies "1"
          ▼
   [STATE: PIN_ENTRY]
   "Enter your 6-digit PIN code"
          │  Farmer replies "441001"
          ▼
   [STATE: VILLAGE_SELECTION]
   "1. Nagpur Rural  2. Kamptee  3. Hingna"
          │  Farmer replies "2"
          ▼
   [STATE: CROP_SELECTION]
   "1. Soybean  2. Cotton  3. Pigeonpea  4. Maize"
          │  Farmer replies "1"
          ▼
   [STATE: CONSENT]
   "Reply YES to activate your Meghvani alerts"
          │  Farmer replies "YES"
          ▼
   [STATE: ACTIVE]
   Profile created, Village → Block auto-mapped
   Confirmation sent in selected language
```

---

## 11. Alert Severity Routing Matrix

| Severity | Channels | Retry Policy |
|---|---|---|
| `NORMAL` | SMS only | 1 attempt |
| `IMPORTANT` | SMS + WhatsApp | 1 attempt each |
| `HIGH_RISK` | Voice Call → retry → Fallback SMS | Attempt 1 → wait → Attempt 2 → SMS fallback |

---

## 12. Advisory Rule Validation Hierarchy

```
VALIDATED ✅   → Can match and produce farmer-facing advisory text
               → Must have: institution, publication, version, date, rule_id
               → Examples: ICAR-CRIDA, ICAR-CICR, Dr. PDKV, MahaAgri

REVIEW_REQUIRED ⏳ → Blocked from farmer dispatch until KVK sign-off
               → Examples: intercropping posture rules

UNVALIDATED ❌  → Used for demonstrations only
               → Never produces agronomic recommendations

UNAVAILABLE 🚫  → No rule found for this crop + decision + language combo
               → advisory_text = null (strict null safety enforced)
```

---

## 13. Configuration Files Summary

| File | Purpose |
|---|---|
| `config/app.yaml` | App name, version, CORS origins |
| `config/event_thresholds.yaml` | Onset/break/heavy-rain thresholds + prediction horizons |
| `config/event_definitions.yaml` | Human-readable event type metadata |
| `config/crops.yaml` | Kharif crop catalog |
| `config/blocks.yaml` | Block spatial metadata |
| `config/communication.yaml` | Channel routing rules + voice retry delays |
| `config/advisory_rules.yaml` | Demo advisory rules (all UNVALIDATED) |
| `config/agronomic_rules.yaml` | Full 11-rule registry (6 VALIDATED, 2 REVIEW, 3 DEMO) |
| `config/agronomic_sources.yaml` | Source institution register |
| `config/decision_costs.yaml` | Decision cost weights for economic analysis |

---

## 14. Testing Strategy

### Total: 166 / 166 Tests PASSED

| Phase | Tests | Coverage |
|---|---|---|
| **Phase 1** (Foundation) | 25 | DB models, PIN resolution, SMS state machine, mock alerts, voice fallback |
| **Phase 2 & 2.1** (Historical) | 29 | CSV loading, validation, rolling features, onset debounce, break episodes |
| **Phase 3A** (Feature Engineering) | 19 | Horizon boundaries, causal features, block isolation, temporal split, leakage audit |
| **Phase 3B & 3B.1** (Baseline ML) | 24 | Climatology, logistic baseline, evaluation status, artifact separation |
| **Phase 4A** (Calibration) | 15 | Dual probability, synthetic range, temporal precedence, artifact isolation |
| **Phase 4B** (Decision Engine) | 20 | All threshold boundaries, reason codes, null/NaN/invalid handling |
| **Phase 5A** (Advisory Framework) | 20 | Registry lookups, null safety, no unauthorized advisory text |
| **Phase 5B** (Source Rules) | 14 | Source metadata integrity, VALIDATED matching, YAML validation |

---

## 15. Scientific Boundaries & Current Limitations

> [!WARNING]
> **Single-Year Dataset Constraint**
> All ML evaluation metrics are prototype demonstrations on a single 2025 calendar year.
> Multi-year out-of-sample validation is architecturally required before operational use.

| Limitation | Status |
|---|---|
| Real SMS / WhatsApp / Voice dispatch | ❌ Mocked in Phase 1 |
| Real IMD / satellite rainfall data | ❌ Demo CSV only |
| Complex ML models (RF, LightGBM, LSTM) | ❌ Not yet implemented |
| Multi-year validation | ❌ Architectural requirement |
| REVIEW_REQUIRED rules dispatch | ❌ Blocked pending KVK sign-off |
| Operational forecast status | ❌ `is_operational: false` enforced everywhere |

---

## 16. Deployment Architecture

```
                    ┌──────────────────────────────────┐
                    │         Docker Compose            │
                    │                                  │
                    │  ┌──────────┐  ┌──────────────┐  │
                    │  │ Backend  │  │   Frontend   │  │
                    │  │ FastAPI  │  │  React/Vite  │  │
                    │  │ :8000    │  │  :5173/:80   │  │
                    │  └────┬─────┘  └──────────────┘  │
                    │       │                           │
                    │  ┌────▼──────────────────────┐    │
                    │  │  SQLite (dev) / PostgreSQL │    │
                    │  │  + PostGIS (production)   │    │
                    │  └───────────────────────────┘    │
                    └──────────────────────────────────┘

  Development:  uvicorn app.main:app --app-dir backend --reload --port 8000
  Frontend Dev: cd frontend && npm run dev          → http://localhost:5173
  Full Stack:   docker-compose up --build
  Swagger UI:   http://localhost:8000/docs
```

---

## 17. Development Phases Roadmap

```
Phase 1  ✅ Foundation: FastAPI, ORM, SMS state machine, mock communication
Phase 2  ✅ Historical Rainfall Pipeline & Event Detection Engine
Phase 2.1✅ Label Quality: Onset debounce, break episode IDs
Phase 3A ✅ Predictive Feature & Target Engineering (zero leakage)
Phase 3B ✅ First Probabilistic Baseline (Logistic Regression)
Phase 3B.1✅ Evaluation Integrity Fix (INSUFFICIENT_EVENT_VARIATION)
Phase 4A ✅ Probability Calibration Framework (Platt scaling)
Phase 4B ✅ Prototype Decision Layer (SOW_NOW / SOW_PART_NOW / WAIT)
Phase 5A ✅ Advisory Rule Framework (strict null safety, source traceability)
Phase 5B ✅ Sourced Agronomic Rule Registration (6 VALIDATED rules)
Phase 5C 🔄 Hyperlocal Rule Contextualization & Controlled Pilot Communications
Phase 6A ✅ Communication Simulation
Phase 6B ✅ Farmer Observations Feedback Loop
Phase 7A ✅ End-to-End Demo & Architecture Review
Phase 7B ✅ Scientific Validation & Data Provenance
Phase 7C ✅ Multi-year Validation Architecture
Phase 8A ✅ Calibration Methodology & Evaluation
Phase 8B ✅ In-Season Evaluation & Label Sensitivity
Phase 9  🔲 Advanced Models (Random Forest / LightGBM / LSTM)
Phase 10 🔲 Real IMD Data Integration & Operational Deployment
```

---

*Generated from Meghvani codebase — Smart India Hackathon 2026 Prototype*  
*Architecture covers: 17 API routers · 9 ORM models · 18 ML features · 5 event types · 6 validated agronomic rules · 166 automated tests*
