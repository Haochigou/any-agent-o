from dao import db_util
from dao.entity.user import User


class UserService:
    def getUserByUsername(self, username: str):
        with db_util.getSession() as session:
            user: User = session.query(User).filter(User.userName == username).first()
            if user is None:
                return self.addUser(userName=user)
            return user
        return None

    def addUser(self, userName: str)->User:
        user = User(userName=userName)
        with db_util.getSession() as session:
            session.add(user)
            session.commit()
            f"{user.id}"
            return user
        return None