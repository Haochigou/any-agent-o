import db_util
from dao.entity.toy_master import ToyMaster


class ToyMasterService:
    def getToyMasterByUserId(self, user_id):
        with db_util.getSession() as session:
            toyMasters = session.query(ToyMaster).filter(ToyMaster.user_id == user_id).all()
            return toyMasters;


    def addToyMaster(self, toyMaster):
        with db_util.getSession() as session:
            session.add(toyMaster)
            session.commit()