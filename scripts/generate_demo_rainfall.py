"""
Script to generate demo historical daily rainfall data for Meghvani Phase 2.
Source is explicitly marked as DEMO_DATA.
"""
import csv
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "rainfall"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = DATA_DIR / "demo_rainfall.csv"

def generate_demo_dataset():
    records = []
    start_date = date(2025, 6, 1)
    end_date = date(2025, 9, 30)
    total_days = (end_date - start_date).days + 1

    # Block 1 (BLK001): Normal onset, Break spell, Revival, Heavy rain
    for i in range(total_days):
        current_date = start_date + timedelta(days=i)
        d_str = current_date.isoformat()
        
        # Scenario engineering:
        # June 1-7: Pre-monsoon dry/light showers
        if i < 7:
            rain = 0.0 if i in [0, 1, 3, 5] else 1.2
        # June 8-10: Onset trigger (6.0 + 9.5 + 12.0 = 27.5mm > 20mm)
        elif i == 7: # June 8
            rain = 6.0
        elif i == 8: # June 9
            rain = 9.5
        elif i == 9: # June 10
            rain = 12.0
        # June 11 - July 4: Active monsoon
        elif i < 34:
            pattern = [8.5, 14.0, 3.2, 0.5, 18.0, 6.4, 0.0, 11.2, 5.0]
            rain = pattern[(i - 10) % len(pattern)]
        # July 5-13 (i = 34 to 42): Break spell (9 consecutive dry days <= 2.0mm)
        elif 34 <= i <= 42:
            rain = 0.0 if i % 2 == 0 else 0.8
        # July 14-15 (i = 43, 44): Revival event (10.0 + 12.5 = 22.5mm >= 15mm in 2 days)
        elif i == 43:
            rain = 10.0
        elif i == 44:
            rain = 12.5
        # July 16 - August 1: Active rain
        elif i < 62:
            rain = 7.5 if i % 2 == 0 else 15.0
        # August 2 (i = 62): Heavy rain event (74.5mm >= 64.5mm)
        elif i == 62:
            rain = 74.5
        # August 3 - September 30: Regular showers & receding monsoon
        else:
            pattern = [4.0, 12.0, 0.0, 2.5, 16.5, 0.0, 5.5, 8.0, 0.0]
            rain = pattern[(i - 63) % len(pattern)]

        records.append({
            "block_id": "BLK001",
            "date": d_str,
            "rainfall_mm": round(rain, 1),
            "source": "DEMO_DATA"
        })

    # Block 2 (BLK002): False Onset scenario (onset followed by >=7 consecutive dry days)
    for i in range(total_days):
        current_date = start_date + timedelta(days=i)
        d_str = current_date.isoformat()

        # June 1-4: Dry
        if i < 4:
            rain = 0.0
        # June 5-7 (i = 4, 5, 6): Apparent onset trigger (7.0 + 8.5 + 11.0 = 26.5mm >= 20mm)
        elif i == 4:
            rain = 7.0
        elif i == 5:
            rain = 8.5
        elif i == 6:
            rain = 11.0
        # June 8-16 (i = 7 to 15): 9 consecutive dry days (0.0 to 1.0mm) -> FALSE ONSET triggered!
        elif 7 <= i <= 15:
            rain = 0.0 if i % 3 != 0 else 0.5
        # June 17-24: Scattered showers
        elif i < 24:
            rain = 3.5 if i % 2 == 0 else 1.0
        # June 25-27 (i = 24, 25, 26): Genuine delayed onset trigger (8.0 + 12.0 + 14.0 = 34.0mm)
        elif i == 24:
            rain = 8.0
        elif i == 25:
            rain = 12.0
        elif i == 26:
            rain = 14.0
        # June 28 - September 30: Active regular season
        else:
            pattern = [6.0, 0.0, 15.5, 4.0, 22.0, 1.5, 9.0, 0.0]
            rain = pattern[(i - 27) % len(pattern)]

        records.append({
            "block_id": "BLK002",
            "date": d_str,
            "rainfall_mm": round(rain, 1),
            "source": "DEMO_DATA"
        })

    # Block 3 (BLK003): Steady onset, Extreme Heavy Rain, Late break
    for i in range(total_days):
        current_date = start_date + timedelta(days=i)
        d_str = current_date.isoformat()

        # June 1-11: Dry/light
        if i < 11:
            rain = 0.0 if i % 2 == 0 else 1.5
        # June 12-14 (i = 11, 12, 13): Onset trigger (9.0 + 11.0 + 10.5 = 30.5mm)
        elif i == 11:
            rain = 9.0
        elif i == 12:
            rain = 11.0
        elif i == 13:
            rain = 10.5
        # July 20 (i = 49): Extreme Heavy rain (82.5mm >= 64.5mm)
        elif i == 49:
            rain = 82.5
        # August 10-16 (i = 70 to 76): 7 consecutive dry days (Break spell)
        elif 70 <= i <= 76:
            rain = 0.0
        # August 17-18: Revival (11.0 + 9.0 = 20.0mm >= 15mm)
        elif i == 77:
            rain = 11.0
        elif i == 78:
            rain = 9.0
        else:
            pattern = [7.0, 11.0, 3.5, 0.0, 14.0, 5.0, 2.0]
            rain = pattern[i % len(pattern)]

        records.append({
            "block_id": "BLK003",
            "date": d_str,
            "rainfall_mm": round(rain, 1),
            "source": "DEMO_DATA"
        })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["block_id", "date", "rainfall_mm", "source"])
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} records in {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_demo_dataset()
