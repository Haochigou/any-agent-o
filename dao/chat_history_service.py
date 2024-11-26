from sqlalchemy import desc

from dao import db_util
from dao.entity.chat_history import ChatHistory


class ChatHistoryService:
    def save(self, chatHistory: ChatHistory):
        with db_util.getSession() as session:
            session.add(chatHistory)
            session.commit()

    def save(self, userId, sessionId, roleType, speakerId, content):
        chatHistory = ChatHistory()
        chatHistory.userId = userId
        chatHistory.sessionId = sessionId
        chatHistory.roleType = roleType
        chatHistory.speakerId = speakerId
        chatHistory.content = content
        with db_util.getSession() as session:
            session.add(chatHistory)
            session.commit()


    def getSpeakerRecentHistory(self, userId: int, speakerId: str)->[ChatHistory]:
        with (db_util.getSession() as session):
            obj = session.query(ChatHistory).filter_by(userId=userId, speakerId=speakerId
                                                           ).order_by(desc(ChatHistory.createTime)).offset(0).limit(8)
            return self.convert(obj)

        return []


    def getRecentHistory(self, userId: int)->[ChatHistory]:
        with (db_util.getSession() as session):
            obj = session.query(ChatHistory).filter_by(userId=userId).order_by(desc(ChatHistory.createTime)).offset(0).limit(8)
            return self.convert(obj)

        return []

    def convert(self, items):
        arr = []
        for item in items:
            if not item.content:
                continue
            if item.roleType == 1:
                arr.append({
                    "role": "user",
                    "speaker": item.speakerId,
                    "content": item.content
                })
            else:
                arr.append({
                    "role": "淘淘",
                    "content": item.content,
                })
        arr.reverse()
        return arr