import logging
from typing import List
import requests

from hub.app.entities.processed_agent_data import ProcessedAgentData
from hub.app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        try:
            data = []
            for item in processed_agent_data_batch:
                timestamp_isoformat = item.agent_data.timestamp.isoformat()
                data_item = item.model_dump()
                data_item['agent_data']['timestamp'] = timestamp_isoformat
                data.append(data_item)
            response = requests.post(f"{self.api_base_url}/processed_agent_data/", json=data)
            print(response)
            if response.status_code == 200 or response.ok :
                return True
            else:
                return False
        except Exception as e:
            logging.info(f"Error occured {e}")
            return False
