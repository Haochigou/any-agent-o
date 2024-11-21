import asyncio
import json
import os

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from agent.domain.entities.chat import ChatRequest
from agent.app.chat_service import ChatService
from agent.app.duplex_chat_service import duplex_chat
from agent.domain.entities.milian_chat import MilianChatRequest
from agent.domain.interfaces.milian_response import get_milian_response

'''
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"now start the scheduler task in process {os.getpid()}")
    job_build_profile = scheduler.add_job(abstract_data_from_dialog, 'interval', seconds=30)
    scheduler.start()
    yield    
    scheduler.remove_job(job_build_profile.id)
    scheduler.shutdown()
'''
    
def create_fastapi():
    app = FastAPI()
    
    @app.websocket("/v1/duplex_chat/{interactive_policy_id}")
    async def websocket_endpoint(websocket: WebSocket, interactive_policy_id: str):
        await websocket.accept()
        await duplex_chat(websocket, interactive_policy_id)

    @app.post("/v1/achat")
    async def async_chat(chat: ChatRequest):
        print(chat)
        chat_service = ChatService(chat)
        for i in range(3): # 尝试3次
            try:
                if await chat_service.create_chat(i):                    
                    if chat.mode != "complete":
                        return StreamingResponse(chat_service(), media_type="text/event-stream")
                    else:
                        full_msg = ""
                        async for frame in chat_service():
                            full_msg += frame                            
                        return full_msg
            except StopAsyncIteration:
                break
            except Exception as e:
                print(f"try model index {i} error, message: {e}")
                continue
        
        raise HTTPException(status_code=404, detail="request mismatch the definition, please check your submitted scene or robot")
    
    @app.post("/v1/milian_chat")
    async def milian_chat(milian_request: MilianChatRequest):
        reference = f"""
用户档案
性别:{milian_request.gender}
年龄:{milian_request.age}
婚姻状况:{milian_request.marriage}
生育状况:{milian_request.fertilityStatus}
分娩方式:{milian_request.deliveryMethod}
抚养孩童:{str(milian_request.children).replace("childGender", "儿童性别").replace("childAge", "儿童年龄")}
最后一次月经日期:{milian_request.lastMensesDate}
月经周期:{milian_request.mensesCycle}
月经持续时间:{milian_request.mensesDuration}

问卷信息"""
        if milian_request.questionnaire and len(milian_request.questionnaire) > 0:
            for questionnaire in milian_request.questionnaire:
                reference += f"\n问卷名称:" + questionnaire["questionnaireName"]
                if questionnaire["option"] and len(questionnaire["option"]) > 0:
                    for qa in questionnaire["option"]:
                        reference += "\n" + qa["question"] + "：" + qa["answer"]
        print(reference)
        request = ChatRequest(scene="open_talk", robot="humi", mode="sentence", content=milian_request.content, user=str(milian_request.userId), reference=reference)
        '''
        req = ChatRequest(scene="open_talk",
                          user=str(milian_request.userId),
                          robot="humi",
                          content=str(milian_request.content),
                          reference=reference)
        '''
        chat_service = ChatService(request)
        for i in range(3): # 尝试3次
            print(f"loops：{i}")
            try:
                if await chat_service.create_chat(i):                 
                    
                    if request.mode != "complete":
                        return StreamingResponse(get_milian_response(traceId=milian_request.traceId, chat_service=chat_service), media_type="text/event-stream")
                    else:
                        full_msg = ""
                        async for frame in chat_service():
                            full_msg += frame                            
                        return full_msg
                
            except Exception as e:
                print(f"try model index {i} error, message: {e}")
                continue
        
        raise HTTPException(status_code=500, detail="系统错误！")
    
    return app
