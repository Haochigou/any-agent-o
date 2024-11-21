import json

import uuid

from agent.domain.entities.chat import ChatResponse
from agent.domain.entities.chat import ChatRequest
from agent.app.chat_service import ChatService
from agent.infra.utils.packed_ulid import get_packed_ulid

def detect_content_type(content: str):
    return 1

async def get_milian_response(traceId: str, chat_service: ChatService):    
    messageId = uuid.uuid1()
    is_start = "true"
    async for x in chat_service():
        try:
            #x = await chat_service().__anext__()
            raw_response = json.loads(x.strip("data:"))
            content = raw_response["content"]
            
            type = detect_content_type(content)
            
            milian_response = "data: {" + f"\"messageId\":\"{messageId}\",\"isStart\":{is_start}, \"isEnd\":false, \"traceId\":\"{traceId}\",\"userId\":{chat_service._chat_request.user},\"responseType\":{type},\"content\":\"{content}\",\"finishReason\":\"null\"" + "}\n\n"
            is_start = "false"
            yield milian_response
        except StopAsyncIteration:           
            break
        except Exception as e:
            print(e)
            break
            # TODO 追加后续处理，如完成返回内容等
    milian_response = "data: {" + f"\"messageId\":\"{messageId}\",\"isStart\":{is_start}, \"isEnd\":true, \"traceId\":\"{traceId}\",\"userId\":{chat_service._chat_request.user},\"responseType\":99,\"content\":\"{chat_service._chat_response.content}\",\"finishReason\":\"stop\"" + "}\n\n"
    yield milian_response