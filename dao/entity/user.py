from pip._internal.utils import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP

from dao import db_util


class User(db_util.TblObject):
    __tablename__ = "tb_user"
    id: int = Column("id",Integer, primary_key=True)
    userName: str = Column("user_name", String(32))
    updateTime: str = Column("update_time", TIMESTAMP, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    createTime: str = Column("create_time", TIMESTAMP, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def __init__(self, userName: str, sellStatus = 0):
        self.userName = userName
        self.sellStatus = sellStatus
        self.updateTime = None
        self.createTime = None

    def __repr__(self):
        return f"<User id: {self.id} userName: {self.userName} sellStatus: {self.sellStatus} updateTime: {self.updateTime} createTime: {self.createTime}>"

