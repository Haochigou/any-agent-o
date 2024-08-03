"""Memory 作为机器人的记忆描述，每个机器人有独立的一套
    包括历史感知和行为（如对话、思考等），由action、sense和function等节点构成
    并按照时空逻辑进行组装
"""
class Memory():
    robot_id: str # 机器人标识，也使用uuid的16bytes形式表示，在存储中作为key区分多机器人
    network: dict # key: uuid bytes, value: action, sense, function nodes
    update_list: list # 在network中的节点更新列表