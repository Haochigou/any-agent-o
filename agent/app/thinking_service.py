'''
从和用户（环境）的交互中，思考并形成认知
该服务独立调度，通过数据读写和chat服务交互：
chat --- dialog ---> thinking
thinking --- cognition memory ---> chat

针对用户的认知记忆格式如下：
[refresh_timestamp:99999999]
[user information]
name:xxxxx
gender:xxxx
birthday:9999-99-99
[]


'''
from typing import Any
import re
import json
import asyncio
import os
from datetime import datetime
import multiprocessing

from agent.infra.llm.async_chat import AsyncChat
from agent.domain.entities.chat import ChatRequest, ChatResponse
from agent import domain
from agent.domain.interfaces import scene
from agent.domain.entities import knowledge_manager

scenes = scene.load_scenes_from_yaml("agent/config/scene.yaml")
g_profile_build_multiproc_lock = multiprocessing.Lock()

class ToolService():
    def __init__(self, chat_request:ChatRequest) -> None:
        self._messages = []
        self._history_len = 2
        self._chat_request = chat_request
        #self._full_msg = ""
        self._chat_response = ChatResponse(content="", finish_reason=None, request_cost=0, response_cost=0)
        #self._chat_history = domain.get_robot_history_manager().get(user=self._chat_request.user,
        #                                                            robot=self._chat_request.robot)

    async def __call__(self) -> Any:
        async for msg in self._async_chat.predict:
            # print(msg)
            rmsg = re.sub(r'/', '', json.dumps(msg)).encode('utf-8').decode('unicode_escape')
            if msg["content"]:
                self._chat_response.content += msg["content"]
            self._chat_response.finish_reason = msg["finish_reason"]
            
            #yield f"data: {rmsg}\n\n"
        return self._chat_response.content
    
    async def create(self, model_turns = 0) -> None:
        # TODO 根据场景获取模板
        target_scene = scene.get_scene(self._chat_request.scene)
        if not target_scene:            
            # TODO 根据模板进行prompt组装
            return False
        if self._chat_request.robot not in target_scene:
            return False
        s = target_scene[self._chat_request.robot]
        sys_prompt = ""
        if "scene" in s:
            sys_prompt += f"#scene:\n{s["scene"]}\n"
        if "role" in s:
            sys_prompt += f"#role:\n{s["role"]}\n"
        if "task" in s:
            sys_prompt += f"#task:\n{s["task"]}\n"
        if "knowledge" in s:            
            kbs = [item["name"] for item in s["knowledge"]]
            knowledge = knowledge_manager.kb_manager.query(self._chat_request.content, kbs)
            if knowledge is not None and len(knowledge) > 0:
                if knowledge[0][0] < 0.1:
                    self._direct_response = knowledge[0][2]
                    return True
                else:
                    sys_prompt += "以下是一些资料信息，请根据需要灵活运用：\n\
1.如果对话内容和资料信息高度重复，请根据用户的问题结合资料忠实的回答。\n\
2.如果涉及事件相关，结合资料信息的内容进行回复。\n\
3.如果用户的问题超出资料信息的范围，用一致的语气回复。\n\
4.在不改变基本语义和数据的情况下，以角色的语气重新组织。\n"
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
        self._messages.append({"role":"user", "content":self._chat_request.content})
        
        if "models" not in s:
            models = target_scene["default_models"]
        else:
            models = s["models"]
        
        
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


async def test_tool_service():
    request = ChatRequest(content="你好", user="kdk3232", robot="xiaoming", mode="sentence", scene="scene")
 
    ad = ToolService(request)  
    await ad.create_chat()
    response  = await ad()
    return response


async def abstract_data_from_dialog():
    '''
    global g_profile_build_multiproc_lock
    if not g_profile_build_multiproc_lock.acquire():
        return
    '''
    try:
        dialog_src_dir = "chat-history"
        data_dir = "data"
        paths = os.walk(dialog_src_dir)
        #processed = {1}
        print("scan begin")
        for path, dir_lst, file_lst in paths:
            for file_name in file_lst:
                if os.path.exists(os.path.join(data_dir, file_name.replace("dialogue", "status"))):
                    history_timestamp = os.path.getmtime(os.path.join(path, file_name))            
                    status_timestamp = os.path.getmtime(os.path.join(data_dir, file_name.replace("dialogue", "status")))
                    #print(f"history:{history_timestamp}, status:{status_timestamp}")
                    if history_timestamp < status_timestamp:
                        continue
                '''
                if file_name in processed:
                    continue
                processed.add(file_name)
                '''
                print(f"dir:{path}, file:{file_name}")
                
                with open(os.path.join(path, file_name), "r") as history_handle:
                    history = history_handle.read()
                    request = ChatRequest(scene="tools", robot="profile_build", mode="complete", content=history, user="")
                    tool = ToolService(request)
                    await tool.create()
                    result = await tool()
                    result = result.split('\\n')
                    print(f"dir:{path}, file:{file_name}")
                
                profile_name = file_name.replace('dialogue', 'profile')
                status_name = file_name.replace('dialogue', 'status')
                with open(os.path.join("data", profile_name), "a+") as profile:
                    profile.writelines('\n'.join(result[0:-1]))
                with open(os.path.join("data", status_name), "w") as status:
                    print(result[-1])
                    status.write(result[-1])
                
    finally:
        #g_profile_build_multiproc_lock.release()
        print("profile build finish!")

def job_build_profile():
    while True:
        asyncio.run(abstract_data_from_dialog)
        asyncio.sleep(10)
    
if __name__ == "__main__":
    #domain.init_global_resource()
    #response = asyncio.run(test_tool_service())
    
    #print(response)
    job_build_profile()