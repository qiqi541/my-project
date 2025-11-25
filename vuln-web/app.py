import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- 1. 模拟数据库 ---
def init_vuln_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE users (username TEXT, secret_data TEXT)")
    c.execute("INSERT INTO users VALUES ('admin', '这是管理员的机密数据！')")
    c.execute("INSERT INTO users VALUES ('guest', '这是普通数据')")
    conn.commit()
    return conn

db_conn = init_vuln_db()

@app.route('/')
def home():
    return "靶机运行中：支持 /login, /search, /feedback (XSS)"

# --- 2. 弱口令接口 ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data: return jsonify({"msg": "No data"}), 400
    if data.get("username") == "admin" and data.get("password") == "admin123":
        return jsonify({"status": "success", "msg": "登录成功！"}), 200
    return jsonify({"status": "fail", "msg": "密码错误"}), 401

# --- 3. SQL 注入接口 ---
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    sql = f"SELECT * FROM users WHERE username = '{query}'"
    try:
        cursor = db_conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            return jsonify({"status": "success", "data": results}), 200
        else:
            return jsonify({"status": "fail", "msg": "未找到"}), 404
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

# --- 4. [新增] XSS 漏洞接口 (留言板) ---
@app.route('/feedback', methods=['POST'])
def feedback():
    # 获取用户提交的留言
    data = request.get_json()
    content = data.get('content', '')

    # [严重漏洞]：没有对 content 进行任何过滤或转义，直接返回！
    # 如果攻击者发送 "<script>alert(1)</script>"，浏览器就会执行它。
    return f"提交成功！你的留言是: {content}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
