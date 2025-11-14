# 使用官方 Python 3.10 镜像作为基础
FROM python:3.10-slim

# 在容器中创建工作目录
WORKDIR /app

# 复制项目文件（这里只会复制 run.py）
COPY . .

# 安装依赖（目前只需要 kafka-python）
RUN pip install kafka-python

# 启动命令（默认执行 run.py）
CMD ["python3", "run.py"]
