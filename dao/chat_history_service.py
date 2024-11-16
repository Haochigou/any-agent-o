import db_util
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
