from typing import Any
import re
import json
import asyncio
from datetime import datetime

from agent.infra.llm.async_chat import AsyncChat
from agent.domain.entities.chat import ChatRequest, ChatResponse
from agent import domain
from agent.domain.interfaces import scene

scenes = scene.load_scenes_from_yaml("agent/config/scene.yaml")

class ChatService():
    def __init__(self, chat_request:ChatRequest) -> None:
        self._messages = []
        self._history_len = 2
        self._chat_request = chat_request
        #self._full_msg = ""
        self._chat_response = ChatResponse(content="", finish_reason=None, request_cost=0, response_cost=0)
        self._chat_history = domain.get_robot_history_manager().get(user=self._chat_request.user,
                                                                    robot=self._chat_request.robot)

    async def __call__(self) -> Any:
        end_reason = None
        last_index = 0
        async for msg in self._async_chat.predict:
            print(msg)
            last_index = msg['index']
            rmsg = re.sub(r'/', '', json.dumps(msg))
            if msg["content"]:
                self._chat_response.content += msg["content"]
            self._chat_response.finish_reason = msg["finish_reason"]
            end_reason = msg["finish_reason"]
            yield f"data: {rmsg}\n\n"
        
        if end_reason is None:
            print("append stop for iter end msg")
            self._chat_response.finish_reason = "stop"
            last_index += 1
            yield "data: {'index': "+ str(last_index) + ", 'content': '', 'finish_reason': 'stop'}\n\n"
            
        if self._chat_response.content and len(self._chat_response.content) > 0:
            ### TODOself._chat_response.content.find()
            self._chat_history.load()
            self._chat_history.append({
                "role": "assistant",
                "time": round(datetime.now().timestamp()),
                "content": self._chat_response.content
            })
            self._chat_history.save()

        #print(self._chat_response)
        #return self._chat_response.content
    
    async def create_chat(self, model_turns = 0) -> None:
        # TODO 根据场景获取模板
        target_scene = scene.get_scene(self._chat_request.scene)
        if not target_scene:            
            # TODO 根据模板进行prompt组装
            return False
        if self._chat_request.robot not in target_scene:
            return False
        s = target_scene[self._chat_request.robot]
        self._messages.append({"role":"system", "content":"#role:\n"+s["role"]+"\ntask:\n"+s["task"]})
        #hs = domain.get_robot_history_manager().get(user=self._chat_request.user, robot=self._chat_request.robot)
        if self._chat_request.content and len(self._chat_request.content) > 0:
            self._chat_history.append({
                "role": "user",
                "time": round(datetime.now().timestamp()),
                "content": self._chat_request.content
            })
            self._chat_history.save()
        max_history_round = 1
        if "max_history_round" not in s:
            max_history_round = target_scene["default_max_history_round"]
        else:
            max_history_round = s["max_history_round"]
        
        if "models" not in s:
            models = target_scene["default_models"]
        else:
            models = s["models"]
        self._messages.extend(self._chat_history.get_context(max_history_round))
        #last = self._messages.pop()
        #new_content = "请思考：结合上下文，对我的最新请求\"" + last["content"] + "\"进行分析，" + "如果询问某个地方或景点的位置，或表达希望去某个地方时，则只需要返回一个json，格式如：{\"功能\":\"地图查询\", \"起点\":\"用户表达起点\", \"目的地\":\"用户目的地\"}即可。否则结合上下文正常回复。"
        #self._messages.append({"role":"user", "content":"请思考：结合上下文进行分析，如果询问某个地方或景点的位置，或表达希望去某个地方时，则只需要返回一个json，格式如：{\"功能\":\"地图查询\", \"起点\":\"用户表达起点\", \"目的地\":\"用户目的地\"}即可。"})
        #self._messages.append({"role":"user", "content":new_content})
        
        self._async_chat = AsyncChat(models[model_turns % len(models)]["provider"])
        print(self._messages)
        await self._async_chat.create(messages=self._messages,
                                      model=models[model_turns % len(models)]["name"],
                                      stream_mode=self._chat_request.mode,
                                      temperature=models[model_turns % len(models)]["temperature"],
                                      top_p=models[model_turns % len(models)]["top_p"]
                                      )
        return True

    def get_response(self) -> ChatResponse:
        return self._chat_response


async def test_chat_service():
    request = ChatRequest(content="你好", user="kdk3232", robot="xiaoming", mode="sentence", scene="scene")
 
    ad = ChatService(request)  
    await ad.create_chat()
    response  = await ad()
    return response

if __name__ == "__main__":
    domain.init_global_resource()
    response = asyncio.run(test_chat_service())
    
    print(response)