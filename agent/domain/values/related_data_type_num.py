from enum import Enum


class RelatedDataTypeEnum(str, Enum):
    sequence = "sequence"
    concurrency = "concurrency"
    competition = "competition"