from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

RawT = TypeVar("RawT")
EntityT = TypeVar("EntityT")


class BaseSensor(ABC, Generic[RawT, EntityT]):
    @abstractmethod
    def get_sensor_data(self) -> RawT:
        """Read raw data from the sensor implementation."""
        raise NotImplementedError

    def get_data(self, entity_factory: Callable[[RawT], EntityT]) -> EntityT:
        """Read raw data and wrap it into the provided entity factory."""
        raw = self.get_sensor_data()
        return entity_factory(raw)

