from dataclasses import dataclass


@dataclass
class Aq:
    co2_level: int
    temperature: float
    pm2_5: int
    pm10: int
