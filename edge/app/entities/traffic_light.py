from datetime import datetime
from pydantic import BaseModel, field_validator


class TrafficLightData(BaseModel):
    traffic_light_id: int
    timestamp: datetime
    cars_waiting: int
    longitude: float
    latitude: float

    @classmethod
    @field_validator("timestamp", mode="before")
    def parse_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )

