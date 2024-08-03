from datetime import datetime
from pydantic import BaseModel

from agent.domain.values.related_data_type_num import RelatedDataTypeEnum


class Action(BaseModel):
    object_id: str # 客体对象标识，和用户交互时，为user id，当是世界信息时，这里可以默认为"world"
    actor: str # 包括内外部行为，如微笑、猜想、推理、自省等，考虑定义为枚举
    goal: str|None # 行为目标，可以为空，每个实例可能不同
    instruction: str # 模型指令，每个实例可能不同
    source_working_memory_nodes: dict|None # pair of {id, weight}，来自于其他感知或行为节点
    type: RelatedDataTypeEnum
    next_working_memory_nodes: dict|None
    weight: int
    create_datetime: datetime
