from dataclasses import dataclass
from datetime import datetime


@dataclass
class TrafficLight:
    traffic_light_id: int
    timestamp: datetime
    cars_waiting: int
    longitude: float
    latitude: float

