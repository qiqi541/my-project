import json
import sqlite3
import os
import time
from kafka import KafkaConsumer

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
TOPIC = 'evidence_topic'
DB_FILE = 'passwords.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attack_logs
                 (timestamp REAL, attack_type TEXT, payload TEXT, http_status INTEGER, result TEXT)''')
    conn.commit()
    return conn

def get_consumer():
    while True:
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print("Consumer 启动成功，正在监听数据...")
            return consumer
        except:
            time.sleep(2)

def run_consumer():
    conn = init_db()
    consumer = get_consumer()
    c = conn.cursor()

    for message in consumer:
        data = message.value

        # --- 修复点：使用 .get() 方法，防止缺少字段报错 ---
        ts = data.get('timestamp', time.time())
        atype = data.get('attack_type', 'unknown')
        payload = data.get('payload', '')
        status = data.get('http_status', 0)  # 如果没有状态码，默认填 0
        result = data.get('result', 'unknown')

        print(f"[收到数据] 类型: {atype}, 结果: {result}, 密码: {payload}")

        try:
            c.execute("INSERT INTO attack_logs (timestamp, attack_type, payload, http_status, result) VALUES (?, ?, ?, ?, ?)",
                      (ts, atype, payload, status, result))
            conn.commit()
        except Exception as e:
            print(f"写入数据库错误: {e}")

if __name__ == '__main__':
    run_consumer()
