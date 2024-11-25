from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

from agent.infra.utils.dbs import dbs


mysql_ci = dbs.get_db("mysql")
uri = "mysql+mysqldb://" + mysql_ci["user"] + ":" + mysql_ci["password"] + "@" + mysql_ci["host"] + ":" + str(mysql_ci["port"]) + "/" + mysql_ci["db_name"]

engine = create_engine(uri)

def get_session():
    return Session(engine)

def get_tbl_object():
    return declarative_base()

if __name__ == "__main__":
    s = get_session()
    print(get_session())