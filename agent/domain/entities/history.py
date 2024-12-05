import os
import json

from NamedAtomicLock import NamedAtomicLock

from agent.infra.utils import sql
from agent.domain.entities.mysql_user_memory import Memory

class HistoryManager:

    def __init__(self, path, context_length=4):
        self.path = path
        self.context_length = context_length
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def get(self, who):
        if not who:
            who = "unknown"
        return History(self.path, who, self.context_length)


class History:
    def __init__(self, path, who, context_length):
        self.path = path
        self.context_length = context_length

        if not isinstance(who, str):
            raise TypeError("who必须是字符串")
        #if not who.isalnum():
        #    raise ValueError("who必须只由字母数字组成")
        self.who = who

        self._history = None

        self.load()

    def __del__(self):
        self.save()

    @property
    def filename(self):
        return os.path.join(self.path, f"dialogue-{self.who}.json")

    @property
    def history(self):
        if self._history is not None:
            return self._history
        self.load()
        return self._history

    def append(self, dialogue):
        if isinstance(dialogue, list):
            self._history.extend(dialogue)
            return
        if isinstance(dialogue, dict):
            self._history.append(dialogue)
            return
        raise TypeError(f"unknown dialogue type {type(dialogue)}")

    def load(self):
        result = []
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                result = json.load(file) or []

        self._history = result

    def save(self):
        with open(self.filename, "w+") as file:
            json.dump(self.history, file)

    def get_context(self, context_length=None):
        if context_length is None:
            context_length = self.context_length
        return self.history[-1*context_length:]

    def get_clean_context(self, context_length=None):

        def clean(s: str):
            return s.replace("\n", "\\n")

        res = self.get_context(context_length)
        for r in res:
            r["content"] = clean(r["content"])

        return res


class RobotHistoryManager:

    def __init__(self, path, context_length=4):
        self.path = path
        self.context_length = context_length
        if path != "mysql":
            if not os.path.exists(self.path):
                os.makedirs(self.path)

    def get(self, user, robot):
        if not user:
            user = "unknown"
        if not robot:
            robot = "unknown"

        return RobotHistory(self.path, user, robot, self.context_length)


class RobotHistory:
    def __init__(self, path, user, robot, context_length):
        self.path = path
        self.context_length = context_length
        
        if not isinstance(user, str):
            raise TypeError("who必须是字符串")
        #if not user.isalnum():
        #    raise ValueError("who必须只由字母数字组成")
        self.user = user

        if not isinstance(robot, str):
            raise TypeError("who必须是字符串")
            #if not robot.isalnum():
            #    raise ValueError("who必须只由字母数字组成")
        self.robot = robot

        self._history = None
        
        self._lock = NamedAtomicLock(self.user)
        
        self.load()
            
    def __del__(self):
        self.save()

    @property
    def filename(self):
        return os.path.join(self.path, f"dialogue-{self.user}-{self.robot}.json")

    @property
    def history(self):
        if self._history is not None:
            return self._history
        self.load()
        return self._history

    def append(self, dialogue):
        if isinstance(dialogue, list):
            self._history.extend(dialogue)
            return
        if isinstance(dialogue, dict):
            self._history.append(dialogue)
            return
        raise TypeError(f"unknown dialogue type {type(dialogue)}")

    def load(self):
        result = []
        if self.path != "mysql":
            self._lock.acquire(timeout=5)
            try:
                if os.path.exists(self.filename):
                    with open(self.filename, "r") as file:
                        buffer = file.read()
                        result = json.loads(buffer) if len(buffer) > 1 else []
            except Exception as e:
                print(f"user {self.user} load history error {e}")
            finally:
                self._lock.release()
        else:
            s = sql.get_session()            
            one = None
            try:
                one = s.query(Memory).filter(Memory.user_id == int(self.user)).first()
            except Exception as e:
                print(e)
            if one:
                result = one.chat_history
        self._history = result

    def save(self):
        if self.path != "mysql":
            self._lock.acquire(timeout=5)
            #print(f"user {self.user} save history with lock {self._lock}")
            try:
                with open(self.filename, "w+") as file:
                    json.dump(self._history, file)
            except Exception as e:
                print(f"user {self.user} save history error {e}")
            finally:
                self._lock.release()
        else:
            s = sql.get_session()
            try:
                one = s.query(Memory).filter(Memory.user_id == int(self.user)).first()
                if not one:
                    memory = Memory()
                    memory.user_id = int(self.user)
                    memory.profile = {}
                    memory.chat_history = self._history
                    s.add(memory)
                else:
                    one.chat_history = self._history
                s.commit()
            except Exception as e:
                print(e)

    def get_context(self, context_length=None):
        if context_length is None:
            context_length = self.context_length
        return self._history[-1*context_length:]

    def get_clean_context(self, context_length=None):

        def clean(s: str):
            return s.replace("\n", "\\n")

        res = self.get_context(context_length)
        for r in res:
            r["content"] = clean(r["content"])

        return res
