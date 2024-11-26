import json

from dao.chat_history_service import ChatHistoryService
from dao.toy_master_service import ToyMasterService
from agent.app.user_status_service import userStatusService

class ChatContext:
    scene: str = "stranger"
    history: str

    def __init__(self, scene: str, history: []):
        self.scene = scene
        self.history = history

    def __repr__(self):
        return f"{self.scene}: {self.history}"

class ChatContextService:

    def getChatContext(self, userId: int, speakerId: str, sellStatus: str) -> ChatContext:
        """
        stranger: 待售
        friend: 已售
        master: 主人聊天场景
        try_master: 尝试认主场景
        """
        chatHistoryService = ChatHistoryService()
        userStatus = userStatusService.getUserStatus(userId=userId)
        if len(userStatus.speakers)>1: # 多人聊天
            history: [] = chatHistoryService.getRecentHistory(userId)
            return ChatContext("stranger", json.dumps(history, ensure_ascii=False))

        history: str = ""
        if "待售" == sellStatus:
            return ChatContext("stranger", history)

        if self.isMaster(userId=userId, speakerId=speakerId):
            # 已认主，和主人聊天
            return ChatContext("master", history)

        if self.needTryMaster(userId=userId, speakerId=speakerId):
            # 进入认主场景
            return ChatContext("try_master", history)

        # 已售时的聊天场景
        return ChatContext(scene="friend", history=history)

    def isMaster(self, userId: int, speakerId: str) -> bool:
        toyMasterService = ToyMasterService()
        return toyMasterService.isMaster(userId=userId, speakerId=speakerId)

    def needTryMaster(self, userId: int, speakerId: str) -> bool:
        """
            1. 每24小时触发一次
            2. 如果拒绝了，12小时后再触发一次
        """
        if userStatusService.tryMaster(userId=userId, speakerId=speakerId):
            return True

        return False