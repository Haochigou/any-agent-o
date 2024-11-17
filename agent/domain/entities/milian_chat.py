"""Chat 描述和用户的交互信息
    在系统内部，chat被分解到感知和执行节点上，既听到了什么，说了什么
"""
from pydantic import BaseModel

class MilianChatRequest(BaseModel):
    traceId: str
    userId: int
    requestType: int
    content: str
    gender: str | None = None
    age: int | None = None
    marriage: str | None = None
    fertilityStatus: str | None = None
    deliveryMethod: str | None = None
    children: list | None = None
    lastMensesDate: str | None = None
    mensesCycle: int | None = None
    mensesDuration: int | None = None
    questionnaire: list | None = None
    
class MilianChatResponse(BaseModel):
    content: str
    finish_reason: str|None
    request_cost: int
    response_cost: int