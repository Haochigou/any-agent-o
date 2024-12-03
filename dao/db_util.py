from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

import config

engine = create_engine(url=config.DB_URL, pool_size=10, max_overflow=10)

TblObject = declarative_base()


def getSession():
    return Session(engine)
