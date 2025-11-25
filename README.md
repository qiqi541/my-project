🛡️ 密码应用漏洞复现与验证系统

Password Application Vulnerability Reproduction and Verification System

一个基于微服务架构的自动化网络安全仿真平台，集成了漏洞靶机、自动化攻击模拟、实时流量监测与态势感知大屏。

📖 项目简介

本项目旨在构建一套全链路闭环的网络安全研究平台，用于研究密码应用中的典型漏洞及其防护技术。系统采用 Docker 容器化技术构建，通过 Kafka 消息队列实现攻击端与分析端的解耦，并基于 Python 全栈开发实现了从漏洞探测、风险评估到可视化展示的完整流程。

本项目响应了网络安全研究中的三大核心任务：

模块化架构设计：实现组件解耦与灵活扩展。

攻击行为动态监测：实时捕获并分析攻击流量。

数据收集与可视化：构建态势感知大屏，提供决策支持。

🚀 核心功能

1. 多类型漏洞复现 (Vulnerability Reproduction)

内置高度仿真的漏洞靶机 (vuln-web)，支持以下典型漏洞：

弱口令 (Weak Password)：模拟管理员账号使用简单密码。

SQL 注入 (SQL Injection)：模拟未经过滤的数据库查询漏洞。

跨站脚本攻击 (XSS)：模拟存储型/反射型 XSS 漏洞。

2. 自动化攻击模拟 (Automated Attack Simulation)

智能攻击者模块 (producer) 能够自动对靶机发起探测：

暴力破解：基于字典的自动化登录尝试。

Payload 投递：自动构造 SQL 注入和 XSS 脚本 Payload。

自适应检测：根据 HTTP 响应状态码自动判定攻击是否成功。

3. 动态风险评估 (Risk Assessment)

系统内置风险定级算法，根据攻击类型自动评估威胁等级：

🔴 HIGH (高危)：SQL 注入（可能导致数据泄露）。

🟠 MEDIUM (中危)：弱口令破解（可能导致权限丢失）。

🟢 LOW (低危)：XSS 攻击（可能影响客户端安全）。

4. 态势感知大屏 (Situational Awareness Dashboard)

基于 Flask 和 Chart.js 构建的实时监控平台：

实时数据流：秒级展示最新的攻击日志。

统计图表：攻击成功率饼图 + 风险等级分布柱状图。

访问控制：集成 Session 登录认证，保护敏感数据。

🏗️ 系统架构

本系统采用微服务架构，包含以下核心组件：

组件名称

技术栈

功能描述

Vuln-Web

Python Flask, SQLite

漏洞靶机：提供存在漏洞的 Web 接口。

Producer

Python, Requests

攻击源：模拟黑客行为，发起攻击并生成证据数据。

Kafka

Apache Kafka, Zookeeper

数据总线：负责高吞吐量的攻击数据传输与缓冲。

Consumer

Python, Kafka-Python

分析器：消费数据，清洗并存储至数据库。

Dashboard

Flask, Chart.js

可视化中心：展示攻击态势与风险报表。

🛠️ 快速开始 (Quick Start)

前置要求

操作系统：Linux (Ubuntu) / Windows / macOS

环境依赖：Docker 和 Docker Compose

1. 克隆项目

git clone <q1q1541/my-project>
cd password-vuln-repro


2. 启动系统

使用 Docker Compose 一键启动所有服务：

docker compose up --build -d


3. 访问仪表盘

等待约 10-20 秒，待所有容器启动完毕后，打开浏览器访问：

地址：http://localhost:5001

管理员账号：admin

访问口令：security2025

登录成功后，您将看到实时更新的攻击态势大屏。

4. 停止系统

docker compose down


📂 项目结构

password-vuln-repro/
├── docker-compose.yml      # 系统编排文件 (核心)
├── vuln-web/               # [靶机] 漏洞 Web 服务
│   ├── app.py
│   └── Dockerfile
├── producer/               # [攻击者] 自动化攻击脚本
│   ├── producer.py         # 包含攻击逻辑与风险评估算法
│   ├── payloads.txt        # 密码字典
│   └── Dockerfile
├── consumer/               # [分析器] 数据处理服务
│   ├── consumer.py         # Kafka 消费者与 SQLite 存储
│   └── Dockerfile
└── dashboard/              # [大屏] 可视化前端
    ├── app.py              # 后端统计逻辑与登录认证
    ├── templates/          # HTML 模板
    │   ├── index.html      # 仪表盘主页
    │   └── login.html      # 登录页
    └── Dockerfile


⚠️ 免责声明

本项目仅用于网络安全教学、学术研究与漏洞复现演示。

请勿将本项目部署于公网环境。

请勿使用本项目中的攻击脚本对非授权目标进行测试。

使用者需自行承担因使用本项目而产生的任何法律责任。

Project Status: ✅ Completed (v1.0)
Author: [qiqi]
