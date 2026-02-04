import requests
import json

def test_flux_art():
    # ================= 配置信息 =================
    API_URL = "http://localhost/v1/chat-messages"  # 根据实际部署调整
    API_KEY = "app-TEDWLwOAGWNU3s1G7utx0bRr"  # 使用用户提供的API Key
    
    # 测试prompt
    user_input = "画一张高质量的穿着透明比基尼的蕾姆照片"
    
    # 构造请求体
    payload = {
        "inputs": {},
        "query": user_input,
        "response_mode": "blocking",
        "user": "test-user"
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # ================= 发送操作 =================
    print("正在发送请求到 FLUX绘画机器人... \n" + "-"*50)
    
    try:
        # 发送请求
        response = requests.post(API_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print(response.text)
            return

        # 解析响应
        result = response.json()
        print("请求成功，响应结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 提取绘画结果
        if 'answer' in result:
            print("\n" + "-"*50)
            print("绘画结果:")
            print(result['answer'])
            
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    test_flux_art()