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
        async for msg in self._async_chat.predict:
            # print(msg)
            rmsg = re.sub(r'/', '', json.dumps(msg)).encode('utf-8').decode('unicode_escape')
            if msg["content"]:
                self._chat_response.content += msg["content"]
            self._chat_response.finish_reason = msg["finish_reason"]
            
            yield f"data: {rmsg}\n\n"
            
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
    
    async def create_chat(self) -> None:
        # TODO 根据场景获取模板
        s = scene.get_scene(self._chat_request.scene)
        if not s:            
            # TODO 根据模板进行prompt组装
            return False
        if self._chat_request.robot not in s:
            return False
        s = s[self._chat_request.robot]
        self._messages.append({"role":"system", "content":"#role:\n"+s["role"]+"\ntask:\n"+s["task"]})
        #hs = domain.get_robot_history_manager().get(user=self._chat_request.user, robot=self._chat_request.robot)
        if self._chat_request.content and len(self._chat_request.content) > 0:
            self._chat_history.append({
                "role": "user",
                "time": round(datetime.now().timestamp()),
                "content": self._chat_request.content
            })
            self._chat_history.save()
        self._messages.extend(self._chat_history.get_context(s["max_history_round"]))
        self._async_chat = AsyncChat(s["models"][1]["provider"])
        print(self._messages)
        await self._async_chat.create(messages=self._messages,
                                      model=s["models"][1]["name"],
                                      stream_mode=self._chat_request.mode,
                                      temperature=s["models"][1]["temperature"],
                                      top_p=s["models"][1]["top_p"]
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