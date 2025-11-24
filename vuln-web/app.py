from flask import Flask, request, jsonify

app = Flask(__name__)

# 这是正确的账号和密码
TARGET_USERNAME = "admin"
TARGET_PASSWORD = "admin123"

@app.route('/')
def home():
    return "漏洞靶机正在运行！请尝试攻击 /login 接口"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "No data"}), 400

    username = data.get("username")
    password = data.get("password")

    if username == TARGET_USERNAME and password == TARGET_PASSWORD:
        return jsonify({"status": "success", "msg": "登录成功！"}), 200
    else:
        return jsonify({"status": "fail", "msg": "密码错误"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

