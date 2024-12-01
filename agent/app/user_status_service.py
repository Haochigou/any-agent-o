import json
import time

import redis.asyncio as aioredis


# 会话（多人会话），
# 认主流程控制（1. 明确拒绝，24小时后重试，2. ）

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
    tryMaster: bool = False

    def __repr__(self):
        return f"sessionId: {self.sessionId}, speakers: {self.speakers}, tryMaster: {self.tryMaster}"


class UserTryMasterStatus:
    nextTime: int  # 下一次开启引导认主的时间。
    lastTime: int  # 用户最后一次说话的时间。主要是判断开启认主后，用户是否消极回应（30分钟没有回复）
    trying: bool  # 正在执行认主流程
    count: int = 0  # 统计聊天次数，在一个周期内，超过8轮，即满足认主条件

    def __repr__(self):
        return f"nextTime: {self.nextTime}, lastTime: {self.lastTime}, count: {self.count}"


class UserStatusService:
    redis = aioredis.Redis

    def updateSession(self, userId: int, speakerId: str) -> UserStatus:
        userStatus: UserStatus = self.getUserStatus(userId=userId)
        userStatus.speakers[speakerId] = 1
        self.setUserStatus(userId=userId, userStatus=userStatus)

    async def setUserStatus(self, userId: int, userStatus: UserStatus) -> None:
        key: str = f"qie:userstatus:{userId}"
        await self.redis.set(key, json.dumps(userStatus, ensure_ascii=False), ex=5 * 60)

    async def getUserStatus(self, userId: int) -> UserStatus:
        key: str = f"qie:userstatus:{userId}"

        val = await self.redis.get(key);

        userStatus: UserStatus = None
        if val:
            userStatus = json.loads(val, cls=UserStatus)

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

    async def getUserTryMasterStatus(self, userId: int, speakerId: str) -> UserTryMasterStatus:
        key = self.tryMasterKey(userId, speakerId)

        val = await self.redis.get(key)
        status: UserStatus = None
        if val:
            status = json.loads(val, UserStatus)

        if status is None:
            timestamp = int(time.time())  # 获取到秒
            status = UserTryMasterStatus()
            status.nextTime = timestamp
            status.lastTime = timestamp
            status.trying = True
            status.count = 0
            self.setUserTryMasterStatus(userId, speakerId, status)

        return status

    async def setUserTryMasterStatus(self, userId: int, speakerId: str, status: UserTryMasterStatus) -> None:
        key: str = self.tryMasterKey(userId, speakerId)

        await self.redis.set(key, json.dumps(status, ensure_ascii=False), ex=2 * 24 * 60 * 60)  # 2天过期

    def rejectMaster(self, userId: int, speakerId: str) -> None:
        # 明确拒绝
        timestamp = int(time.time())  # 获取到秒
        status: UserTryMasterStatus = self.getUserTryMasterStatus(userId, speakerId)

        status.count = 0
        status.trying = False
        status.nextTime = timestamp + (24 * 60 * 60)  # 更新下一次认主时间

        self.setUserTryMasterStatus(userId, speakerId, status)

    def tryMaster(self, userId: int, speakerId: str) -> bool:
        timestamp = int(time.time())  # 获取到秒
        status: UserTryMasterStatus = self.getUserTryMasterStatus(userId, speakerId)

        status.count += 1
        if status.count < 8:  # 判断聊天轮数
            # 聊天次数小于8此，不满足认主条件
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
