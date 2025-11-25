import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
DB_FILE = '/app/passwords.db'

def get_db_stats():
    try:
        conn = sqlite3.connect(f'file:{DB_FILE}?mode=ro', uri=True)
        cursor = conn.cursor()

        # 1. 基础统计
        cursor.execute("SELECT COUNT(*) FROM attack_logs")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attack_logs WHERE result='success'")
        success = cursor.fetchone()[0]
        fail = total - success

        # 2. [新增] 风险等级统计
        # 统计 HIGH, MEDIUM, LOW 各有多少
        risk_stats = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        cursor.execute("SELECT risk_level, COUNT(*) FROM attack_logs GROUP BY risk_level")
        rows = cursor.fetchall()
        for r in rows:
            # r[0] 是风险等级名字, r[1] 是数量
            if r[0] in risk_stats:
                risk_stats[r[0]] = r[1]

        # 3. 获取最新日志
        cursor.execute("SELECT * FROM attack_logs ORDER BY rowid DESC LIMIT 10")
        logs = cursor.fetchall()

        conn.close()
        return total, success, fail, logs, risk_stats
    except Exception as e:
        print(f"DB Error: {e}")
        return 0, 0, 0, [], {'HIGH':0, 'MEDIUM':0, 'LOW':0}

@app.route('/')
def index():
    total, success, fail, logs, risk_stats = get_db_stats()
    return render_template('index.html', 
                           total=total, 
                           success=success, 
                           fail=fail, 
                           logs=logs,
                           risks=risk_stats) # 把风险数据传给网页

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
