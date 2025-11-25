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
    # --- 修改点：在表中增加了 risk_level 字段 ---
    c.execute('''CREATE TABLE IF NOT EXISTS attack_logs
                 (timestamp REAL, attack_type TEXT, payload TEXT, http_status INTEGER, result TEXT, risk_level TEXT)''')
    conn.commit()
    return conn

def get_consumer():
    while True:
        try:
            return KafkaConsumer(TOPIC, bootstrap_servers=[KAFKA_BROKER], value_deserializer=lambda x: json.loads(x.decode('utf-8')))
        except: time.sleep(2)

def run_consumer():
    conn = init_db()
    consumer = get_consumer()
    c = conn.cursor()
    print("Consumer 升级完毕，准备记录风险等级...")

    for message in consumer:
        data = message.value
        ts = data.get('timestamp', time.time())
        atype = data.get('attack_type', 'unknown')
        payload = data.get('payload', '')
        status = data.get('http_status', 0)
        result = data.get('result', 'unknown')
        # 获取风险等级，默认为 INFO
        risk = data.get('risk_level', 'INFO')

        print(f"[收到] 类型:{atype} | 结果:{result} | 风险:{risk}")

        try:
            # --- 修改点：插入语句增加了 risk_level ---
            c.execute("INSERT INTO attack_logs VALUES (?, ?, ?, ?, ?, ?)",
                      (ts, atype, payload, status, result, risk))
            conn.commit()
        except Exception as e:
            print(f"写入错误: {e}")

if __name__ == '__main__':
    run_consumer()
