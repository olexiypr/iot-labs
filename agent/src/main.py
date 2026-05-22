from paho.mqtt import client as mqtt_client
import time
from datetime import datetime
from schema.aggregated_data_schema import AggregatedDataSchema
from schema.traffic_light_schema import TrafficLight as TrafficLightSchema
from domain.aggregated_data import AggregatedData
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aq import Aq
from domain.traffic_light import TrafficLight
from sensor.accelerometer_sensor import AccelerometerSensor
from sensor.aq_sensor import AqSensor
from sensor.gps_sensor import GpsSensor
from sensor.traffic_light_sensor import TrafficLightSensor
import config


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


def publish_agent_data_once(client, topic, accelerometer_sensor, gps_sensor, aq_sensor):
    accelerometer = accelerometer_sensor.get_data(
        lambda r: Accelerometer(r["x"], r["y"], r["z"])
    )
    gps = gps_sensor.get_data(lambda r: Gps(r["longitude"], r["latitude"]))
    aq = aq_sensor.get_data(
        lambda r: Aq(r["co2_level"], r["temperature"], r["pm2_5"], r["pm10"])
    )
    data = AggregatedData(
        accelerometer=accelerometer,
        gps=gps,
        aq=aq,
        timestamp=datetime.now(),
        user_id=config.USER_ID,
    )
    msg = AggregatedDataSchema().dumps(data)
    result = client.publish(topic, msg)
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {topic}")


def publish_traffic_light_data_batch_once(client, topic, traffic_light_sensor, batch_size=5):
    for _ in range(batch_size):
        traffic_light = traffic_light_sensor.get_data(
            lambda r: TrafficLight(
                r["traffic_light_id"],
                r["timestamp"],
                r["cars_waiting"],
                r["longitude"],
                r["latitude"],
            )
        )
        msg = TrafficLightSchema().dumps(traffic_light)
        result = client.publish(topic, msg)
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {topic}")


def run():
    # Prepare mqtt client
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)
    accelerometer_sensor = AccelerometerSensor()
    gps_sensor = GpsSensor()
    aq_sensor = AqSensor()
    traffic_light_sensor = TrafficLightSensor()
    last_agent_sent = 0.0
    last_traffic_sent = 0.0
    try:
        while True:
            now = time.time()
            if now - last_agent_sent >= config.DELAY:
                publish_agent_data_once(
                    client,
                    config.MQTT_TOPIC,
                    accelerometer_sensor,
                    gps_sensor,
                    aq_sensor,
                )
                last_agent_sent = now
            if now - last_traffic_sent >= config.TRAFFIC_LIGHT_DELAY:
                publish_traffic_light_data_batch_once(
                    client,
                    config.TRAFFIC_LIGHT_MQTT_TOPIC,
                    traffic_light_sensor,
                    batch_size=5,
                )
                last_traffic_sent = now
            time.sleep(0.1)
    finally:
        accelerometer_sensor.close()
        gps_sensor.close()
        aq_sensor.close()
        traffic_light_sensor.close()


if __name__ == "__main__":
    run()