import sqlite3
import os
from flask import Flask, render_template, session, redirect, url_for, request

app = Flask(__name__)
app.secret_key = 'my_super_secret_key_888'

DB_FILE = '/app/passwords.db'
ADMIN_USER = 'admin'
ADMIN_PASS = 'security2025'

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

        # 2. 风险统计 (这里改用了最稳妥的写法)
        risk_stats = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        cursor.execute("SELECT risk_level, COUNT(*) FROM attack_logs GROUP BY risk_level")
        rows = cursor.fetchall()
        for r in rows:
            if r[0] in risk_stats:
                risk_stats[r[0]] = r[1]

        # 3. 最新日志
        cursor.execute("SELECT * FROM attack_logs ORDER BY rowid DESC LIMIT 10")
        logs = cursor.fetchall()

        conn.close()
        return total, success, fail, logs, risk_stats
    except Exception as e:
        print(f"Database Error: {e}")
        return 0, 0, 0, [], {'HIGH':0, 'MEDIUM':0, 'LOW':0}

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = '⚠️ 认证失败：账号或口令错误'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    total, success, fail, logs, risk_stats = get_db_stats()
    return render_template('index.html', total=total, success=success, fail=fail, logs=logs, risks=risk_stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
