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

## 9. Current Limitations & Intentionally Unimplemented Items
In strict compliance with the Phase 1 specification:
- Real-time rainfall forecasting is **not connected**.
- Real telco SMS/WhatsApp/Voice APIs are **mocked**.
- Weather data represents sample **DEMO DATA**.
- Historical event detection (IMD NetCDF processing) is reserved for **Phase 2**.
- ML model training & probability calibration are reserved for **Phases 3–5**.
- Automated model retraining from farmer crowd feedback is intentionally disabled.

---

## 10. Next Phases (SIH 2026 Progression)
- **Phase 2**: Historical rainfall processing and event detection
- **Phase 3**: Feature engineering and baseline forecasting
- **Phase 4**: Onset / false-onset / break / heavy-rain probabilistic models
- **Phase 5**: Calibration and skill evaluation
- **Phase 6**: Sow Now / Sow Part Now / Wait engine
- **Phase 7**: Crop-specific advisory engine
- **Phase 8**: Risk maps and officer dashboard
- **Phase 9**: Farmer communication providers
- **Phase 10**: Historical replay, validation, and SIH demonstration
