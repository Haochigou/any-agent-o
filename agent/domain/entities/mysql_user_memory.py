from sqlalchemy import Column, Integer, JSON

from agent.infra.utils import sql


class Memory(sql.get_tbl_object()):
    __tablename__ = "tb_interaction_memory"
    user_id: int = Column("user_id", Integer, primary_key=True)
    chat_history: int = Column("chat_history", JSON) 
    profile: str = Column("profile", JSON)    

    def __repr__(self):
        return f"memory: {self.user_id} history: {self.chat_history} profile: {self.profile}"

if __name__ == "__main__":
    memory = Memory()
    memory.user_id = 1
    memory.chat_history = {"history":5}
    memory.profile = {"profile":7}
    s = sql.get_session()
    result = s.query(Memory).filter(Memory.user_id == 2).first()
   
    print(result)
    #result.profile = {"profile": "updated"}        
    #s.commit()
    