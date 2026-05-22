import os

STORE_HOST = "localhost"
STORE_PORT = 8000
TRAFFIC_LIGHT_TOPIC = os.environ.get("TRAFFIC_LIGHT_TOPIC") or "traffic_light_view_topic"
