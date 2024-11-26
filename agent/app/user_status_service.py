import time


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
    lastTime: int
    speakers: {}
    tryMaster: bool = False

    def __repr__(self):
        return f"sessionId: {self.sessionId}, lastTime: {self.lastTime}, speakers: {self.speakers}, tryMaster: {self.tryMaster}"


class UserTryMasterStatus:
    nextTime: int  # 下一次开启引导认主的时间。
    lastTime: int
    trying: bool  # 正在执行认主流程
    count: int = 0 # 统计聊天次数，在一个周期内，超过8轮，即满足认主条件

    def __repr__(self):
        return f"nextTime: {self.nextTime}, lastTime: {self.lastTime}, count: {self.count}"

class UserStatusService:
    userStatus: {str: UserStatus} = {}
    userTryMasterStatus: {str: UserTryMasterStatus} = {}

    def __init__(self):
        pass

    def updateSession(self, userId: int, speakerId: str) -> str:
        key: str = f"user:{userId}"
        timestamp = int(time.time())  # 获取到秒

        userStatus: UserStatus = self.userStatus.get(key)
        if userStatus:
            if userStatus.lastTime + 300 < timestamp:  # 最后一次聊天时间间隔超过了5分钟，重新生产一个session
                userStatus = None

        if userStatus:
            userStatus.lastTime = timestamp
            userStatus.speakers[speakerId] = timestamp
        else:
            userStatus = UserStatus()
            userStatus.sessionId = f"{userId}.{timestamp}"
            userStatus.lastTime = timestamp
            userStatus.speakers = {speakerId: timestamp}
            self.userStatus[key] = userStatus

        return userStatus.sessionId

    def getUserStatus(self, userId: int) -> UserStatus:
        key: str = f"user:{userId}"
        return self.userStatus.get(key)



    def tryMasterKey(self, userId: int, speakerId: str) -> str:
        key: str = f"{userId}.{speakerId}"
        return key

    def rejectMaster(self, userId: int, speakerId: str) -> None:
        # 明确拒绝
        key: str = self.tryMasterKey(userId=userId, speakerId=speakerId)
        timestamp = int(time.time())  # 获取到秒
        status: UserTryMasterStatus = self.userTryMasterStatus.get(key)
        if status:
            status.count = 0
            status.trying = False
            status.nextTime = timestamp + (24 * 60 * 60)  # 更新下一次认主时间

    def tryMaster(self, userId: int, speakerId: str) -> bool:
        key: str = self.tryMasterKey(userId=userId, speakerId=speakerId)
        timestamp = int(time.time())  # 获取到秒
        status: UserTryMasterStatus = self.userTryMasterStatus.get(key)

        if status is None:
            status = UserTryMasterStatus()
            status.nextTime = timestamp
            status.lastTime = timestamp
            status.trying = True
            status.count = 0
            self.userTryMasterStatus[key] = status

        status.count += 1
        if status.count < 8: # 判断聊天轮数
            # 聊天次数小于8此，不满足认主条件
            return False

        if timestamp < status.nextTime: # 判断认主间隔（明确拒绝：24小时后再次发起，消极响应：12小时后再次发起）
            # 还没有到下一次尝试认主的时间。
            return False

        if status.trying and status.lastTime + (30 * 60) < timestamp:  # 已经进入认主流程了，但是用户超过半个小时没有说话（消极相应）
            status.trying = False
            status.nextTime = timestamp + (12 * 60 * 60)  # 12个小时后再次尝试
            status.lastTime = timestamp # 更新用户最后一次说话的时间。
            status.count = 0
            return False

        status.lastTime = timestamp # 更新用户最后一次说话的时间。
        status.trying = True
        return True


userStatusService = UserStatusService()
