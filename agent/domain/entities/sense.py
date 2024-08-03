from datetime import datetime

from pydantic import BaseModel

from agent.domain.values.related_data_type_num import RelatedDataTypeEnum
    

class Sense(BaseModel):    
    object_id: str # 客体对象标识，和用户交互时，为user id，当是世界信息时，这里可以默认为"world"
    sensor: str # 感知器名称，如视觉、嗅觉、内感知等，考虑定义为枚举
    data: str
    source_working_memory_nodes: dict|None # pair of {id, weight}, 定义感知来源，可能感知外部设备，这时候为None，也可能来之行为或工具使用
    type: RelatedDataTypeEnum
    next_working_memory_nodes: dict|None # node uuid，
    weight: int
    create_datetime: datetime
