#!/usr/bin/env python

import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect

from agent.domain.entities.chat import ChatRequest
from agent.app.chat_service import ChatService

PROACTIVELY_INQUIRE_TIME_THRESHOLD = 10 # seconds
INTERACTION_TIMEOUT_THRESHOLD = 60 # seconds

async def duplex_chat(websocket: WebSocket, interactive_policy_id: str):
    print(interactive_policy_id)
    # TODO 使用交互策略id来获取交互策略
    last_interaction_acc_time = 0
    while True:
        try:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=PROACTIVELY_INQUIRE_TIME_THRESHOLD)
                last_interaction_acc_time = 0 # 重置计时器                
                #request = json.loads(data)
                chat = ChatRequest(robot="taotao", user=interactive_policy_id, scene="stranger", mode="sentence", content=data)
                    
                chat_service = ChatService(chat)
                await chat_service.create_chat(1)
                async for msg in chat_service():
                    print(msg)
                    jmsg = json.loads(msg.strip('data:'))
                    if len(jmsg["content"]) > 0:
                        await websocket.send_text(f"play{jmsg["content"]}")
            except asyncio.TimeoutError:
                # 处理一定时间未响应的逻辑，如打招呼等
                print("active time")
                last_interaction_acc_time += PROACTIVELY_INQUIRE_TIME_THRESHOLD
                if last_interaction_acc_time >= INTERACTION_TIMEOUT_THRESHOLD:
                    await websocket.close()
                    break
                #await websocket.send_text("{'index': 0" + ", 'content': 'hi, 还在吗？', 'finish_reason': 'stop'}\n\n")
                await websocket.send_text("playhi, 还在吗？")
        except WebSocketDisconnect:
            await websocket.close()
            break