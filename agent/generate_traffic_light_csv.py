"""
Generate traffic_light.csv with 1000 rows.
Columns:
- traffic_light_id (1..5)
- timestamp (ISO 8601, 4-second steps shared across all lights)
- cars_waiting (int)
- longitude
- latitude
"""

import csv
import os
import random
from datetime import datetime, timedelta

# Configuration
NUM_ROWS = 1000
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "src", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "traffic_light.csv")

# Fixed traffic light coordinates (Kyiv-ish)
TRAFFIC_LIGHTS = {
    1: (30.523900, 50.450700),
    2: (30.524200, 50.450450),
    3: (30.524600, 50.450250),
    4: (30.523500, 50.450900),
    5: (30.524000, 50.450550),
}

CARS_WAITING_RANGE = (0, 20)


def generate_rows(start_time: datetime):
    timestamps_per_light = NUM_ROWS // len(TRAFFIC_LIGHTS)
    for i in range(timestamps_per_light):
        timestamp = start_time + timedelta(seconds=4 * i)
        for traffic_light_id, (longitude, latitude) in TRAFFIC_LIGHTS.items():
            yield {
                "traffic_light_id": traffic_light_id,
                "timestamp": timestamp.isoformat(timespec="seconds"),
                "cars_waiting": random.randint(*CARS_WAITING_RANGE),
                "longitude": f"{longitude:.6f}",
                "latitude": f"{latitude:.6f}",
            }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    start_time = datetime.now().replace(microsecond=0)

    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "traffic_light_id",
                "timestamp",
                "cars_waiting",
                "longitude",
                "latitude",
            ],
        )
        writer.writeheader()
        for row in generate_rows(start_time):
            writer.writerow(row)

    print(f"Generated {NUM_ROWS} rows -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

