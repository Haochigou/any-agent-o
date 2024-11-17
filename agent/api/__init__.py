import asyncio
import json

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from agent.domain.entities.chat import ChatRequest, ChatMessagesRequest
from agent.app.chat_service import ChatService
from agent.app.duplex_chat_service import duplex_chat
from dao.chat_history_service import ChatHistoryService
from dao.entity.chat_history import ChatHistory
from dao.user_service import UserService


def create_fastapi():
    app = FastAPI()

    @app.websocket("/v1/duplex_chat/{interactive_policy_id}")
    async def websocket_endpoint(websocket: WebSocket, interactive_policy_id: str):
        await websocket.accept()
        await duplex_chat(websocket, interactive_policy_id)

    @app.post("/v1/achat")
    async def async_chat(chat: ChatRequest):
        chat_service = ChatService(chat)
        for i in range(3):  # 尝试3次
            try:
                if await chat_service.create_chat(i):
                    # return StreamingResponse(chat_service(), media_type="text/event-stream")

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

        raise HTTPException(status_code=404,
                            detail="request mismatch the definition, please check your submitted scene or robot")

    @app.get("/test")
    async def test():
        return "test ok"

    @app.post("/v1/chat-messages")
    async def chat_messages(chatMessage: ChatMessagesRequest):
        # chat.query: {"toy": {"id": "f09e9e01655c", "status": "待售"}, "speaker": {"id": "97758ac0-ea41-493f-a8ec-f0538ec21a3a", "first_time": false, "gender": "男性", "age": "中年"}, "stt": {"text": "你好！"}}

        userService = UserService()
        userObj = userService.getUserByUsername(username=chatMessage.user)
        userId = userObj.id;

        queryObj = json.loads(chatMessage.query)
        toy = queryObj["toy"]
        status = toy["status"]  # 售卖状态：待售、

        speaker = queryObj["speaker"]
        speakerId: str = speaker["id"];
        age = speaker["age"];
        gender = speaker["gender"];
        content: str = queryObj["stt"]["text"];
        print(
            f"user: {chatMessage.user}, conversation_id: {chatMessage.conversation_id}, userId: {userId}, speakerId: {speakerId}, age: {age}, gender: {gender}, content: {content}")


        chat = ChatRequest()
        chat.scene = "open_talk";
        chat.user = str(userId)
        chat.conversation_id = chatMessage.conversation_id
        chat.robot = "taotao";
        chat.mode = "sentence";
        chat.content = content

        chatHistoryService = ChatHistoryService()
        chatHistoryService.save(userId=userId, sessionId="", roleType=1, speakerId=speakerId, content=content)

        def fake_video_stream():
            for i in range(3):
                yield "data: {\"event\": \"message\", \"answer\": \"123" + str(i) + "\"}\n\n"
            yield "data: {\"event\": \"message_end\"}\n\n"

        return StreamingResponse(fake_video_stream(), media_type="text/event-stream")

    return app
