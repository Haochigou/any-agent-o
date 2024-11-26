from typing import Any
import os
import re
import json
import asyncio
from datetime import datetime

from agent.infra.llm.async_chat import AsyncChat
from agent.domain.entities.chat import ChatRequest, ChatResponse
from agent import domain
from agent.domain.interfaces import scene
from agent.domain.entities import knowledge_manager


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
        self._direct_response = None

    async def __call__(self) -> Any:
        end_reason = None
        last_index = 0
        if self._direct_response is not None:
            yield "data: {'index': 0, 'content': '" + self._direct_response + "', 'finish_reason': 'stop'}\n\n"
            self._chat_response.content = self._direct_response
        else:
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
            #self._chat_response.content = re.sub(r"/", "", self._chat_response.content)
            #self._chat_response.content = self._chat_response.content.encode('utf-8').decode("unicode_escape")
            self._chat_history.load()
            self._chat_history.append({
                "role": "assistant",
                "time": datetime.now().strftime("%Y-%m-%d,%H:%M:%S"),
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
        if self._chat_request.content and len(self._chat_request.content) > 0:
            #self._chat_request.content = re.sub(r"/", "", self._chat_request.content)
            #self._chat_request.content = self._chat_request.content.encode('utf-8').decode("unicode_escape")
            self._chat_history.append({
                "role": "user",
                "time": datetime.now().strftime("%Y-%m-%d,%H:%M:%S"),
                "content": self._chat_request.content
            })
            self._chat_history.save()
        sys_prompt = ""
        if "scene" in s:
            sys_prompt += f"#scene:\n{s["scene"]}\n"
        max_history_round = 1
        if "max_history_round" not in s:
            max_history_round = target_scene["default_max_history_round"]
        else:
            max_history_round = s["max_history_round"]
        if "reference" in s and s["reference"] and self._chat_request.reference is not None:
            sys_prompt += "现在你和多个小伙伴在一起聊天，前面大家的对话信息如下：\n" + self._chat_request.reference + "\n"
            sys_prompt += f"其中当前用户的speakerId是{self._chat_request.user}\n请结合场景和当前用户进行对话\n"
            max_history_round = 2
        if "role" in s:
            sys_prompt += f"#role:\n{s["role"]}\n"
        if "task" in s:
            sys_prompt += f"#task:\n{s["task"]}\n"
        if "direct" in s and s["direct"]:
            status_file = os.path.join("data", f"status-{self._chat_request.user}-{self._chat_request.robot}.json")
            if os.path.exists(status_file):
                with open(status_file, "r") as status_handle:
                    status = status_handle.read()
                sys_prompt += f"#play direct:\n{status}\n"            
        if "knowledge" in s:            
            kbs = [item["name"] for item in s["knowledge"]]
            knowledge = knowledge_manager.kb_manager.query(self._chat_request.content, kbs)
            if knowledge is not None and len(knowledge) > 0:
                print(knowledge)
                if knowledge[0][0] < 0.12:
                    self._direct_response = knowledge[0][2]
                    return True
                else:
                    sys_prompt += """
以下是一些资料信息，请根据需要灵活运用：
1.如果对话内容和资料信息高度重复，请根据用户的问题结合资料忠实的回答。
2.如果涉及事件相关，结合资料信息的内容进行回复。
3.如果用户的问题超出资料信息的范围，用一致的语气回复。
4.在不改变基本语义和数据的情况下，以角色的语气重新组织。
"""
                    sys_prompt += "<context_reference>\n" + '\n'.join(item[1] + ":\n"+ item[2] for item in knowledge) + "\n"
                    sys_prompt += "</context_reference>\n"
        if "tools" in s:
            for tool in s["tools"]:               
                tool_script = compile(tool["python"], "string", "exec")
                exec_locals = {}
                exec(tool_script, globals(), exec_locals)
                result = exec_locals.get(tool["name"])
                sys_prompt += tool["context"].replace("{" + tool["name"] + "}", str(result)) + "\n"
                
        self._messages.append({"role":"system", "content":sys_prompt})        
        #hs = domain.get_robot_history_manager().get(user=self._chat_request.user, robot=self._chat_request.robot)
        
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
    request = ChatRequest(content="请介绍一下哈尔滨", user="kdk3232", robot="xiaoming", mode="sentence", scene="scene")
 
    ad = ChatService(request)  
    await ad.create_chat()
    response  = await ad()
    return response

if __name__ == "__main__":
    domain.init_global_resource()
    response = asyncio.run(test_chat_service())
    
    print(response)