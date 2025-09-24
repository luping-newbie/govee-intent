from typing import Literal, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import json
from loguru import logger
import os
from dotenv import load_dotenv

from rtclient.labels import get_map_dict
from rtclient.prompts import get_system_prompt

from tools import tool_schemas, metadata_map  # 假设这些模块仍然需要
from openai import AzureOpenAI

from utils import anonymize_text

load_dotenv()

class Message(BaseModel):
    role: Literal["user", "assistant"]  # 必须为这两种角色
    content: str                        # 消息内容（建议限制在500字符内）

class UserRequest(BaseModel):
    content: str                        # 当前用户消息
    history: List[Message] = []         # 历史消息列表（按时间顺序排列）


class ChatProcessor:
    def __init__(self):
        self.logger = logger
        self.chat_client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_VERSION"),
        )
        self.system_role = get_system_prompt()
        logger.info("Chat processor initialized")



    def process_chat(self, request):
        # messages = [
        #     {"role": "system", "content": self.system_role},
        #     {"role": "user", "content": content}
        # ]

        messages = [{"role": "system", "content": self.system_role}]

        # 添加验证后的历史消息（自动截断和过滤）
        validated_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history[-10:]  # todo 保留最近10条
            if msg.role in ("user", "assistant")
        ]
        print(validated_history)
        messages.extend(validated_history)

        # 添加当前消息
        format_content =anonymize_text(request.content)# 邮件地址信息过滤
        messages.append({"role": "user", "content": format_content})

        chat_tools = [
            {
                "type": "function",
                "function": {
                    "name": func["name"],
                    "description": func["description"],
                    "parameters": func["parameters"],
                },
            }
            for func in tool_schemas
        ]

        response = self.chat_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            messages=messages,
            tools=chat_tools,
            tool_choice="auto",
            stream=False,
            temperature=0.00000001,
            top_p=0.00000001
        )

        return self._handle_response(response)

    def _handle_response(self, response):
        response_message = response.choices[0].message
        logger.info(f"API响应内容: {response_message.content}")
        result = {
            "func_name": None,
            "args": {}}

        # Token统计（保持原有功能）
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        logger.info(f"Token使用 - 输入: {prompt_tokens}, 输出: {completion_tokens}")

        # 处理工具调用
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]  # 取第一个工具调用
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

            logger.info(f"检测到工具调用: {func_name}，参数: {args}")

            result["func_name"] = func_name
            result["args"] = args
        else:
            try:
                content =json.loads(response_message.content)
                issue_label = (content.get("issue_label", [])[0] if isinstance(content, dict) else None)
                result["args"]["issue_label"]=issue_label
            except Exception as e:
                print(response_message.content)

        return result


app = FastAPI()
chat_processor = ChatProcessor()

# CORS中间件（保持原有配置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/request")
async def handle_request(req: UserRequest):
    try:
        result = chat_processor.process_chat(req)
        print(result)
        issue_label = result.get('args', {}).get('issue_label')
        if not issue_label:
            result["label"]="其他"
        else:
            # 使用之前创建的映射关系获取 一级类别
            result["label"] = get_map_dict().get(issue_label,"其他")
        return JSONResponse(content={"response": result})
    except Exception as e:
        logger.error(f"处理请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/notification")
async def handle_notification(request: Request):
    try:
        data = await request.json()
        print(f"收到通知: {data}")
        # data = await request.json()
        # data = "收到通知"
        return {"status": "success", "received": data}
    except Exception as e:
        logger.error(f"处理请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@app.get("/health")
def health_check():
    return {"status": "ok", "version": os.getenv("VERSION", "1.0")}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info", workers=4)
