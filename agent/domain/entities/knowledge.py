''' 对知识进行定义 '''

import os
import pickle

import numpy as np
import faiss

from agent.infra.utils.filters.dfa import DFAFilter
from agent.infra.association.embedding import Embedding
class Knowledge():
    def __init__(self, name: str):
        self._name = name
        # 文件路径应该是kb该定义的内容
        # self._kb_filename = os.path.abspath() + "/knowledge/" + self._robot + ".pkl"
        self._raw_text = [] # [(seq1, q, a), (seq2, q, a)]
        self._entity_rindex = {} # dict {(keyword, [seq1, seq2, ...])}
        self._graph = None # dict
        self._d = 0 # default ALI = 1024, ARK = 2560
        self._embeddings = [] # [(seq, [field_no1, field_no2], embedding), (seq, [field_no1, field_no2], embedding)]
        self._embedding_service_name = None # "ALI" or "ARK"
        self._filter = DFAFilter()        
        
    def start(self):
        '''实体加载'''
        if len(self._entity_rindex) > 0:
            self._filter.add_words(item[0] for item in self._entity_rindex)
        
        '''向量索引构建'''
        index = faiss.IndexFlatL2(self._d)
        embe = np.array([emm[2] for emm in self._embeddings])
        index.add(embe)
        self.index_size = len(self._embeddings) # this should not dump to pickle
        self.index = index # this should not dump to pickle
        self.embed = Embedding(self._embedding_service_name, self._d)
        self.ready = True # this should not dump to pickle
       
    def build_from_table(self, table: list, model_name: str) -> bool:
        if model_name.upper() not in ['ALI', 'ARK']:
            return False
        self._embedding_service_name = model_name.upper()
        self.embed = Embedding(self._embedding_service_name, self._d)
        self._d = self.embed._d
        index = 0
        for item in table:
            embed_str = f"{str(item[0])}\n{str(item[1])}"
            if len(embed_str) > 2048:
                print(f"--------embedding string warning!!!, string length below is exceed the max 2048, will be corped for embedding calc!\n{embed_str}")
                embed_str = embed_str[0:2048]
            vector = self.embed.embed_string(embed_str)
            self._raw_text.append((index, item[0], item[1]))
            self._embeddings.append((index, [0, 1], vector))
            if item[0] and len(item[0]) > 0:
                vector = self.embed.embed_string(item[0])
                self._embeddings.append((index, [0, 1], vector))
            index += 1
        pass
    
    def query(self, content: str, limit: int):
        if not self.ready:
            return None
        #entities = self._filter.check(content)[2]
        result = []
        if self.index_size > 0:
            if limit > self.index_size:
                limit = self.index_size
            embedding = self.embed.embed_string(content)
            distances, text_index = self.index.search(np.array([embedding]), limit)            
            context = []
            dists = []
            topics = []
            thres_index = 0
            hit_flag = False
            for i in list(distances[0]):
                if i < 0.1248:                    
                    hit_flag = True
                elif hit_flag:
                    break
                if i < 0.60: 
                    thres_index += 1
                    dists.append(float(i))
                else:
                    break
            
            for idx, index in enumerate(list(text_index[0])):
                if index < 0:
                    break
                thres_index -= 1
                if thres_index < 0:
                    break
                result.append((dists[idx], self._raw_text[self._embeddings[index][0]][1], self._raw_text[self._embeddings[index][0]][2]))
            return result
    