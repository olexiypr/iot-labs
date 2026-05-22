from dataclasses import dataclass

from datetime import datetime

from .accelerometer import Accelerometer
from .gps import Gps
from .aq import Aq


@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    aq: Aq
    timestamp: datetime
    user_id: int
