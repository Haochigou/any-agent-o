import json

import uuid

from agent.domain.entities.chat import ChatResponse
from agent.domain.entities.chat import ChatRequest
from agent.app.chat_service import ChatService
from agent.infra.utils.packed_ulid import get_packed_ulid

recommand = {"情感陪伴——放松舒缓催眠冥想", "JIMI肌密公主痛经贴", "凯格尔运动——核心训练", "私密花园——黄金三角区激活", "身体魅力训练——自由舞动", "爱道灵动运动——108动"}

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
    cards = None
    async for x in chat_service():
        try:
            #x = await chat_service().__anext__()
            raw_response = json.loads(x.strip("data:"))
            print(raw_response)
            if raw_response["finish_reason"] is not None:
                print(cards)
                chat_service._chat_response.content = total + (f"\n自我提醒：我已经为用户生成了cardTag为：{cards} 的推荐内容，后面无论用户怎么表达，我都不能再生成同样的内容，否则用户会厌烦。" if cards else "")
                print(chat_service._chat_response.content)
            content = raw_response["content"]
            pre_content = None
            type = detect_content_type(content)
            if type != 1:
                start = content.find("{")
                if start > 0:
                    pre_content = content[0:start-1]
                    content = content[start:]
                start = content.find("[")
                if start > 0:
                    pre_content = content[0:start-1]
                    content = content[start:]
            if pre_content is not None:
                milian_response = "data: {" + f"\"messageId\":\"{messageId}\",\"isStart\":{is_start}, \"isEnd\":false, \"traceId\":\"{traceId}\",\"userId\":{chat_service._chat_request.user},\"responseType\":1,\"content\":\"{pre_content}\",\"finishReason\":\"null\"" + "}\n\n"
                yield milian_response
                total += pre_content
                is_start = "false"
            if type != 2:
                milian_response = "data: {" + f"\"messageId\":\"{messageId}\",\"isStart\":{is_start}, \"isEnd\":false, \"traceId\":\"{traceId}\",\"userId\":{chat_service._chat_request.user},\"responseType\":{type},\"content\":\"{content}\",\"finishReason\":\"null\"" + "}\n\n"
                is_start = "false"
                if type != 1 and type != 5:
                    item = json.loads(content.replace("\\\"","\""))
                    if item["cardTag"] not in recommand:
                        continue
                    if any(history["content"].find(item["cardTag"]) >= 0 for history in chat_service._chat_history.get_context(15)):
                        continue
                    if cards is None:
                        cards = str(item["cardTag"])
                    else:
                        cards += "," + str(item["cardTag"])
                    
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