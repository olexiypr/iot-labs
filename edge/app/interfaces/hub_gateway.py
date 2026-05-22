from abc import ABC, abstractmethod

from ..entities.processed_agent_data import ProcessedAgentData
from ..entities.traffic_light import TrafficLightData


class HubGateway(ABC):
    """
    Abstract class representing the Store Gateway interface.
    All store gateway adapters must implement these methods.
    """

    @abstractmethod
    def save_data(self, processed_data: ProcessedAgentData) -> bool:
        """
        Method to save the processed agent data in the database.
        Parameters:
            processed_data (ProcessedAgentData): The processed agent data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        pass

    @abstractmethod
    def save_traffic_light_data(self, traffic_light_data: TrafficLightData) -> bool:
        """Save traffic light data to the hub."""
        pass
