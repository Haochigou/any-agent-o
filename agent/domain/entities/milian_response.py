import json

from agent.domain.entities.chat import ChatResponse
from agent.domain.entities.chat import ChatRequest
from agent.app.chat_service import ChatService

def check_content_type(content: str):
    return 1

async def get_milian_response(traceId: str, chat_service: ChatService):
    fullmsg = ""
    while True:
        try:
            x = await chat_service().__anext__()
            raw_response = json.loads(x.strip("data:"))
            content = raw_response["content"]
            
            type = check_content_type(content)
            
            milian_response = "data: {" + f"\"traceId\":\"{traceId}\",\"userId\":{chat_service._chat_request.user},\"responseType\":{type},\"content\"=\"{content}\",\"finishReason\":\"null\"" + "}\n\n"
            yield milian_response
        except Exception as e:
            #print(e)
            break
            # TODO 追加后续处理，如完成返回内容等
    milian_response = "data: {" + f"\"traceId\":\"{traceId}\",\"userId\":{chat_service._chat_request.user},\"responseType\":99,\"content\"=\"{chat_service._chat_response.content}\",\"finishReason\":\"stop\"" + "}\n\n"
    yield milian_response