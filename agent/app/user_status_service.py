import json
import time

from redis import Redis
from agent.infra.log.local import getLogger
# 会话（多人会话），
# 认主流程控制（1. 明确拒绝，24小时后重试，2. ）
logger = getLogger("chat")
class UserStatus:
    """
    {
        "sessionId": f"{userId}.{timestamp}",
        "lastTime": timestamp,
        "speakers": {speakerId: 1}
    }
    """
    sessionId: str
    speakers: {}

    def __repr__(self):
        return f"sessionId: {self.sessionId}, speakers: {self.speakers}"

    def to_dict(self):
        return {
            "sessionId": self.sessionId,
            "speakers": self.speakers,
        }

    @staticmethod
    def from_dict(data):
        status = UserStatus()
        status.sessionId = data["sessionId"]
        status.speakers = data["speakers"]
        return status


class UserTryMasterStatus:
    nextTime: int  # 下一次开启引导认主的时间。
    lastTime: int  # 用户最后一次说话的时间。主要是判断开启认主后，用户是否消极回应（30分钟没有回复）
    trying: bool  # 正在执行认主流程
    count: int = 0  # 统计聊天次数，在一个周期内，超过8轮，即满足认主条件

    def __repr__(self):
        return f"nextTime: {self.nextTime}, lastTime: {self.lastTime}, count: {self.count}"

    def to_dict(self):
        return {
            "nextTime": self.nextTime,
            "lastTime": self.lastTime,
            "trying": self.trying,
            "count": self.count
        }

    @staticmethod
    def from_dict(data):
        status = UserTryMasterStatus()
        status.nextTime = data["nextTime"]
        status.lastTime = data["lastTime"]
        status.trying = data["trying"]
        status.count = data["count"]
        return status


class UserStatusService:
    redis = Redis

    def clean(self, userId: int):
        key: str = f"qie:userstatus:{userId}"
        self.redis.delete(key)

        speakers = self.redis.smembers(f"userspeakers:{userId}")
        if speakers is not None:
            for speaker in speakers:
                tryMasterKey = self.tryMasterKey(userId=userId,speakerId=speaker)
                print(f"clean userId: {userId}, speaker: {speaker}, tryMasterKey: {tryMasterKey}")
                self.redis.delete(tryMasterKey)

    def addSpeaker(self, userId: int, speakerId: str):
        speakerKey = f"userspeakers:{userId}"
        self.redis.sadd(speakerKey, speakerId)
        self.redis.expire(speakerKey, 2 * 24 * 60 * 60)

    def updateSession(self, userId: int, speakerId: str) -> UserStatus:
        userStatus: UserStatus = self.getUserStatus(userId=userId)
        userStatus.speakers[speakerId] = 1
        self.setUserStatus(userId=userId, userStatus=userStatus)

        self.addSpeaker(userId=userId, speakerId=speakerId)
        return userStatus

    def setUserStatus(self, userId: int, userStatus: UserStatus) -> None:
        key: str = f"qie:userstatus:{userId}"
        logger.info(f"setUserStatus key: {key} value: {userStatus}")
        self.redis.set(key, json.dumps(userStatus.to_dict(), ensure_ascii=False), ex=5 * 60)

    def getUserStatus(self, userId: int) -> UserStatus:
        key: str = f"qie:userstatus:{userId}"

        val = self.redis.get(key);
        logger.info(f"getUserStatus key: {key}, userStatus: {val}")

        userStatus: UserStatus = None
        if val:
            userStatus = UserStatus.from_dict(json.loads(val))

        if userStatus is None:
            timestamp = int(time.time())  # 获取到秒
            userStatus = UserStatus()
            userStatus.sessionId = f"{userId}.{timestamp}"
            userStatus.speakers = {}
            self.setUserStatus(userId, userStatus)

        return userStatus

    def tryMasterKey(self, userId: int, speakerId: str) -> str:
        key: str = f"qie:userstrymaster:{userId}.{speakerId}"
        return key

    def setUserTryMasterStatus(self, userId: int, speakerId: str, status: UserTryMasterStatus) -> None:
        key: str = self.tryMasterKey(userId, speakerId)
        logger.info(f"setUserTryMasterStatus key: {key}, userId:{userId}, speakerId: {speakerId}, status: {status}")
        self.redis.set(key, json.dumps(status.to_dict(), ensure_ascii=False), ex=2 * 24 * 60 * 60)  # 2天过期

    def getUserTryMasterStatus(self, userId: int, speakerId: str) -> UserTryMasterStatus:
        key = self.tryMasterKey(userId, speakerId)

        val = self.redis.get(key)
        logger.info(f"getUserTryMasterStatus key: {key}, userId:{userId}, speakerId: {speakerId}, val: {val}")
        status: UserTryMasterStatus = None
        if val:
            status = UserTryMasterStatus.from_dict(json.loads(val))

        if status is None:
            timestamp = int(time.time())  # 获取到秒
            status = UserTryMasterStatus()
            status.nextTime = timestamp
            status.lastTime = timestamp
            status.trying = False
            status.count = 0
            self.setUserTryMasterStatus(userId, speakerId, status)

        return status


    def rejectMaster(self, userId: int, speakerId: str) -> None:
        # 明确拒绝
        timestamp = int(time.time())  # 获取到秒
        status: UserTryMasterStatus = self.getUserTryMasterStatus(userId, speakerId)

        status.count = 0
        status.trying = False
        status.nextTime = timestamp + (24 * 60 * 60)  # 更新下一次认主时间
        status.lastTime = timestamp

        self.setUserTryMasterStatus(userId, speakerId, status)


    def tryMaster(self, userId: int, speakerId: str) -> bool:
        timestamp = int(time.time())  # 获取到秒
        status: UserTryMasterStatus = self.getUserTryMasterStatus(userId, speakerId)

        status.count += 1
        if status.count < 8:  # 判断聊天轮数
            # 聊天次数小于8此，不满足认主条件
            self.setUserTryMasterStatus(userId, speakerId, status)
            return False

        if timestamp < status.nextTime:  # 判断认主间隔（明确拒绝：24小时后再次发起，消极响应：12小时后再次发起）
            # 还没有到下一次尝试认主的时间。
            return False

        if status.trying and status.lastTime + (30 * 60) < timestamp:  # 已经进入认主流程了，但是用户超过半个小时没有说话（消极相应）
            status.trying = False
            status.nextTime = timestamp + (12 * 60 * 60)  # 12个小时后再次尝试
            status.lastTime = timestamp  # 更新用户最后一次说话的时间。
            status.count = 0
            self.setUserTryMasterStatus(userId, speakerId, status)
            return False

        status.lastTime = timestamp  # 更新用户最后一次说话的时间。
        status.trying = True
        self.setUserTryMasterStatus(userId, speakerId, status)
        return True

userStatusService = UserStatusService()
