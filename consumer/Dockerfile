# 文件路径: consumer/Dockerfile
FROM python:3.9-slim
WORKDIR /app
# 安装 kafka-python 和 sqlite3
# sqlite3 库通常是 Python 内建的，但这里还是需要安装 kafka-python
RUN pip install kafka-python
COPY . .
# 让 Python 的 print 立即输出，不要缓存
ENV PYTHONUNBUFFERED=1
CMD ["python", "consumer.py"]
