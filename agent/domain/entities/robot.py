"""Role 描述AI所扮演的角色
"""
from pydantic import BaseModel

class Robot(BaseModel):
    name: str # 角色名称
    description: str # 角色描述包括：性别、年龄、经历等
    scene: str # 场景是赋予角色当前的谈话背景
    goal: str # 目标是当前角色的谈话目标，包括：疏导用户、为用户提供规划等，可以在推理过程中切换
    functions: list|None # 角色可以调用的功能/工具列表
