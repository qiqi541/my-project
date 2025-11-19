from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json

app = Flask(__name__)

# Kafka Producer 初始化
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # 漏洞模拟：弱密码验证（永远认为密码正确）
    login_success = True

    # 将登录事件发送到 Kafka
    event = {
        "username": username,
        "password": password,
        "login_success": login_success,
        "source": "vuln-web"
    }

    producer.send("attack-events", event)

    return jsonify({"message": "Login processed (vulnerable)", "received": event})

@app.route("/", methods=["GET"])
def home():
    return "Vulnerable Web App Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

