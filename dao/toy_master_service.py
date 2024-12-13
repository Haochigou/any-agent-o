from dao import db_util
from dao.entity.toy_master import ToyMaster


class ToyMasterService:
    def getToyMasterByUserId(self, user_id):
        with db_util.getSession() as session:
            toyMasters = session.query(ToyMaster).filter(ToyMaster.userId == user_id).all()
            return toyMasters;

    def deleteToyMasterByUserId(self, user_id):
        with db_util.getSession() as session:
            session.query(ToyMaster).filter(ToyMaster.userId == user_id).delete()
            session.commit()


    def addToyMaster(self, toyMaster: ToyMaster):
        with db_util.getSession() as session:
            session.add(toyMaster)
            session.commit()


    def addToyMaster(self, userId: int, masterId: str):
        toyMaster = ToyMaster()
        toyMaster.userId = userId
        toyMaster.masterId = masterId
        with db_util.getSession() as session:
            session.add(toyMaster)
            session.commit()


    def isMaster(self, userId: int, speakerId: str)->bool:
        with db_util.getSession() as session:
            return session.query(ToyMaster).filter(ToyMaster.userId == userId,ToyMaster.masterId == speakerId).count() > 0

        return False