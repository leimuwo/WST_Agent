      
from test import DifyChatClient
import json

client = DifyChatClient('http://localhost', 'app-fCE9IH9pdKqDzOZnMcv8HS0x')

result = client.send_chat_message(
    query='你好，请解释一下这段代码：print("Hello World")',
    response_mode='blocking'
)

if result:
    print("连接成功！响应结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
else:
    print("连接失败")

    