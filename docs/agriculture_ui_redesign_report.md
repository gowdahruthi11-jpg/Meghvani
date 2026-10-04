# Meghvani — Agriculture-First UI Redesign Report

**Date:** October 3, 2026  
**System:** Meghvani — Hyperlocal Monsoon Intelligence  
**Phase:** Frontend Visual Experience Redesign (Agriculture-First)  

---

## 1. Design Philosophy

Meghvani is an **Agricultural + Monsoon + Weather Decision-Support Platform**, not a generic SaaS, cryptocurrency, cybersecurity, or dark AI control room dashboard. 

The visual identity directly reflects the realities of Indian agriculture in the Vidarbha region:
- **Palette**: Deep forest green (`#1B4332`), leaf green (`#2D6A4F`), warm off-white / very light cream background (`#FAF9F5`), rain/monsoon sky blue (`#0284c7` / `#1e3d59`), rich soil/earth tones (`#78350F`), clear amber for caution, and vivid crimson for high-risk alerts.
- **Card Aesthetics**: Crisp white cards (`#FFFFFF`) with restrained, soft drop-shadows (`box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)`), subtle border outlines (`border border-stone-200/80`), and rounded corners (`rounded-2xl` / `rounded-xl`). Heavy glassmorphism, neon glows, and dark mode control rooms have been systematically purged.
- **Atmosphere**: Clean, calm, natural, trustworthy, and credible for farmers, KVK extension officers, agricultural researchers, and SIH evaluators.
- **Data Integrity**: **No fabricated data**. Every forecast probability, rainfall millimeter, and crop advisory rendered in the interface originates strictly from the backend APIs. If an API returns missing or uncalibrated data, the UI displays explicit, honest empty states (`"Forecast unavailable for this block"`, `"Historical verification required"`) rather than synthetic mock numbers.

---

## 2. Pages Redesigned

All primary, extension, and research views were overhauled from the ground up:

| Page / Route | Primary Target Audience | Redesign Focus |
|---|---|---|
| **Landing & Dashboard** (`/`) | Farmers & Village Extension Workers | Centered entirely around the question: *"What is happening with rainfall and what should farmers do?"*. Features a high-contrast Farm Decision hero banner (`SOW NOW`, `SOW PART NOW`, `WAIT`), 7/14/21/30-day rainfall outlook with weather icons, interactive Vidarbha block risk map, crop cards (Soybean, Cotton, Pigeonpea), simulated multi-channel farmer message preview, and an accessible risk legend. |
| **SIH Demo** (`/sih-demo`) | Hackathon Evaluators & Jury | Re-architected as a 9-stage agricultural journey timeline (`Weather Data` → `Forecast` → `Risk` → `Farm Decision` → `Farmer Message` → `Delivery Sim` → `Farmer Observation` → `Validation` → `Officer View`). Clearly stamped with `HISTORICAL REPLAY · SIMULATION · NOT OPERATIONAL`. Supports interactive scenario testing ($p=0.20, 0.45, 0.70$) without fabricated endpoints. |
| **Scientific Validation** (`/scientific-validation`) | Agricultural Scientists & Reviewers | Transformed from a dark theme into an authoritative scientific research report. Retains every single IMD audit table (6,576 records, 2019–2024), LOYO cross-validation metrics, raw vs. calibrated Brier scores (isotonic regression), forward-chaining rolling-origin results (7D, 14D, 21D, 30D), and unvarnished reliability diagrams. Prominently displays: `RESEARCH BENCHMARK — NOT OPERATIONAL`. |
| **Farmer Registration & SMS** (`/farmer-register`) | Farmers & Field Animators | Mobile-first interactive feature phone / smartphone simulation with missed-call triggers, USSD simulation, conversational Marathi/Hindi/English registration, and live backend farmer database synchronization. |
| **Officer Dashboard** (`/officer-dashboard`) | KVK & District Agriculture Officers | Reorganized command console with block risk overview, crop advisory distribution charts, alert dispatch simulation modal (SMS/Voice/WhatsApp with fallback logging), and farmer ground observation verification table. |
| **Historical Analysis** (`/historical-analysis`) | Extension Specialists & Agronomists | Light-themed multi-year rainfall telemetry explorer featuring interactive block filters, SVG rainfall bar charts, and feature extraction statistics. |
| **System Status** (`/system-status`) | Technical Auditors & Engineers | Clean architectural overview tracking all 8 phases of development, sub-system health indicators, and operational safety boundaries. |

---

## 3. Components Created

Eight new modular, reusable components were created to establish Meghvani's agricultural design system:

1. **`AgricultureMetricCard.tsx`**:
   - Clean, light metric card with semantic agricultural color accents (`forest`, `leaf`, `rain`, `amber`, `rose`).
   - Supports trend indicators, status pills, and accessible micro-descriptions.
2. **`RainfallOutlook.tsx`**:
   - Horizon selector supporting 7-day, 14-day, 21-day, and 30-day outlooks.
   - Agriculture-friendly daily breakdown with cloud/rain/sun emojis (`🌧️`, `🌦️`, `⛅`, `☀️`), formatted dates, millimeter bars, and cumulative totals.
   - Honest empty states if observations are unavailable.
3. **`CropDecisionCard.tsx`**:
   - Dedicated agronomic decision cards for Vidarbha's core crops: Soybean (JS-335 / JS-9560), Cotton (Bt Hybrid), and Pigeonpea (BDN-711).
   - High-contrast decision badges (`SOW NOW`, `SOW PART NOW`, `WAIT`), rule codes (`RULE_ONSET_CONFIRMED_HIGH_CONFIDENCE`), institutional source status (ICAR / VNMKV), and moisture requirements.
4. **`BlockRiskMap.tsx`**:
   - Clean SVG spatial visualizer representing Vidarbha target blocks (Nagpur Rural, Wardha East, Amravati Central).
   - Layer toggles for False Onset Risk, Dry Break Risk, and Heavy Rain Risk with responsive hover tooltips and selection state.
5. **`FarmerMessageCard.tsx`**:
   - High-fidelity smartphone chassis preview displaying actual backend-generated advisory messages in Marathi (मराठी), Hindi (हिंदी), and English.
   - Simulation channel switcher (WhatsApp, SMS, IVR Voice call) with an indelible `SIMULATED` badge and audio playback preview.
6. **`RiskLegend.tsx`**:
   - Color-blind accessible semantic guide explaining agricultural meanings: Green (Favorable / Sow Now), Amber (Caution / Sow Part), Red (High Risk / Wait), Blue (Rainfall / Information), and Stone (Data Gap).
7. **`ScientificMetricCard.tsx`**:
   - Rigorous scientific card displaying calibration and discrimination metrics (ROC AUC, PR AUC, Raw Brier, Calibrated Brier, BSS, ECE).
   - Strictly labels whether a metric measures discrimination or probabilistic sharpness, preventing mischaracterization of ROC AUC as "accuracy".
8. **`DemoTimeline.tsx`**:
   - Visual 9-node interactive stepper for the SIH evaluation flow with active execution states, completed checkmarks, and milestone descriptions.

---

## 4. Components Modified

- **`Navbar.tsx`**:
  - Replaced dark header with deep forest green background (`bg-[#1B4332]`), warm wheat accents (`#FEF3C7`), and golden seed highlight badges.
  - Implemented intuitive navigation hierarchy: Primary agricultural items (`Dashboard`, `Monsoon Outlook`, `Risk Map`, `Crop Advisory`, `Farmer Mobile`, `Scientific Validation`, `SIH Demo`) alongside a structured `System` dropdown.
- **`Footer.tsx`**:
  - Converted to light agricultural styling with institutional attribution to IMD (0.25° gridded daily rainfall) and ICAR/VNMKV agronomic guidelines.
- **`App.tsx`**:
  - Unified root container styling using warm off-white (`bg-[#FAF9F5]`) and charcoal text (`text-stone-800`), eliminating all dark mode flicker and preserving route state.

---

## 5. Existing Features Preserved

Zero backend functionality, APIs, routes, or algorithms were altered:
- **Backend APIs**: All FastAPI routes (`/api/v1/forecast`, `/api/v1/advisory`, `/api/v1/farmers`, `/api/v1/alerts`, `/api/v1/validation`, `/api/v1/historical`, etc.) remain identical.
- **ML Logic & Thresholds**: False onset classification ($P > 0.40$), onset precipitation thresholds ($50\text{ mm}$ over 3 days), dry spell rules, and isotonic calibration formulas remain 100% untouched.
- **Agronomic Rules**: All 11 rules (6 VALIDATED, 2 REVIEW_REQUIRED, 3 UNVALIDATED) defined in `config/advisory_rules.yaml` continue driving recommendations without fabrication.
- **Scientific Integrity**:
  - Negative Brier Skill Scores are displayed transparently without masking.
  - ROC AUC is never labeled as "accuracy".
  - `is_operational = false` and `external_dispatch = false` remain strictly enforced.
- **Navigation Routes**: All tab keys (`landing`, `demo`, `validation`, `historical`, `prediction`, `baseline`, `register`, `alerts`, `observations`, `dashboard`, `status`) remain active.

---

## 6. Responsive Behavior

- **Mobile Viewports (< 640px)**:
  - Touch-friendly tap targets ($\ge 44\text{px}$).
  - Full-width decision cards with large typography.
  - Horizontal scrolling eliminated across all tables using responsive card wraps.
  - Collapsible navigation drawer.
- **Tablet Viewports (640px – 1024px)**:
  - 2-column balanced layouts for crop advisories and risk maps.
- **Desktop Viewports (> 1024px)**:
  - Spacious 3-column telemetry grids, multi-layer risk map displays, and side-by-side scientific validation tables.

---

## 7. Accessibility

- **Contrast Ratios**: Body text on warm cream exceeds WCAG AA ($> 4.5:1$); primary headers in deep forest green on cream exceed AAA ($> 7:1$).
- **Non-Color Dependence**: Every risk indicator pairs colors with text labels (`LOW RISK`, `MODERATE CAUTION`, `HIGH RISK`) and recognizable icons (`✅`, `⚠️`, `🛑`, `🌧️`, `🌱`).
- **Semantic HTML**: Proper `<h1>` through `<h3>` hierarchy on every view with accessible ARIA attributes and keyboard-focusable interactive elements.

---

## 8. Test & Verification Results

### Backend Pytest Suite
```
Command: backend\venv\Scripts\python.exe -m pytest -q
Results: 321 passed, 6 warnings in 25.48s
Exit Code: 0
```

### System Verification Script
```
Command: backend\venv\Scripts\python.exe scripts/verify_system.py
Results:
[OK] Blocks seeded: 3 blocks found.
[OK] PIN 441501 mapped: 2 villages found (Kalmeshwar, Mohpa).
[OK] Registration start -> Step: ALREADY_REGISTERED
[OK] Alert Dispatched across 4 log entries (Voice retry + SMS fallback verified).
[OK] Advisory Decision: SOW_NOW (RULE_ONSET_CONFIRMED_HIGH_CONFIDENCE)
ALL FOUNDATION SUBSYSTEMS VERIFIED SUCCESSFULLY!
Exit Code: 0
```

### Production Frontend Build
```
Command: npm run build (in frontend/)
Output:
> meghvani-frontend@1.0.0 build
> tsc && vite build
vite v5.4.21 building for production...
✓ 1526 modules transformed.
dist/index.html                   1.48 kB │ gzip:  0.87 kB
dist/assets/index-abwJkp-N.css   54.50 kB │ gzip:  9.41 kB
dist/assets/index-BDpl8IT3.js   423.43 kB │ gzip: 99.28 kB
✓ built in 4.39s
Exit Code: 0
```

---

## 9. Known UI Limitations

1. **Simulated Delivery Only**: Message delivery (SMS, WhatsApp, Voice IVR) is simulated on the frontend canvas; real external SMS gateways are intentionally disconnected by design.
2. **Prototype Geographic Scope**: The interactive SVG risk map covers the 3 prototype Vidarbha blocks (Nagpur Rural, Wardha East, Amravati Central). Additional blocks require IMD 0.25° coordinate grid mapping.
3. **Research Benchmark Notice**: Multi-year forecast calibration relies on the 2019–2024 IMD gridded dataset and must be treated as an agronomic benchmark rather than operational real-time NWP guidance.
