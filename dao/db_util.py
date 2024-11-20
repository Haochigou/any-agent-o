from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

DB_URI = "mysql+mysqldb://root:123456@192.168.0.103/qie_toy"
engine = create_engine(url=DB_URI)

TblObject = declarative_base()


def getSession():
    return Session(engine)
