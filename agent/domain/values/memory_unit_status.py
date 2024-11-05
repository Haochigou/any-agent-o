from enum import Enum


class MemoryUnitStatus(str, Enum):
    stop = "stop"
    sensing = "sensing"
    acting = "acting"
    interrupted = "interrupted"