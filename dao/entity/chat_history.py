import sqlalchemy

from sqlalchemy import Column, Integer, String, TIMESTAMP, Text

from dao import db_util


class ChatHistory(db_util.TblObject):
    __tablename__ = "tb_chat_history"
    id: int = Column("id", Integer, primary_key=True)
    userId: int = Column("user_id", Integer)
    sessionId: str = Column("session_id", String(32))
    speakerId: str = Column("speaker_id", String(32))
    roleType: int = Column("role_type", Integer, comment="角色类型，0：AI，1：用户")
    content: str = Column("content", Text)
    updateTime: str = Column("update_time", TIMESTAMP, default=sqlalchemy.func.now())
    createTime: str = Column("create_time", TIMESTAMP, default=sqlalchemy.func.now())

    def __repr__(self):
        return f"ChatHistory id: {self.id} userId: {self.userId} sessionId: {self.sessionId} updateTime: {self.updateTime} createTime: {self.createTime}"
