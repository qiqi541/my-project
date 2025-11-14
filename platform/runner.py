#!/usr/bin/env python3
import subprocess, json, os, uuid, time, sys
from kafka import KafkaProducer

# 可修改：镜像名、Kafka地址、topic
IMAGE = os.environ.get("REPRO_IMAGE", "repro-cve-hello:0.1")
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "evidence_topic")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_container_and_capture(image: str):
    cmd = ["docker", "run", "--rm", image]
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()
    return stdout, stderr, proc.returncode

def save_output(stdout: str, stderr: str, returncode: int):
    run_id = str(uuid.uuid4())
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out = {
        "runner_run_id": run_id,
        "timestamp": timestamp,
        "container_returncode": returncode,
        "stdout": None,
        "stderr": stderr
    }
    try:
        out["stdout"] = json.loads(stdout) if stdout else None
    except Exception:
        out["stdout"] = stdout
    fname = os.path.join(OUTPUT_DIR, f"evidence_{run_id}.json")
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("Saved evidence to", fname)
    return fname, out

def push_to_kafka(evidence_obj):
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BOOTSTRAP],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        producer.send(KAFKA_TOPIC, value=evidence_obj)
        producer.flush()
        print("Pushed evidence to Kafka topic:", KAFKA_TOPIC)
    except Exception as e:
        print("Failed to push to Kafka:", e, file=sys.stderr)

if __name__ == "__main__":
    stdout, stderr, rc = run_container_and_capture(IMAGE)
    fname, evidence = save_output(stdout, stderr, rc)
    # 加入文件路径信息到 evidence，再推送
    evidence["_local_file"] = fname
    push_to_kafka(evidence)
