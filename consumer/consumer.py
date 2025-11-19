from kafka import KafkaConsumer
import requests
import json

# Kafka consumer 监听 attack_events topic
consumer = KafkaConsumer(
    'attack_events',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

print("Consumer started. Listening for attack events...")

API_URL = "http://127.0.0.1:5000/ingest"

for message in consumer:
    attack_event = message.value
    print("Received attack event:", attack_event)

    # 转发到 Flask API
    try:
        r = requests.post(API_URL, json=attack_event)
        print("Forwarded to Flask API, status:", r.status_code)
    except Exception as e:
        print("Error forwarding to API:", e)

