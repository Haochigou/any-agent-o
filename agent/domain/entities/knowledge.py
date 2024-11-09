''' 对知识进行定义 '''

import os
import pickle

class Knowledge():
    def __init__(self, robot: str):
        self._robot = robot
        # 文件路径应该是kb该定义的内容
        # self._kb_filename = os.path.abspath() + "/knowledge/" + self._robot + ".pkl"
        self._raw_text = None # [(seq, q, a), (seq, q, a)]
        self._entity_rindex = None # dict {(keyword, [seq1, seq2, ...])}
        self._graph = None # dict
        self._d = 0 # default ALI = 1024, ARK = 2560
        self._embedding = None # [(seq, embedding), (seq, embedding)]
        self._embedding_service_name = None # "ALI" or "ARK"
        
    def load_from_kb_file(self):
        if not os.path.exists(self._kb_filename):
            print(f"The knowledge file of robot name {self._robot} is not exist! You can run build_knowledge first")
            return False
        with open(self._kb_filename, 'rb') as handle:    
            self._knowledge = pickle.load(handle)
    
    def build_from_qa_excel(self, excel_path: str, enable_entity = False):
        pass