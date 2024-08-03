"""User 描述用户的信息
"""
from datetime import datetime
from pydantic import BaseModel

class User(BaseModel):
    name: str # 用户名称
    gender: str # 男孩女孩
    birthday: datetime # 出生年月
    description: str # 用户介绍，来自用户画像
    
    