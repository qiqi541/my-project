# 文件路径: consumer/consumer.py
import json
import sqlite3
import os
import time
from kafka import KafkaConsumer

# 配置信息
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
TOPIC = 'evidence_topic'
DB_FILE = 'passwords.db'

# 初始化数据库
def init_db():
    # 如果文件不存在，会自动创建
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 创建表，用于存储攻击日志
    c.execute('''CREATE TABLE IF NOT EXISTS attack_logs
                 (timestamp REAL, attack_type TEXT, payload TEXT, http_status INTEGER, result TEXT)''')
    conn.commit()
    return conn

def get_consumer(conn):
    consumer = None
    while not consumer:
        try:
            print(f"正在尝试连接 Consumer 到 Kafka: {KAFKA_BROKER}...")
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print("Consumer 启动成功，正在监听数据...")
        except Exception as e:
            print(f"连接失败，2秒后重试...")
            time.sleep(2)
    return consumer

def run_consumer():
    conn = init_db()
    consumer = get_consumer(conn)
    c = conn.cursor()

    for message in consumer:
        data = message.value
        print(f"[收到数据] 类型: {data['attack_type']}, 结果: {data['result']}, 密码: {data['payload']}")

        # 写入数据库 (与 producer 发送的 JSON 字段对应)
        c.execute("INSERT INTO attack_logs (timestamp, attack_type, payload, http_status, result) VALUES (?, ?, ?, ?, ?)",
                  (data['timestamp'], data['attack_type'], data['payload'], data['http_status'], data['result']))
        conn.commit()

if __name__ == '__main__':
    run_consumer()
