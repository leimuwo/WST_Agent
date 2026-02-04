import requests
import json

def call_dify_api():
    # ================= 配置信息 =================
    API_URL = "http://localhost/v1/completion-messages"
    API_KEY = "app-IKPVAYsx91LR2P4kvsmxwokv"
    
    # 这里是你想要发送给 Dify 处理的代码内容
    python_code_content = """
import os
import re
from PIL import Image
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

def convert_single_image(args):
    \"\"\"单个文件转换函数，供多进程调用\"\"\"
    file_path, target_path = args
    try:
        with Image.open(file_path) as img:
            rgb_img = img.convert('RGB')
            rgb_img.save(target_path, 'PNG', optimize=False)
        return True, None
    except Exception as e:
        return False, f"Error processing {file_path}: {e}"

def convert_jpg_to_png_multi(source_folder, target_folder, max_workers=None):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    valid_extensions = ('.jpg', '.jpeg', '.JPG', '.JPEG')
    image_files = [f for f in os.listdir(source_folder) if f.endswith(valid_extensions)]
    # ... (其余逻辑)
"""

    # 构造请求体，严格匹配你 Dify 应用的变量名
    payload = {
        "inputs": {
            "Target_code": "Java",      # 对应你之前报错缺失的变量
            "default_input": python_code_content, # 传入你的 Python 代码
            "query": "请根据提供的 Python 代码逻辑，详细解释其多进程实现的方式。"
        },
        "response_mode": "streaming",
        "user": "developer-admin"
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # ================= 发送操作 =================
    print("正在发送请求到 Dify (流式输出)... \n" + "-"*30)
    
    try:
        # 使用 stream=True 处理流式响应
        response = requests.post(API_URL, json=payload, headers=headers, stream=True)
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.text)
            return

        # 逐行解析流式数据
        for line in response.iter_lines():
            if line:
                # 转换字节流并去除 'data: ' 前缀
                line_data = line.decode('utf-8')
                if line_data.startswith("data: "):
                    json_str = line_data[6:]
                    try:
                        data = json.loads(json_str)
                        # Dify 流式返回中，内容通常在 'answer' 字段
                        if 'answer' in data:
                            print(data['answer'], end='', flush=True)
                        if data.get('event') == 'message_end':
                            print("\n" + "-"*30 + "\n回答生成结束。")
                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    call_dify_api()