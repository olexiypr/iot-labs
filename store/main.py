import json
import logging
import os
from typing import Set, Dict, List, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from datetime import datetime
from pydantic import BaseModel, field_validator
from config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)
from fastapi.middleware.cors import CORSMiddleware
from paho.mqtt import client as mqtt_client

# FastAPI app setup
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to a specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# SQLAlchemy setup
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
# Define the ProcessedAgentData table
processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String),
    Column("air_quality", String),
    Column("user_id", Integer),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)

raw_agent_data = Table(
    "raw_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("co2_level", Integer),
    Column("temperature", Float),
    Column("pm2_5", Integer),
    Column("pm10", Integer),
    Column("timestamp", DateTime),
)

traffic_light_data = Table(
    "traffic_light_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("traffic_light_id", Integer),
    Column("cars_waiting", Integer),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)
SessionLocal = sessionmaker(bind=engine)


# SQLAlchemy model
class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    air_quality: str
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime


class TrafficLightDataInDB(BaseModel):
    id: int
    traffic_light_id: int
    cars_waiting: int
    latitude: float
    longitude: float
    timestamp: datetime


# FastAPI models
class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float


class GpsData(BaseModel):
    latitude: float
    longitude: float


class AqData(BaseModel):
    co2_level: int
    temperature: float
    pm2_5: int
    pm10: int


class AgentData(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    aq: AqData
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


class AgentDataMessage(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    aq: AqData
    timestamp: datetime
    user_id: int

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


class ProcessedAgentData(BaseModel):
    road_state: str
    air_quality: str
    agent_data: AgentData


class TrafficLightData(BaseModel):
    traffic_light_id: int
    cars_waiting: int
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


# WebSocket subscriptions
subscriptions: Dict[int, Set[WebSocket]] = {}


# FastAPI WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in subscriptions:
        subscriptions[user_id] = set()
    subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions[user_id].remove(websocket)


# Function to send data to subscribed users
def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print(f"Failed to connect {broker}:{port}, return code %d\n", rc)
            exit(rc)  # Stop execution

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client

mqClient = connect_mqtt("localhost", 1883)

async def send_data_to_subscribers(user_id: int, data):
    mqClient.publish("map_view_topic", json.dumps(data))


async def send_traffic_light_to_subscribers(data):
    mqClient.publish("traffic_light_view_topic", json.dumps(data))


# MQTT ingest for raw agent data
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "agent_data_topic")


def _save_agent_data_from_mqtt(agent_data: AgentDataMessage) -> None:
    value = {
        "x": agent_data.accelerometer.x,
        "y": agent_data.accelerometer.y,
        "z": agent_data.accelerometer.z,
        "latitude": agent_data.gps.latitude,
        "longitude": agent_data.gps.longitude,
        "co2_level": agent_data.aq.co2_level,
        "temperature": agent_data.aq.temperature,
        "pm2_5": agent_data.aq.pm2_5,
        "pm10": agent_data.aq.pm10,
        "timestamp": agent_data.timestamp,
        "user_id": agent_data.user_id,
    }
    query = raw_agent_data.insert().values([value])
    with engine.begin() as conn:
        conn.execute(query)


def _start_agent_mqtt_listener():
    client = mqtt_client.Client()

    def on_connect(inner_client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker for ingest")
            inner_client.subscribe(MQTT_TOPIC)
        else:
            logging.info("Failed to connect to MQTT broker for ingest: %s", rc)

    def on_message(inner_client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8")
            agent_data = AgentDataMessage.model_validate_json(payload, strict=True)
            _save_agent_data_from_mqtt(agent_data)
        except Exception as exc:
            logging.info("MQTT ingest error: %s", exc)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
    client.loop_start()
    return client


agent_mqtt_client = None


@app.on_event("startup")
def _startup():
    global agent_mqtt_client
    agent_mqtt_client = _start_agent_mqtt_listener()


@app.on_event("shutdown")
def _shutdown():
    if agent_mqtt_client is not None:
        agent_mqtt_client.loop_stop()


# FastAPI CRUDL endpoints


@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    query_values = []
    for item in data:
        value = {
            "road_state": item.road_state,
            "air_quality": item.air_quality,
            "x": item.agent_data.accelerometer.x,
            "y": item.agent_data.accelerometer.y,
            "z": item.agent_data.accelerometer.z,
            "latitude": item.agent_data.gps.latitude,
            "longitude": item.agent_data.gps.longitude,
            "timestamp": item.agent_data.timestamp,
            "user_id": 1,
        }
        query_values.append(value)
    query = processed_agent_data.insert().values(query_values)
    with engine.begin() as conn:
        conn.execute(query)
    for item in data:
        await send_data_to_subscribers(1, [{**d, "timestamp": d["timestamp"].isoformat()} for d in query_values])


@app.get(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def read_processed_agent_data(processed_agent_data_id: int):
    query = select(processed_agent_data).where(processed_agent_data.c.id == processed_agent_data_id)
    with engine.connect() as conn:
        result = conn.execute(query)
        data = result.fetchone()
        if data is None:
            raise HTTPException(status_code=404, detail="Data not found")
    return data


@app.get("/processed_agent_data/", response_model=list[ProcessedAgentDataInDB])
def list_processed_agent_data():
    query = select(processed_agent_data)
    with engine.connect() as conn:
        result = conn.execute(query)
        data_list = result.fetchall()
    return data_list


@app.put(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    query = (processed_agent_data.update().where(
        processed_agent_data.c.id == processed_agent_data_id)
    .values(
        road_state=data.road_state,
        air_quality=data.air_quality,
        x=data.agent_data.accelerometer.x,
        y=data.agent_data.accelerometer.y,
        z=data.agent_data.accelerometer.z,
        latitude=data.agent_data.gps.latitude,
        longitude=data.agent_data.gps.longitude,
        timestamp=data.agent_data.timestamp,
        user_id=1))
    with engine.begin() as conn:
        result = conn.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Data not found")
    return read_processed_agent_data(processed_agent_data_id)


@app.delete(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def delete_processed_agent_data(processed_agent_data_id: int):
    processed_agent_data_to_be_removed = read_processed_agent_data(processed_agent_data_id)
    query = processed_agent_data.delete().where(processed_agent_data.c.id == processed_agent_data_id)
    with engine.begin() as conn:
        result = conn.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Data not found")
    return processed_agent_data_to_be_removed


@app.post("/traffic_light/")
async def create_traffic_light_data(data: TrafficLightData):
    value = {
        "traffic_light_id": data.traffic_light_id,
        "cars_waiting": data.cars_waiting,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "timestamp": data.timestamp,
    }
    query = traffic_light_data.insert().values([value])
    with engine.begin() as conn:
        conn.execute(query)
    await send_traffic_light_to_subscribers(
        [{**value, "timestamp": value["timestamp"].isoformat()}]
    )
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
