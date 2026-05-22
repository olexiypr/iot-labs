"""
Generate a CSV file with random air quality data matching the AqSchema:
    co2_level  - Int (ppm, realistic range: 300–2000)
    temperature - Int (°C, realistic range: -10–45)
    pm2_5      - Int (µg/m³, realistic range: 0–500)
    pm10       - Int (µg/m³, realistic range: 0–600)
"""

import csv
import os
import random

# Configuration
NUM_ROWS = 1000
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "src", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "aq.csv")

# Realistic value ranges
CO2_LEVEL_RANGE = (300, 2000)      # ppm
TEMPERATURE_RANGE = (20, 25)      # °C
PM2_5_RANGE = (0, 500)             # µg/m³
PM10_RANGE = (0, 600)              # µg/m³


def generate_row():
    """Generate a single row of random air quality data."""
    return {
        "co2_level": random.randint(*CO2_LEVEL_RANGE),
        "temperature": random.uniform(*TEMPERATURE_RANGE),
        "pm2_5": random.randint(*PM2_5_RANGE),
        "pm10": random.randint(*PM10_RANGE),
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["co2_level", "temperature", "pm2_5", "pm10"])
        writer.writeheader()
        for _ in range(NUM_ROWS):
            writer.writerow(generate_row())

    print(f"Generated {NUM_ROWS} rows → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
