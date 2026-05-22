from abc import ABC, abstractmethod
from typing import List
from ..entities.processed_agent_data import ProcessedAgentData
from ..entities.traffic_light import TrafficLightData


class StoreGateway(ABC):
    """
    Abstract class representing the Store Gateway interface.
    All store gateway adapters must implement these methods.
    """

    @abstractmethod
    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]) -> bool:
        """
        Method to save the processed agent data in the database.
        Parameters:
            processed_agent_data_batch (ProcessedAgentData): The processed agent data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        pass

    @abstractmethod
    def save_traffic_light_data(self, traffic_light_data: TrafficLightData) -> bool:
        """Save traffic light data in the store."""
        pass
