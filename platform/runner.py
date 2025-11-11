import subprocess
import json
import os
import datetime

def run_reproducer():
    # 设置 docker 命令（根据需要修改）
    command = ["docker", "run", "--rm", "repro-cve-hello:0.1"]
    
    try:
        # 执行 docker 命令并捕获 stdout
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # 获取当前时间
        timestamp = datetime.datetime.now().isoformat()

        # 定义输出的 JSON 格式
        output_data = {
            "plugin": "repro-cve-hello",
            "run_id": "1234-5678-90",  # 这里你可以根据需要生成或获取 run_id
            "timestamp": timestamp,
            "stdout": result.stdout,  # 捕获的 stdout
            "stderr": result.stderr,  # 捕获的 stderr
        }

        # 创建 outputs 文件夹（如果不存在）
        if not os.path.exists("outputs"):
            os.makedirs("outputs")
        
        # 定义输出文件路径
        output_file = os.path.join("outputs", f"evidence_{timestamp}.json")

        # 将输出数据写入 JSON 文件
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=4)

        print(f"Saved evidence to {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running the command: {e}")
        print(f"stderr: {e.stderr}")

if __name__ == "__main__":
    run_reproducer()
