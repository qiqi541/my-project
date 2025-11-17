#!/usr/bin/env python3
import os
import json
import time
import uuid
import sqlite3
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

# 配置（容器内路径）
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = os.getenv("TOPIC", "evidence_topic")
OUT_DIR = "/app/outputs"   # 确保 docker-compose 中挂载了 ./outputs:/app/outputs

print("Consumer starting. Kafka broker:", KAFKA_BROKER, "topic:", TOPIC, "outputs:", OUT_DIR)

# 确保输出目录存在（容器内）
os.makedirs(OUT_DIR, exist_ok=True)

# 初始化 SQLite（数据库文件放在 OUT_DIR）
DB_PATH = os.path.join(OUT_DIR, "evidence.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    topic TEXT,
    partition INTEGER,
    offset INTEGER,
    received_at REAL,
    payload_json TEXT
)
""")
conn.commit()

# 连接 Kafka（带重试）
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
    try:
        data = message.value
    except Exception as e:
        print("[ERROR] decode message:", e)
        continue

    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    uid = uuid.uuid4().hex[:8]
    filename = f"evidence_{ts}_{uid}.json"
    path = os.path.join(OUT_DIR, filename)

    # 写文件
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "kafka_topic": TOPIC,
                "kafka_partition": message.partition,
                "kafka_offset": message.offset,
                "received_at": time.time(),
                "payload": data
            }, f, ensure_ascii=False, indent=2)
        print(f"[Kafka] Received and saved to {path}: {data}")
    except Exception as e:
        print("[ERROR] writing file:", e)

    # 写入 SQLite
    try:
        cur.execute(
            "INSERT OR REPLACE INTO evidence (id, topic, partition, offset, received_at, payload_json) VALUES (?, ?, ?, ?, ?, ?)",
            (uid, TOPIC, message.partition, message.offset, time.time(), json.dumps(data, ensure_ascii=False))
        )
        conn.commit()
        print(f"[DB] Inserted record id={uid}")
    except Exception as e:
        print("[ERROR] sqlite insert:", e)

