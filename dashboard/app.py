import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
# 这里我们读取挂载进来的数据库文件
DB_FILE = '/app/passwords.db'

def get_db_stats():
    try:
        # 以只读模式连接，避免锁死数据库
        conn = sqlite3.connect(f'file:{DB_FILE}?mode=ro', uri=True)
        cursor = conn.cursor()

        # 1. 统计总数
        cursor.execute("SELECT COUNT(*) FROM attack_logs")
        total = cursor.fetchone()[0]

        # 2. 统计成功数
        cursor.execute("SELECT COUNT(*) FROM attack_logs WHERE result='success'")
        success = cursor.fetchone()[0]

        # 3. 失败数 = 总数 - 成功数
        fail = total - success

        # 4. 获取最新的 10 条日志
        cursor.execute("SELECT * FROM attack_logs ORDER BY rowid DESC LIMIT 10")
        logs = cursor.fetchall()

        conn.close()
        return total, success, fail, logs
    except Exception as e:
        print(f"Error reading DB: {e}")
        return 0, 0, 0, []

@app.route('/')
def index():
    total, success, fail, logs = get_db_stats()
    return render_template('index.html', 
                           total=total, 
                           success=success, 
                           fail=fail, 
                           logs=logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
