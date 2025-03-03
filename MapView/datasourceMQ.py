import asyncio
import json
from datetime import datetime
import websockets
from kivy import Logger
from pydantic import BaseModel, field_validator
import paho.mqtt.client as mqtt

from config import STORE_HOST, STORE_PORT


# Pydantic models
class ProcessedAgentData(BaseModel):
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )


class DatasourceMq:
    def __init__(self, user_id: int):
        self.index = 0
        self.user_id = user_id
        self.connection_status = None
        self._new_points = []
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883)
        self.client.loop_start()

    def get_new_points(self):
        Logger.debug(self._new_points)
        points = self._new_points
        self._new_points = []
        return points


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            Logger.info("Connected to MQTT broker")
            client.subscribe("map_view_topic")
        else:
            Logger.info(f"Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload: str = msg.payload.decode("utf-8")
            # Create ProcessedAgentData instance with the received data
            parsed_data = json.loads(payload)
            self.handle_received_data(parsed_data)
        except Exception as e:
            Logger.error(e)

    def handle_received_data(self, data):
        # Update your UI or perform actions with received data here
        Logger.debug(f"Received data: {data}")
        processed_agent_data_list = sorted(
            [
                ProcessedAgentData(**processed_data_json)
                for processed_data_json in data
            ],
            key=lambda v: v.timestamp,
        )
        new_points = [
            (
                processed_agent_data.latitude,
                processed_agent_data.longitude,
                processed_agent_data.road_state,
            )
            for processed_agent_data in processed_agent_data_list
        ]
        self._new_points.extend(new_points)
