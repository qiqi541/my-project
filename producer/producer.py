from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 模拟攻击类型
attack_types = [
    "brute_force",
    "sql_injection",
    "xss_attempt",
    "credential_stuffing",
    "weak_password_test"
]

def generate_attack_event():
    event = {
        "attack_type": random.choice(attack_types),
        "timestamp": time.time(),
        "source_ip": f"192.168.1.{random.randint(10, 200)}",
        "payload": "test_payload",
        "status": "attempt"
    }
    return event

if __name__ == "__main__":
    print("Producer started. Sending attack events...")
    while True:
        event = generate_attack_event()
        print("Sent event:", event)
        producer.send("attack_events", event)  # ⭐ 使用正确的 Topic 名称
        time.sleep(2)

