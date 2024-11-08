import asyncio
import json

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from agent.domain.entities.chat import ChatRequest
from agent.app.chat_service import ChatService
from agent.app.duplex_chat_service import duplex_chat

def create_fastapi():
    app = FastAPI()
    
    @app.websocket("/v1/duplex_chat/{interactive_policy_id}")
    async def websocket_endpoint(websocket: WebSocket, interactive_policy_id: str):
        await websocket.accept()
        await duplex_chat(websocket, interactive_policy_id)

    @app.post("/v1/achat")
    async def async_chat(chat: ChatRequest):
        chat_service = ChatService(chat)
        for i in range(3): # 尝试3次
            try:
                if await chat_service.create_chat(i):
                    #return StreamingResponse(chat_service(), media_type="text/event-stream")
                    
                    if chat.mode != "complete":
                        return StreamingResponse(chat_service(), media_type="text/event-stream")
                    else:
                        full_msg = ""
                        async for frame in chat_service():
                            full_msg += frame                            
                        return full_msg
                
            except Exception as e:
                print(f"try model index {i} error, message: {e}")
                continue
        
        raise HTTPException(status_code=404, detail="request mismatch the definition, please check your submitted scene or robot")
    
    return app
