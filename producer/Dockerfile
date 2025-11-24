# 文件路径: producer/Dockerfile
FROM python:3.9-slim
WORKDIR /app
# 安装 requests 用来发请求，kafka-python 用来发数据
RUN pip install kafka-python requests
COPY . .
# 让 Python 的 print 立即输出，不要缓存
ENV PYTHONUNBUFFERED=1
CMD ["python", "producer.py"]
