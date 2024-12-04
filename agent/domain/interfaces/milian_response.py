import json

import uuid

from agent.domain.entities.chat import ChatResponse
from agent.domain.entities.chat import ChatRequest
from agent.app.chat_service import ChatService
from agent.infra.utils.packed_ulid import get_packed_ulid

def detect_content_type(content: str):
    start = content.find("{")
    if start >= 0:
        content = content[start:]
    start = content.find("[")
    if start >= 0:
        content = content[start:]
    if content.startswith("{") and content.rstrip("\n").endswith("}"):
        if "lastMenses" in content:
            return 2
        if "cardTag" in content:
            return 4
    elif content.startswith("[") and content.rstrip("\n").endswith("]"):
        return 5
    else:
        return 1

async def get_milian_response(traceId: str, chat_service: ChatService):    
    messageId = uuid.uuid1()
    is_start = "true"
    total = ""
    async for x in chat_service():
        try:
            #x = await chat_service().__anext__()
            raw_response = json.loads(x.strip("data:"))
            content = raw_response["content"]
            
            type = detect_content_type(content)
            if type != 1:
                start = content.find("{")
                if start > 0:
                    content = content[start:]
                start = content.find("[")
                if start > 0:
                    content = content[start:]
            if type != 2:
                milian_response = "data: {" + f"\"messageId\":\"{messageId}\",\"isStart\":{is_start}, \"isEnd\":false, \"traceId\":\"{traceId}\",\"userId\":{chat_service._chat_request.user},\"responseType\":{type},\"content\":\"{content}\",\"finishReason\":\"null\"" + "}\n\n"
                is_start = "false"
            else:                
                content = content.replace("\\\"", "\"")
                milian_response = "data: {" + f"\"messageId\":\"{messageId}\",\"isStart\":false, \"isEnd\":false, \"traceId\":\"{traceId}\",\"userId\":{chat_service._chat_request.user},\"responseType\":{type},\"content\":\"\",\"extend\":{content}, \"finishReason\":\"null\"" + "}\n\n"
            if type == 1:
                total += content
            yield milian_response
        except StopAsyncIteration:           
            break
        except Exception as e:
            print(e)
            break
            # TODO 追加后续处理，如完成返回内容等
    milian_response = "data: {" + f"\"messageId\":\"{messageId}\",\"isStart\":{is_start}, \"isEnd\":true, \"traceId\":\"{traceId}\",\"userId\":{chat_service._chat_request.user},\"responseType\":99,\"content\":\"{total}\",\"finishReason\":\"stop\"" + "}\n\n"
    yield milian_response