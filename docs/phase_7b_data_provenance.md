# Meghvani Phase 7B: Historical Data Provenance & Verification Record

## 1. Provenance Integrity Statement
In compliance with Phase 7B Scientific Rules:
- No synthetic or fabricated multi-year datasets have been manufactured.
- No URLs, digital object identifiers (DOIs), or institutional providers have been invented.
- Datasets not verified through an immutable cryptographic hash and institutional source are marked:
  **`SOURCE_VERIFICATION_REQUIRED`** or **`DEMO_DATA_ONLY`**.

---

## 2. Currently Ingested Datasets

### Dataset Record 1: Prototype Demo Rainfall (2025)

| Field | Record Details |
| :--- | :--- |
| **Dataset Name** | `demo_rainfall.csv` |
| **Provider** | Meghvani Prototype Seed Repository |
| **Source Reference / URL** | `data/raw/rainfall/demo_rainfall.csv` (local repository file) |
| **Verification Status** | **`DEMO_DATA_ONLY`** (Unverified for scientific climatological claims) |
| **Calendar Years Used** | **2025 only** |
| **Spatial Coverage** | 3 prototype blocks (`BLK001`, `BLK002`, `BLK003`) located in Vidarbha, Maharashtra |
| **Temporal Resolution** | Daily observations (122 calendar days: June 1, 2025 – September 30, 2025) |
| **Total Record Count** | 366 rows (122 days × 3 blocks) |
| **Variable & Units** | Daily cumulative precipitation in millimeters (`rainfall_mm`) |
| **Preprocessing Applied** | Validated via `RainfallValidator`: non-negative check, missing value imputation flag, and format coercion. |
| **Missing-Data Handling** | No missing dates in 2025 demo set. Pipeline handles missing observations by flagging `data_quality_flag = SUSPECT_OR_INVALID` and excluding them from rolling antecedent sums without fabricating synthetic rainfall. |
| **Known Scientific Limitations** | Single season only. Extremely low false-onset prevalence ($n=6$, all in early June 2025). Chronological holdout has 0 positive events. Inadequate for operational multi-year skill evaluation. |

---

## 3. External Multi-Year Data Requirements & Ingestion Schema

To transition Meghvani's multi-year validation status from **`BLOCKED_PENDING_MULTIYEAR_DATA`** to **`READY`**, the following verified institutional datasets must be deposited into `data/raw/historical/`:

### Required Specification for External Ground Truth Data

1. **Target Historical Coverage**:
   - Minimum: 5 consecutive monsoon seasons (e.g., 2019, 2020, 2021, 2022, 2023, 2024).
   - Season Duration: June 1 to September 30 (minimum 122 days per year per block).
2. **Acceptable Institutional Providers**:
   - **India Meteorological Department (IMD)**: High-resolution daily gridded rainfall ($0.25^\circ \times 0.25^\circ$).
   - **ECMWF ERA5 / ERA5-Land**: Reanalysis precipitation (daily accumulated total).
   - **State Agriculture Department / Mahavedh**: Block-level Automatic Weather Station (AWS) network observations.
3. **Mandatory Ingestion Fields**:
   - `block_id`: Unique identifier matching target sub-districts (e.g., `BLK001` or Census block code).
   - `date`: ISO-8601 calendar date (`YYYY-MM-DD`).
   - `rainfall_mm`: Total 24-hour rainfall in millimeters ($08:30\text{ IST}$ to $08:30\text{ IST}$).
   - `source`: Identifier string referencing the exact institutional file release.
4. **Ingestion Directory Hierarchy**:
   ```
   data/
   ├── raw/
   │   └── historical/        <- Raw CSV / NetCDF / GeoTIFF imports with sha256 checksums
   ├── interim/
   │   └── historical/        <- Standardized daily block-aggregated CSVs
   └── processed/
       └── historical/        <- Feature-engineered and event-labeled datasets
   ```
5. **Verification Requirement**:
   - Every file placed in `data/raw/historical/` must be accompanied by a JSON metadata descriptor declaring provider, publication year, spatial resolution, and SHA-256 hash.
   - Any unverified external file will retain the tag `SOURCE_VERIFICATION_REQUIRED`.
