from kafka import KafkaProducer
import json
from src.config import KAFKA_BOOTSTRAP_SERVERS

# Globalny Producent
producer = None

def get_producer():
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
        except Exception as e:
            print(f"Niepowodzenie utworzenia producenta: {e}")
    return producer
