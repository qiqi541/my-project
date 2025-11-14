FROM python:3.10-slim
WORKDIR /app
COPY consumer.py /app
RUN pip install kafka-python
CMD ["python3", "-u", "consumer.py"]
