# Meghvani — Agriculture & Weather Map UI Redesign Report

**Date:** October 3, 2026  
**System:** Meghvani — Hyperlocal Monsoon Intelligence  
**Phase:** Frontend Spatial Weather & Farm Decision Redesign  

---

## 1. What Changed (UX Hierarchy Paradigm Shift)

The user experience of the Meghvani dashboard was restructured from a number/card-heavy SaaS presentation to a **spatial weather intelligence and agricultural decision platform**:

$$\text{Numbers } \to \text{ Cards } \to \text{ Text} \quad \Longrightarrow \quad \mathbf{MAP} \to \mathbf{WEATHER} \to \mathbf{RISK} \to \mathbf{FARM\ DECISION}$$

The initial viewport now immediately answers three fundamental farmer and officer questions:
1. **"Where is rainfall occurring?"** — High-resolution Leaflet cartography depicting IMD 0.25° representative-grid cells.
2. **"Where is the monsoon risk?"** — Layer toggles visualizing calibrated false-onset probabilities across Vidarbha blocks.
3. **"What should the farmer do?"** — An authoritative, high-contrast Farm Decision panel placed directly beside the map (`SOW NOW`, `SOW PART NOW`, `WAIT`), explicitly distinguishing source-supported agronomy from engineering model outputs.

---

## 2. Interactive Map Implementation

- **Technology**: Leaflet cartography with custom SVG `divIcon` markers and CartoDB Positron / OSM base tiles.
- **Geographic Focus**: Centered on the Vidarbha prototype blocks:
  - **Nagpur Rural** (`BLK001`): Centroid $(21.1458^\circ\text{N}, 79.0882^\circ\text{E})$, snapped IMD grid $(21.25^\circ\text{N}, 79.00^\circ\text{E})$
  - **Wardha East** (`BLK002`): Centroid $(20.7453^\circ\text{N}, 78.6022^\circ\text{E})$, snapped IMD grid $(20.75^\circ\text{N}, 78.50^\circ\text{E})$
  - **Amravati Central** (`BLK003`): Centroid $(20.9374^\circ\text{N}, 77.7796^\circ\text{E})$, snapped IMD grid $(21.00^\circ\text{N}, 77.75^\circ\text{E})$
- **Spatial Grid Bounds**: Rendered exact $0.25^\circ \times 0.25^\circ$ geographic bounding rectangles ($[\text{lat} \pm 0.125^\circ, \text{lon} \pm 0.125^\circ]$) dynamically color-coded by the selected layer.
- **Interactive Block Popups**: Clicking a marker or cell opens an inspection card showing:
  - District & block name
  - Recent 7-day rainfall ($92.7\text{ mm}$)
  - False-onset risk percentage ($18\%$)
  - Dry break risk (`Data unavailable (Phase 8)`)
  - Heavy rain risk (`Data unavailable (Phase 8)`)
  - Sowing recommendation (`SOW NOW`)
  - IMD $0.25^\circ$ grid coordinates and data source citation.
- **Cartographic Disclosure**: Prominently displays:  
  `"IMD 0.25° representative-grid rainfall: Prototype centroid-to-grid mapping; block polygons are not currently integrated."`

---

## 3. Data Sources Used & API Endpoints Reused

All visual elements strictly ingest data from existing backend contracts without fabricating values:
- `GET /api/blocks`: Geocoded centroids for Vidarbha blocks.
- `GET /api/weather/{block_id}`: Daily rainfall observations, temperature, humidity, wind, and soil moisture.
- `GET /api/forecast/{block_code}/false-onset`: False-onset probability outputs ($p=0.18$).
- `GET /api/forecast/{block_code}/false-onset/decision`: Decision support results (`SOW_NOW`), reason codes, and thresholds.
- `GET /api/advisory/{block_code}`: Agronomic rule engine results matching ICAR-CRIDA, IISR, and VNMKV frameworks.
- `GET /api/validation/multiyear/spatial/report`: Nearest IMD 0.25° grid coordinates and distance metrics.

---

## 4. Map Layers Implemented

1. **🌧️ Rainfall**: Colored grid cells according to 7-day precipitation:
   - $< 25\text{ mm}$ (Light blue `#BFDBFE`)
   - $25\text{--}50\text{ mm}$ (Moderate blue `#60A5FA`)
   - $50\text{--}80\text{ mm}$ (Rain blue `#2563EB`)
   - $\ge 80\text{ mm}$ (Deep monsoon blue `#1E3A8A`)
2. **⚠️ False Onset Risk**:
   - $< 30\%$ (Low Risk / Green `#16A34A`)
   - $30\text{--}60\%$ (Moderate Caution / Amber `#F59E0B`)
   - $> 60\%$ (High Hazard / Red `#EF4444`)
3. **🌱 Farm Decision**:
   - `SOW NOW` (Green `#16A34A`)
   - `SOW PART NOW` (Amber `#F59E0B`)
   - `WAIT` (Red `#EF4444`)
4. **☀️ Dry Break Risk**: Honest fallback display: `Data unavailable (Phase 8)`.
5. **⛈️ Heavy Rain Risk**: Honest fallback display: `Data unavailable (Phase 8)`.

---

## 5. Weather Visualization & Timeline

1. **Recent Rainfall Bar Chart** (`RecentRainfallChart.tsx`):
   - Interactive SVG bar chart showing daily rainfall sequences for up to 14 days.
   - Real meteorological indicators computed directly from backend observations:
     - Cumulative Rainfall ($\text{mm}$)
     - Rainy Days ($\ge 2.5\text{ mm}$, IMD official meteorological standard)
     - Maximum 24h Rainfall ($\text{mm}$)
     - Daily Mean Rainfall ($\text{mm}$)
2. **Weather Timeline Strip** (`RainfallOutlook.tsx`):
   - Horizontal weather forecast strip with day names (`SAT`, `SUN`, `MON`, etc.), dates, weather icons, millimeter amounts, and intensity categories (`Heavy Rain`, `Moderate Rain`, `Light Showers`, `Dry/Clear`).
   - Horizon selector supporting 7D, 14D, 21D, and 30D intervals.
3. **Monsoon Narrative** (`MonsoonStory.tsx`):
   - Answers *"What is happening?"* with 4 structured natural-language perspectives:
     - **Rainfall**: Adequate cumulative moisture satisfying seedbed criteria.
     - **Risk**: Low false-onset probability ($18\%$) below the $40\%$ threshold.
     - **Farm Action**: Validated recommendation supporting timely sowing with Broad Bed Furrow moisture conservation.
     - **Watch**: 14–21 day vegetative dry spell monitoring protocol.

---

## 6. Farm Decision Panel & Boundary Separation

Placed side-by-side with the Leaflet map on desktop:
- **Decision Hero**: Prominent badge (`SOW NOW`, `SOW PART NOW`, `WAIT`) with risk percentage and 7-day horizon.
- **Crop Selector**: Rapid toggling between Soybean, Cotton, and Pigeonpea (Tur).
- **Why? Rationale Checklist**: Verified moisture receipt, risk below threshold, validated rule availability.
- **Agronomic vs. Engineering Separation**:
  - *Source-Supported Agronomic Condition*: ICAR-CRIDA Nagpur Contingency Plan (75–100 mm seedbed moisture requirement).
  - *Meghvani Engineering Condition*: Statistical false-onset risk calculated from precipitation sequences.

---

## 7. Unavailable-Data Handling & Scientific Integrity Safeguards

- **No Fabricated Radar/Weather**: When observation data is missing or horizons are unpopulated, the UI explicitly renders `Forecast unavailable for this block` or `Data unavailable`.
- **Terminology Cleanliness**: Wording like *"Monsoon onset confirmed"* has been replaced with *"Onset indicator satisfied"* or *"Prototype onset trigger"*.
- **Clear Disclosures**:
  - `HISTORICAL REPLAY · RESEARCH BENCHMARK · NOT OPERATIONAL`
  - `SIMULATED — NO REAL MESSAGING SENT`
  - ROC AUC is strictly labeled as a discrimination metric and never described as "accuracy".

---

## 8. Responsive Design

- **Desktop ($\ge 1024\text{px}$)**: Map ($65\%$ width) and Farm Decision Panel ($35\%$ width) side-by-side in the hero viewport, followed by horizontal weather strips, charts, and 3-column crop advisory cards.
- **Tablet ($640\text{px} - 1023\text{px}$)**: Map on top ($420\text{px}$ height), Farm Decision Panel directly underneath, 2-column crop cards.
- **Mobile ($< 640\text{px}$)**: Single-column mobile-first flow: Compact hero $\to$ Leaflet map with touch controls $\to$ Decision panel $\to$ Horizontal scrollable weather timeline $\to$ Daily rain chart $\to$ Advisory cards $\to$ Simulated smartphone message card.

---

## 9. Tests and Build Results

### Backend Pytest Suite
```
Command: backend\venv\Scripts\python.exe -m pytest -q
Results: 321 passed, 6 warnings in 19.90s
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

### Frontend Production Build
```
Command: npm run build (in frontend/)
Output:
> meghvani-frontend@1.0.0 build
> tsc && vite build
vite v5.4.21 building for production...
✓ 1531 modules transformed.
dist/index.html                   1.48 kB │ gzip:   0.87 kB
dist/assets/index-CTrGdWpH.css   76.27 kB │ gzip:  16.84 kB
dist/assets/index-Cdjbj1FH.js   589.36 kB │ gzip: 147.52 kB
✓ built in 11.36s
Exit Code: 0
```
