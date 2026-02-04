import requests
import json

def test_workflow():
    # ================= 配置信息 =================
    API_URL = "http://localhost/v1/workflows/run"  # Workflow 执行端点
    API_KEY = "app-AZoTWG6sV0V2O77Enzw9pK8c"  # 使用提供的 API Key
    
    # 获取用户输入
    user_input = input("请输入测试文本: ")
    
    # 构造请求体
    payload = {
        "inputs": {"Input": user_input},  # 空 inputs，因为输入是通过纯文本提供
        "response_mode": "streaming",  # 使用流式响应
        "user": "test-user"  # 用户标识
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # ================= 发送操作 =================
    print("\n正在发送请求到 Workflow... \n" + "-"*50)
    print(f"测试输入: {user_input}")
    print("-"*50)
    
    try:
        # 发送请求，使用 stream=True 处理流式响应
        response = requests.post(API_URL, json=payload, headers=headers, stream=True, timeout=60)
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.text)
            return

        # 处理流式响应
        print("流式响应结果:")
        print("-"*50)
        
        for line in response.iter_lines():
            if line:
                # 转换字节流并处理
                line_data = line.decode('utf-8')
                if line_data.startswith("data: "):
                    json_str = line_data[6:]
                    try:
                        data = json.loads(json_str)
                        # 打印响应数据
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                        
                        # 检查是否结束
                        if data.get('event') == 'workflow_end':
                            print("\n" + "-"*50)
                            print("Workflow 执行结束")
                            break
                    except json.JSONDecodeError:
                        print(f"无法解析响应行: {json_str}")
                        continue
            
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    test_workflow()