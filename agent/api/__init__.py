from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from agent.domain.entities.chat import ChatRequest
from agent.app.chat_service import ChatService

def create_fastapi():
    app = FastAPI()

    @app.post("/v1/achat")
    async def async_chat(chat: ChatRequest):
        chat_service = ChatService(chat)
        if await chat_service.create_chat():
            return StreamingResponse(chat_service(), media_type="text/event-stream")
        else:
            raise HTTPException(status_code=404, detail="request mismatch the definition, please check your submitted scene or robot")
    
    return app
