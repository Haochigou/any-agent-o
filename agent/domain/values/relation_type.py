from enum import Enum


class RelationType(str, Enum):
    subsequence = "subsequence"
    presequence = "presequence"
    concurrence ="concurrence"    
    analytic  = "analytic" # 解析关系，方向通过节点类型来标示，content为None的为解析后的，content不为None为解析前的，解析后的None content节点通过其他关系和实际结果内容进行关联