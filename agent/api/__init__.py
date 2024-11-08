from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from agent.domain.entities.chat import ChatRequest
from agent.app.chat_service import ChatService
from agent.domain.entities.ws_manager import ws_manager

def create_fastapi():
    app = FastAPI()

    @app.websocket("/v1/dulex_chat/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        await websocket.accept()
        ws_manager.connect(client_id, websocket)

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
