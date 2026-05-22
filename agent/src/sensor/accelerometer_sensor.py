from __future__ import annotations

import csv
import os
from typing import Dict, Optional

from .base_sensor import BaseSensor


class AccelerometerSensor(BaseSensor[Dict[str, int], Dict[str, int]]):
    def __init__(self, csv_path: Optional[str] = None) -> None:
        if csv_path is None:
            base_dir = os.path.dirname(__file__)
            csv_path = os.path.join(base_dir, "..", "data", "accelerometer.csv")
        self._csv_path = os.path.normpath(csv_path)
        self._file = None
        self._reader = None

    def _open_reader(self) -> None:
        if self._file:
            self._file.close()
        self._file = open(self._csv_path, newline="", encoding="utf-8")
        self._reader = csv.DictReader(self._file)

    def get_sensor_data(self) -> Dict[str, int]:
        if self._reader is None:
            self._open_reader()
        try:
            row = next(self._reader)
        except StopIteration:
            self._open_reader()
            row = next(self._reader)
        return {
            "x": int(row["x"]),
            "y": int(row["y"]),
            "z": int(row["z"]),
        }

    def close(self) -> None:
        if self._file:
            self._file.close()
            self._file = None
            self._reader = None

