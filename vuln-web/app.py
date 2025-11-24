import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- 1. 模拟一个内部数据库 (靶机的存储) ---
# 为了演示 SQL 注入，我们在内存里创建一个临时数据库
def init_vuln_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE users (username TEXT, secret_data TEXT)")
    # 插入一条管理员数据，这是攻击者想偷看的数据
    c.execute("INSERT INTO users VALUES ('admin', '这是管理员的机密数据！')")
    c.execute("INSERT INTO users VALUES ('guest', '这是普通数据')")
    conn.commit()
    return conn

# 初始化数据库
db_conn = init_vuln_db()

@app.route('/')
def home():
    return "靶机运行中：包含 /login (弱口令) 和 /search (SQL注入) 漏洞"

# --- 2. 原有的弱口令漏洞接口 ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data: return jsonify({"msg": "No data"}), 400
    if data.get("username") == "admin" and data.get("password") == "admin123":
        return jsonify({"status": "success", "msg": "登录成功！"}), 200
    return jsonify({"status": "fail", "msg": "密码错误"}), 401

# --- 3. 新增：SQL 注入漏洞接口 ---
@app.route('/search', methods=['GET'])
def search():
    # 获取 URL 参数，例如 /search?q=admin
    query = request.args.get('q', '')

    # [严重漏洞]：直接将用户输入拼接到 SQL 语句中！
    # 攻击者输入 "' OR '1'='1" 就能绕过限制
    sql = f"SELECT * FROM users WHERE username = '{query}'"

    try:
        cursor = db_conn.cursor()
        cursor.execute(sql) # 执行不安全的 SQL
        results = cursor.fetchall()

        if results:
            # 如果查到了数据，就把数据返回给攻击者
            return jsonify({"status": "success", "data": results, "sql": sql}), 200
        else:
            return jsonify({"status": "fail", "msg": "未找到用户", "sql": sql}), 404
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "sql": sql}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
