      
import requests
import json
from typing import Dict, Any, Optional, List


class DifyChatClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def send_chat_message(
        self,
        query: str,
        inputs: Dict[str, Any] = None,
        response_mode: str = "blocking",
        conversation_id: str = "",
        user: str = "default_user",
        files: List[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        发送聊天消息
        
        Args:
            query: 用户查询内容
            inputs: 输入参数字典
            response_mode: 响应模式 ("blocking" 或 "streaming")
            conversation_id: 对话ID（可选）
            user: 用户标识符
            files: 文件列表
            stream: 是否使用流式响应
        
        Returns:
            响应数据
        """
        url = f"{self.base_url}/v1/chat-messages"
        
        payload = {
            "inputs": inputs or {},
            "query": query,
            "response_mode": response_mode,
            "conversation_id": conversation_id,
            "user": user,
            "files": files or []
        }
        
        try:
            if stream:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    stream=True
                )
                response.raise_for_status()
                return self._handle_streaming_response(response)
            else:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            if 'response' in locals():
                print(f"错误详情: {response.text}")
            return None
    
    def _handle_streaming_response(self, response):
        """处理流式响应"""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue


def example_basic_usage():
    """基本使用示例"""
    
    # 初始化客户端
    client = DifyChatClient(
        base_url="http://localhost",
        api_key="your-api-key-here"
    )
    
    # 发送消息（同步模式）
    result = client.send_chat_message(
        query="What are specs of iPhone 13 Pro Max?",
        response_mode="blocking",
        user="abc-123"
    )
    
    if result:
        print("响应结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))


def example_with_files():
    """带文件的使用示例"""
    
    client = DifyChatClient(
        base_url="http://localhost",
        api_key="your-api-key-here"
    )
    
    # 准备文件列表
    files = [
        {
            "type": "image",
            "transfer_method": "remote_url",
            "url": "https://cloud.dify.ai/logo/logo-site.png"
        }
    ]
    
    # 发送带文件的消息
    result = client.send_chat_message(
        query="请描述这张图片",
        files=files,
        response_mode="blocking",
        user="abc-123"
    )
    
    if result:
        print("响应结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))


def example_streaming():
    """流式响应示例"""
    
    client = DifyChatClient(
        base_url="http://localhost",
        api_key="your-api-key-here"
    )
    
    # 发送消息（流式模式）
    print("正在发送消息（流式模式）...")
    
    for chunk in client.send_chat_message(
        query="What are specs of iPhone 13 Pro Max?",
        response_mode="streaming",
        user="abc-123",
        stream=True
    ):
        print(f"收到数据块: {json.dumps(chunk, ensure_ascii=False)}")


def example_with_inputs():
    """带输入参数的示例"""
    
    client = DifyChatClient(
        base_url="http://localhost",
        api_key="your-api-key-here"
    )
    
    # 准备输入参数
    inputs = {
        "language": "zh-CN",
        "format": "detailed"
    }
    
    # 发送带输入参数的消息
    result = client.send_chat_message(
        query="介绍一下iPhone 13 Pro Max",
        inputs=inputs,
        response_mode="blocking",
        user="abc-123"
    )
    
    if result:
        print("响应结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))


def example_conversation():
    """对话上下文示例"""
    
    client = DifyChatClient(
        base_url="http://localhost",
        api_key="your-api-key-here"
    )
    
    # 第一条消息
    result1 = client.send_chat_message(
        query="我的名字是张三",
        response_mode="blocking",
        user="abc-123"
    )
    
    if result1:
        conversation_id = result1.get('data', {}).get('conversation_id', '')
        print(f"对话ID: {conversation_id}")
    
    # 第二条消息（使用相同的conversation_id）
    if 'conversation_id' in locals() and conversation_id:
        result2 = client.send_chat_message(
            query="我叫什么名字？",
            conversation_id=conversation_id,
            response_mode="blocking",
            user="abc-123"
        )
        
        if result2:
            print("响应结果:")
            print(json.dumps(result2, ensure_ascii=False, indent=2))


def main():
    """主函数 - 选择运行示例"""
    
    print("=" * 80)
    print("Dify Chat 消息发送工具")
    print("=" * 80)
    
    print("\n请选择要运行的示例:")
    print("1. 基本使用（同步模式）")
    print("2. 带文件的使用")
    print("3. 流式响应")
    print("4. 带输入参数")
    print("5. 对话上下文")
    print("6. 退出")
    
    choice = input("\n请输入选项 (1-6): ").strip()
    
    if choice == '1':
        example_basic_usage()
    elif choice == '2':
        example_with_files()
    elif choice == '3':
        example_streaming()
    elif choice == '4':
        example_with_inputs()
    elif choice == '5':
        example_conversation()
    elif choice == '6':
        print("退出程序")
    else:
        print("无效的选项")


if __name__ == "__main__":
    main()

    