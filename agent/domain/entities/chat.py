"""Chat 描述和用户的交互信息
    在系统内部，chat被分解到感知和执行节点上，既听到了什么，说了什么
"""
from typing import Optional

from pydantic import BaseModel

class ChatRequest(BaseModel):
    scene: str
    user: str
    robot: str
    mode: str
    content: str
    reference: dict | None = None
    
class ChatResponse(BaseModel):
    content: str
    finish_reason: str | None
    request_cost: int
    response_cost: int


class ChatMessagesRequest(BaseModel):
    query: str
    conversation_id: str
    user: str
    response_mode: str
    scene: Optional[str] = None

