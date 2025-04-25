from fastapi import FastAPI, Request, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketState
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import json
from typing import Union, Literal, TypedDict
import asyncio
from loguru import logger
import os
from dotenv import load_dotenv

from tools import tools, tool_schemas, metadata_map
import threading
from openai import AzureOpenAI
import sys

# sys.path.append("/home/azureuser/projects/Govee AI Agent Backend/")
from rtclient.prompts import get_system_prompt

load_dotenv()

class UserRequest(BaseModel):
    content: str

class UserAgent:
    def __init__(self, user_id):
        self.user_id = user_id
        self.chat_msgs = []
        self.logger = logger.bind(user_id=self.user_id)
        self.chat_client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_VERSION"),
        )
        self.logger.info("New user agent created")
        self.system_role = get_system_prompt()
        # self.logger.info("System role initialized: %s", self.system_role)
        print("System role initialized: %s", self.system_role)

    async def chat(self, content=None):
        if content:
            self.chat_msgs.append({"role": "user", "content": content})
            print(f"Request: {content}")
        messages = [{"role": "system", "content": self.system_role}]
        # print(messages)
        messages.extend(self.chat_msgs[-20:])
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
        response_message = response.choices[0].message
        print(f"Response: {response_message.content}")

        prompt_tokens = response.usage.prompt_tokens  # 输入消耗的tokens
        completion_tokens = response.usage.completion_tokens  # 输出消耗的tokens
        total_tokens = response.usage.total_tokens  # 总消耗tokens

        print(f"\nToken 统计:")
        print(f"输入tokens: {prompt_tokens}")
        print(f"输出tokens: {completion_tokens}")
        print(f"总计tokens: {total_tokens}")

        # 如果需要记录到日志或数据库
        self.logger.info(f"API调用token统计 - 输入: {prompt_tokens}, 输出: {completion_tokens}, 总计: {total_tokens}")
        
        if response_message.tool_calls:
            # First append the assistant message with tool calls
            tool_call_msg = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in response_message.tool_calls
                ]
            }
            self.chat_msgs.append(tool_call_msg)
            
            # Then handle each tool call and append the tool response
            for tool_call in response_message.tool_calls:
                func_name = tool_call.function.name
                metadata = metadata_map.get(func_name)
                
                args = {}
                if tool_call.function.arguments:
                    args = json.loads(tool_call.function.arguments)
                
                # Get function name and args but don't call the handler
                print(f"func: {func_name}, args: {args}")
                
                # Instead of calling the function, just return the function name and arguments
                func_result = json.dumps({
                    "function": func_name,
                    "arguments": args
                })
                
                # Append tool response with the correct tool_call_id
                self.chat_msgs.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": func_result,
                    }
                )
            
            return {
                "args": args,
                "function": func_name
            }
        else:
            return {}

class UserAgentManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(UserAgentManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_users'):
            self._users = {}
            self._users_lock = threading.Lock()

    def get_user(self, user_id):
        with self._users_lock:
            if user_id not in self._users:
                self._users[user_id] = UserAgent(user_id)
            return self._users[user_id]    

app = FastAPI()
agent_manager = UserAgentManager()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"success": True}

@app.post("/request")
def request(request: Request, req: UserRequest):
    token = request.headers.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="User token not found in header")
    
    user_id = extract_user_id(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Cannot read valid user id from token")
    user_agent = agent_manager.get_user(user_id)
    resp = asyncio.run(user_agent.chat(req.content))
    
    return {"response": resp}

def extract_user_id(token: str) -> str:
    return token


if __name__ == "__main__":
    # port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")




