import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, Header
from fastapi.responses import StreamingResponse

import config
from agent.app.chat_context_service import ChatContextService
from agent.app.user_status_service import userStatusService
from agent.domain.entities.chat import ChatRequest, ChatMessagesRequest
from agent.app.chat_service import ChatService
from agent.app.duplex_chat_service import duplex_chat
from dao.chat_history_service import ChatHistoryService
from dao.toy_master_service import ToyMasterService
from dao.user_service import UserService
from agent.infra.log.local import getLogger
from redis import Redis

logger = getLogger("chat")

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis.from_url(config.REDIS_URL)
    yield
    # await app.state.redis.close()

app.router.lifespan_context = lifespan

def get_redis_client()-> Redis:
    return app.state.redis

def create_fastapi():


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
                logger.error(f"try model index {i} error, message: {e}")
                continue

        raise HTTPException(status_code=404,
                            detail="request mismatch the definition, please check your submitted scene or robot")

    @app.get("/test")
    async def test():
        return "test ok"

    @app.post("/v1/chat-messages")
    async def chat_messages(chatMessage: ChatMessagesRequest,
                            token: str = Header(alias="Authorization", default="default_token")):
        token = token.replace("Bearer ", "")
        if token != "61fa181f-84b1-f840-de58-7994399eb3b4":
            # raise HTTPException(status_code=401, detail="认证失败")
            pass

        userStatusService.redis = get_redis_client()

        # chat.query: {"toy": {"id": "f09e9e01655c", "status": "待售"}, "speaker": {"id": "97758ac0-ea41-493f-a8ec-f0538ec21a3a", "first_time": false, "gender": "男性", "age": "中年"}, "stt": {"text": "你好！"}}
        logger.info(f"query: {chatMessage.query}")
        userService = UserService()
        userObj = userService.getUserByUsername(username=chatMessage.user)
        userId = userObj.id;

        queryObj = json.loads(chatMessage.query)
        toy = queryObj.get("toy", {"id": "f09e9e01655c", "status": "待售"})
        status = toy.get("status", "待售")  # 售卖状态：待售、

        speaker = queryObj.get("speaker",
                               {"id": "97758ac0-ea41-493f-a8ec-f0538ec21a3a", "first_time": False, "gender": "男性",
                                "age": "中年"})
        speakerId: str = speaker.get("id", "default_speaker");
        speakerId: str = speaker.get("id", f"{userId}.default_speaker");
        if not speakerId:
            speakerId = f"{userId}.default_speaker"
        age = speaker["age"];
        if age is None:
            age = "中年"
        gender = speaker["gender"];
        if gender is None:
            gender = "男性"

        content: str = queryObj["stt"]["text"];
        logger.info(
            f"user: {chatMessage.user}, status: {status}, userId: {userId}, speakerId: {speakerId}, age: {age}, gender: {gender}, content: {content}")


        userStatus = userStatusService.updateSession(userId=userId, speakerId=speakerId)

        chatHistoryService = ChatHistoryService()
        chatHistoryService.save(userId=userId, sessionId=userStatus.sessionId, roleType=1, speakerId=speakerId, content=content)

        chatContextService = ChatContextService()
        chatContext = chatContextService.getChatContext(userId=userId, speakerId=speakerId, sellStatus=status)
        logger.info(f"chatContext: {chatContext}")

        chat = ChatRequest(content=content, user=str(userId), robot="taotao", mode="sentence", scene=chatContext.scene,
                           reference={
                               "age": age,
                               "gender": gender,
                               "meeting": chatContext.history
                           })

        chat_service = ChatService(chat)

        async def resp_stream():
            if await chat_service.create_chat(1):
                rawContent: str = ""
                haveCmd: bool = False
                cmdContent: str = ""
                while True:
                    resp = await chat_service().__anext__()
                    if resp is None:
                        break

                    # "data: {'index': 0, 'content': '" + self._direct_response + "', 'finish_reason': 'stop'}\n\n"
                    respObj = json.loads(resp.strip("data:"))
                    status = respObj["finish_reason"]
                    if status == "stop":
                        respContent = respObj["content"]
                        yield "data: {\"event\": \"message\", \"answer\": \"" + respContent + "\"}\n\n"
                        break
                    else:
                        respContent = respObj["content"]
                        rawContent += respContent;

                        if -1 != respContent.find("{") and respContent.find("}") != -1:
                            # 指令全部内容在内容中间
                            left = respContent.find("{")
                            right = respContent.find("}")
                            cmdContent = respContent[left:right + 1]
                            leftContent = respContent[0:left]
                            rightContent = respContent[right + 1:]
                            yield "data: {\"event\": \"message\", \"answer\": \"" + leftContent + rightContent + "\"}\n\n"
                            continue

                        if haveCmd != True and -1 != respContent.find("{"):
                            # 只有指令前面部分内容
                            haveCmd = True
                            index = respContent.find("{")
                            leftContent = respContent[0:index]
                            cmdContent += respContent[index:]
                            yield "data: {\"event\": \"message\", \"answer\": \"" + leftContent + "\"}\n\n"
                            continue

                        if haveCmd and -1 != respContent.find("}"):
                            # 只有指令后半部分内容
                            index = respContent.find("}")
                            cmdContent += respContent[0:index + 1]
                            rightContent = respContent[index + 1:]
                            yield "data: {\"event\": \"message\", \"answer\": \"" + rightContent + "\"}\n\n"
                            continue

                        yield "data: {\"event\": \"message\", \"answer\": \"" + respContent + "\"}\n\n"
                if rawContent:
                    chatHistoryService.save(userId=userId, sessionId=userStatus.sessionId, roleType=0, speakerId=speakerId,
                                            content=rawContent)
                if cmdContent:
                    cmdContent = cmdContent.replace("\\", "")
                    logger.info(f"cmdContent: {cmdContent}")
                    cmdObj = json.loads(cmdContent)
                    cmdStatus = cmdObj.get("status")
                    if "accept" == cmdStatus and "try_master" == chatContext.scene: # 只有认主场景的时候，可以认主。
                        toyMasterService = ToyMasterService()
                        toyMasterService.addToyMaster(userId=userId, masterId=speakerId)
                    elif "reject" == cmdStatus:
                        userStatusService.rejectMaster(userId=userId, speakerId=speakerId)

            yield "data: {\"event\": \"message_end\"}\n\n"

        return StreamingResponse(resp_stream(), media_type="text/event-stream")

    return app
