# Meghvani Phase 6B: Farmer Observation, Validation & Feedback Loop

> **CRITICAL SCIENTIFIC INVARIANT**:  
> **"Farmer observations are collected as supplementary validation signals. They are not automatically treated as ground truth and are not automatically used to retrain or recalibrate the forecasting model."**  
> All submissions terminate in analytical storage and research verification. There is strictly **no automated ML model retraining pipeline** triggered by farmer feedback.

---

## 1. Objective

Phase 6B builds a structured, privacy-preserving crowd observation and verification feedback loop:

```text
Farmer receives advisory
        ↓
Local weather event occurs in field
        ↓
Farmer reports qualitative observation
        ↓
Observation stored in database (source = FARMER)
        ↓
Quality & duplicate checks
        ↓
Comparison with available reference rainfall
        ↓
Analytical validation & agreement calculation
        ↓
Officer & researcher audit dashboard
        ↓
Future calibration research dataset (offline only)
```

The system provides hyper-local ground-truth awareness across agricultural blocks without compromising model stability or introducing unvetted data into automated prediction pipelines.

---

## 2. Farmer Observation Flow

1. **Eligibility & Active Farmer Verification**:
   - The farmer must be registered in the system.
   - Farmer profile must be active (`farmer.active == True`).
   - Inactive farmer profiles are rejected with `OBSERVATION_NOT_AUTHORIZED` (HTTP 403).
2. **Qualitative Submission**:
   - The farmer selects their observed weather condition: `RAIN`, `DRY`, or `HEAVY_RAIN`.
   - Optional fields: crop, date (not far future), observation time, short note.
   - Source is permanently tagged as `FARMER`.
3. **Duplicate Prevention**:
   - A farmer submitting an identical event type on the same calendar date is suppressed (`status: DUPLICATE_OBSERVATION`) to prevent redundant records.
4. **Validation Comparison**:
   - The observation is automatically evaluated against available co-dated weather observations in the same block.
   - Status is classified into explicit, non-pejorative categories.
5. **No Dispatch / Retraining Boundary**:
   - Submissions **never** trigger SMS/WhatsApp alerts, modify ML artifacts, or alter model weights.

---

## 3. Observation Types

Phase 6B strictly restricts crowd feedback to three explicit event categories:

| Event Type | Visual Symbol | Definition | Reference Comparison |
| :--- | :---: | :--- | :--- |
| **`RAIN`** | 🌧 | Measurable precipitation experienced | Reference observed rainfall $> 0.0\text{ mm}$ |
| **`DRY`** | ☀ | Absence of rainfall / dry spell condition | Reference observed rainfall $\le 2.5\text{ mm}$ (dry ceiling) |
| **`HEAVY_RAIN`** | ⛈ | Intense precipitation / field ponding | Reference observed rainfall $\ge 64.5\text{ mm}$ (heavy benchmark) |

---

## 4. Data Model

Farmer observations are persisted in the single canonical `farmer_observations` table:

- `id` / `observation_id`: Unique primary key.
- `farmer_id`: Foreign key referencing `farmers.id`.
- `block_id`: Geographic block identifier.
- `village_id`: Village identifier (resolved from farmer profile if omitted).
- `observation_date`: Calendar date of the event.
- `observation_time`: Optional local time string (e.g. `"18:30"`).
- `observation_type`: `RAIN`, `DRY`, or `HEAVY_RAIN`.
- `value`: Optional numerical gauge reading (if farmer possesses an on-farm rain gauge).
- `crop_id`: Sown crop associated with observation.
- `notes`: Qualitative notes (bounded to 500 characters).
- `source`: Tagged as `"FARMER"`.
- `validation_status`: Analytical comparison status.
- `reference_rainfall_mm`: Co-dated reference rainfall recorded by weather station.
- `comparison_notes`: Detailed explanation of the comparison result.
- `created_at`: UTC timestamp.

*Note: Farmer PINs and unmasked telephone numbers are strictly excluded from observation tables and history endpoints.*

---

## 5. Validation Methodology

The `ObservationValidator` (`backend/app/observations/validation.py`) performs deterministic comparison against reference weather observations:

```text
Farmer Observation (Type, Block, Date)
                │
                ▼
Lookup WeatherObservation for (Block, Date)
                │
    ┌───────────┴───────────┐
    ▼                       ▼
Record Found         No Record Found
    │                       │
Evaluate Rules              ▼
    │               REFERENCE_DATA_UNAVAILABLE
    ├── RAIN: rainfall > 0 mm? ──► AGREEMENT / DISAGREEMENT
    ├── DRY: rainfall <= 2.5 mm? ──► AGREEMENT / DISAGREEMENT
    └── HEAVY_RAIN: rainfall >= 64.5 mm? ──► AGREEMENT / DISAGREEMENT
```

### Neutral Terminology
The system strictly enforces neutral terminology:
- `AGREEMENT`
- `DISAGREEMENT`
- `REFERENCE_DATA_UNAVAILABLE`
- `REFERENCE_THRESHOLD_UNAVAILABLE`
- `PENDING_REVIEW`

Terms such as *"wrong"*, *"fraud"*, *"false report"*, or *"unreliable"* are forbidden. A disagreement merely reflects physical variability between a farmer's field and the nearest automated weather station.

---

## 6. Reference Data Limitations

1. **Station Density**: Weather stations or demo gauges may be located kilometers away from the farmer's specific field.
2. **Missing Ingests**: Historical or current observations may not be available for every single calendar day, correctly yielding `REFERENCE_DATA_UNAVAILABLE`.
3. **Threshold Sensitivity**: Benchmark event thresholds (such as 64.5 mm for heavy rain) are prototype engineering guidelines, not rigid absolutes.

---

## 7. Spatial Limitations

- A block in Vidarbha covers hundreds of square kilometers and dozens of villages.
- Convective monsoon rainfall is notoriously patchy; convective cells often deposit 40 mm in one village while leaving an adjacent village 5 km away completely dry.
- Therefore, spatial comparison is inherently **approximate** and indicative, not an absolute ground-truth check.

---

## 8. Temporal Limitations

- Farmer observations reflect daytime or recent 24-hour experiences.
- Reference weather observations operate on daily 24-hour cycles.
- Comparison is strictly restricted to **same-date matching**; observations from different dates are never compared.

---

## 9. Agreement Metrics

Officers and researchers can monitor aggregate validation statistics via `GET /api/observations/summary`:

$$\text{Reference Agreement Rate} = \frac{\text{Agreements}}{\text{Agreements} + \text{Disagreements}}$$

- **Zero Denominator Protection**: If no reference comparisons exist ($\text{Agreements} + \text{Disagreements} = 0$), `agreement_rate` returns `null` rather than generating a divide-by-zero error.
- **Analytical Label**: Described as *"agreement with available reference observations"*, never as farmer "accuracy".
- **Farmer Reliability**: Aggregate summaries for individual farmers are computed solely as analytical statistics and are **never used for punitive farmer ranking or scoring**.

---

## 10. Privacy & Data Protection

- **Phone Number Masking**: Officer history endpoints mask phone numbers as `******1234`.
- **Zero PIN Exposure**: Farmer PINs are never accepted, stored, or returned in observation endpoints.
- **Selective Data Collection**: Only weather-relevant attributes are gathered.

---

## 11. No Automatic Retraining Invariant

```text
FARMER OBSERVATION
        ↓
DATABASE STORAGE
        ↓
ANALYTICAL VALIDATION
        ↓
RESEARCH AUDIT LOG
        ↓
    [ STOP ]
```

- Submitting an observation **does not**:
  - Execute ML training scripts (`train_false_onset_baseline.py`).
  - Modify serialized model weights or preprocessors (`ml/models/`).
  - Alter calibration curves or threshold boundaries.
  - Dispatch communication alerts.

---

## 12. Future Calibration Use

Observations are periodically exported to:
`data/processed/farmer_observation_validation.csv`

This export is intended for **offline agricultural research and post-season validation analysis**. It is explicitly disconnected from real-time operational inference and supervised model retraining.

---

## 13. Current Prototype Limitations

1. **Prototype Thresholds**: Heavy rain (64.5 mm) and dry ceiling (2.5 mm) thresholds are loaded from external configuration and are subject to local agronomic calibration.
2. **Reference Data Source**: Currently compares against the local `weather_observations` database table and demo observations; live IMD radar/satellite grid feeds are not connected.
3. **Operational State**: The entire subsystem operates under `is_operational = false`.
