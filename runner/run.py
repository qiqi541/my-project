#!/usr/bin/env python3
import os, json, time
from kafka import KafkaProducer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = os.getenv("TOPIC", "evidence_topic")

print("Runner started. Kafka broker:", KAFKA_BROKER, "topic:", TOPIC)

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# 发送 5 条 evidence 消息
for i in range(5):
    msg = {
        "type": "evidence",
        "seq": i,
        "ts": time.time()
    }
    print(f"[Kafka] Sending message {msg}")
    producer.send(TOPIC, msg)
    time.sleep(1)

print("Runner finished sending messages.")

