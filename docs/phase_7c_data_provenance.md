# Meghvani Phase 7C: IMD Historical Rainfall Data Provenance & Verification

## 1. Primary Source & Dataset Identification

| Field | Official Specification |
| :--- | :--- |
| **Provider** | India Meteorological Department (IMD), Ministry of Earth Sciences, Government of India |
| **Dataset Name** | IMD New High Spatial Resolution 0.25° × 0.25° Long Period Daily Gridded Rainfall Dataset Over India |
| **Coverage Period** | 1901 – 2024 |
| **Official Portal URL** | [https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html](https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html) |
| **Variable** | Daily rainfall accumulation (`RAINFALL`) |
| **Unit** | Millimetres (`mm`) |
| **Format** | Classic NetCDF-3 (`CDF\x01`) binary format |
| **Grid Extent** | Latitude: 6.5°N – 38.5°N (129 points at 0.25° step)<br>Longitude: 66.5°E – 100.0°E (135 points at 0.25° step) |
| **Dimensions** | `('TIME', 'LATITUDE', 'LONGITUDE')` |
| **Temporal Origin** | `days since 1900-12-31 00:00:00` |
| **Missing Value Convention** | `-999.0` (flagged as masked / no observation; never treated as 0.0 mm) |
| **Physical Limits** | $0.0\text{ mm} \le \text{Rainfall} \le 1500.0\text{ mm}$ |

---

## 2. Ingested Raw Files & Cryptographic Audit

All 6 official IMD files have been deposited into `data/raw/historical/imd/` and verified with SHA-256 hashes:

| File Name | Calendar Year | File Size (Bytes) | Number of Days | Leap Year? | SHA-256 Checksum |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `RF25_ind2019_rfp25.nc` | **2019** | 25,431,832 | 365 (Jan 1 – Dec 31) | No | `c551c563b3514d492a2de94c706c1c254d5826656738b4a8e7dbd83841344a5b` |
| `RF25_ind2020_rfp25.nc` | **2020** | 25,501,500 | 366 (Jan 1 – Dec 31) | Yes (Leap) | `2e567f0f71f3a1936ba11d61a0214fc3927c7b969ee5669d14959aa0b6b026dc` |
| `RF25_ind2021_rfp25.nc` | **2021** | 25,431,832 | 365 (Jan 1 – Dec 31) | No | `fb0f291fa7e214a7811023a9309cead67233b6b4e0bfcc5b277643f976f68374` |
| `RF25_ind2022_rfp25.nc` | **2022** | 25,431,832 | 365 (Jan 1 – Dec 31) | No | `83ae0d4e48f3a408eec3b54844476d406faf70928dc13c79f0bd085e3b0224b8` |
| `RF25_ind2023_rfp25.nc` | **2023** | 25,431,832 | 365 (Jan 1 – Dec 31) | No | `1fa0cbcb56769fd3cd2702e36dc3ee1b81b74755b77c7f058c70dfc3afb82831` |
| `RF25_ind2024_rfp25.nc` | **2024** | 25,501,532 | 366 (Jan 1 – Dec 31) | Yes (Leap) | `1ef02aeba5694dbb57a6cca23a3c2cc11740affb185137c1eacbeab59893228a` |

---

## 3. Spatial Mapping to Meghvani Blocks

### Prototype Block Coordinates & Snapped IMD 0.25° Grid Centers

| Block ID | Block Name | District | State | Centroid Coordinates (Lat, Lon) | IMD Grid Center (Lat, Lon) | Grid Indices (lat_idx, lon_idx) | Distance / Deviation |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BLK001** | Nagpur Rural | Nagpur | Maharashtra | (21.1458, 79.0882) | **(21.25°N, 79.00°E)** | lat_idx=59, lon_idx=50 | 0.1365° (~15.15 km) |
| **BLK002** | Wardha East | Wardha | Maharashtra | (20.7453, 78.6022) | **(20.75°N, 78.50°E)** | lat_idx=57, lon_idx=48 | 0.1023° (~11.36 km) |
| **BLK003** | Amravati Central | Amravati | Maharashtra | (20.9374, 77.7796) | **(21.00°N, 77.75°E)** | lat_idx=58, lon_idx=45 | 0.0692° (~7.69 km) |

### Mapping Terminology Standard
Per scientific rules, this mapping is explicitly designated:
**"Prototype block representative-grid rainfall mapping"** (Method: `CENTROID_GRID_CELL`).
It is NOT labeled "block-average rainfall" because official administrative polygon boundaries have not yet been ingested for area-weighted integration (`BLOCK_GEOMETRY_REQUIRED`).

---

## 4. Derived Data Products

1. **`data/processed/historical/imd_data_quality_report.csv`**:
   Audit of all 6 raw NetCDF files: dimensions, physical range, leap years, missing value counts, and overall quality verification.
2. **`data/processed/historical/block_daily_rainfall.csv`**:
   Standardized block daily rainfall time series for 2019–2024 across BLK001, BLK002, and BLK003.
   Columns: `date, year, block_id, rainfall_mm, source, mapping_method, imd_lat, imd_lon`.
3. **`data/processed/historical/block_rainfall_quality.csv`**:
   Block-by-block and year-by-year quality analysis (min, max, mean, zero-rain days, valid days).
4. **`data/processed/historical/multiyear_event_summary.csv`**:
   Meteorological event detection counts across all 6 years using Phase 2.1 `EventDetector` heuristics.
5. **`data/processed/historical/multiyear_prediction_dataset.csv`**:
   Supervised prediction dataset for LOYO validation.
