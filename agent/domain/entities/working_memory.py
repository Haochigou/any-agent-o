'''
"""Role 描述AI所扮演的角色
'''
from pydantic import BaseModel
from datetime import datetime

from values.memory_unit_type import MemoryUnitType
from values.memory_unit_status import MemoryUnitStatus
from values.relation_type import RelationType

class RelationEdge(BaseModel):
    target_id: str # 采用ulid标准
    relation: RelationType
    weight: int # 连接边的权重

class MemoryUnit(BaseModel):
    id : str # 采用 ulid 标准
    parent_ids : list[RelationEdge]
    child_ids : list[RelationEdge]
    role : str
    type : MemoryUnitType
    content : str | None # 有一些虚拟节点用于逻辑的组织
    created_time : datetime
    status : MemoryUnitStatus

class WorkingMemory(BaseModel): # 以robot和user为单元key
    robot: str
    user: str
    pool : dict # pair of (id, MemoryUnit)
    history : list # time serias of id， last N turns
    attentions : dict # pair of (id, attention_value)
    