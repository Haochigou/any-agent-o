import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP

from dao import db_util


class ToyMaster(db_util.TblObject):
    __tablename__ = "tb_toy_master"
    id: int = Column("id", Integer, primary_key=True)
    userId: int = Column("user_id", Integer)
    masterId: str = Column("master_id", String(32))
    updateTime: str = Column("update_time", TIMESTAMP, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    createTime: str = Column("create_time", TIMESTAMP, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def __repr__(self):
        return f"ToyMaster id: {self.id} userId: {self.userId} masterId: {self.masterId} updateTime: {self.updateTime} createTime: {self.createTime}"
