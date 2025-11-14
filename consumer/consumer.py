#!/usr/bin/env python3
import os, json, time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = os.getenv("TOPIC", "evidence_topic")

print("Consumer starting. Kafka broker:", KAFKA_BROKER, "topic:", TOPIC)

# 连接重试机制
consumer = None
while consumer is None:
    try:
        consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id='my-group',
        )
        print("Connected to Kafka successfully.")
    except NoBrokersAvailable:
        print("Kafka not ready, retrying in 3 seconds...")
        time.sleep(3)

print("Consumer started. Listening for messages...")

for message in consumer:
    print("[Kafka] Received:", message.value)

