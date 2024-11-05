from enum import Enum


class MemoryUnitType(str, Enum):
    speak = "speak" # 说话行为
    listen = "listen" # 听到感知
    think = "think" # 内部思考/反思等
    external = "external" # 外部渠道信号源
    tool = "tool" # 工具信息
    goal = "goal" # 目标，表示一种诉求/意图
