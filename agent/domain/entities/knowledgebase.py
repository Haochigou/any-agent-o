import os
import pickle
import numpy as np
import pandas as pd

import faiss
import openpyxl

from infra.association import embedding

class KnowledgeBase():
    def __init__(self, file_path: str) -> None:
        self._d = 1536
        self._file_path = file_path
        self._knowledge = None
        self._index_size = 0
        self._index = faiss.IndexFlatL2(self._d)
        self._content_list = []
        self._topic_list = []

    def load_from_kb_file(self) -> bool:
        if not os.path.exists(self._file_path):
            return False
        with open(self._file_path, 'rb') as handle:    
            self._knowledge = pickle.load(handle)
        
        index = faiss.IndexFlatL2(self._d)
        embe = np.array([emm[2] for emm in self._knowledge])
        content = [emm[1] for emm in self._knowledge]
        topic = [emm[0] for emm in self._knowledge]
        index.add(embe)
        self._index_size = len(self._knowledge)
        self._index = index
        self._content_list = content
        self._topic_list = topic
        return True
    
    def build_from_qa_excel(self, excel_path: str) -> bool:
        try:
            wb = openpyxl.load_workbook(excel_path)
            sheets = wb.sheetnames
            result = []
            for sheet in sheets:
                df = pd.read_excel(excel_path, sheet_name=sheet, keep_default_na=False)
                for question, answer in zip(df["问"], df['答']):
                    embed_str = f"{question}\n{answer}"
                    if len(embed_str) > 2048:
                        print(f"--------embedding string warning!!!, string length below is exceed the max 2048, will be corped for embedding calc!\n{embed_str}")
                        embed_str = embed_str[0:2048]
                    vector = embedding.embed_with_str(embed_str)
                    result.append((question, answer, vector))
            with open(self._file_path, 'wb') as handle: 
                pickle.dump(result, handle)
        except Exception as e:
            print(f"build from QA excel file {excel_path} fail!, the exception below:\n{e}")
            return False
        return True
    
    def get_texts(self, embeding, limit):
        if limit > self._index_size:
            limit = self._index_size
        distances, text_index = self._index.search(np.array([embeding]), limit)            
        context = []
        dists = []
        topics = []
        thres_index = 0
        hit_flag = False
        for i in list(distances[0]):
            if i < 0.2648:
                hit_flag = True
            elif hit_flag:
                break
            if i < 0.50: 
                thres_index += 1
                dists.append(i)
            else:
                break
        for i in list(text_index[0]):
            if i < 0:
                break
            thres_index -= 1
            if thres_index < 0:
                break
            context.append(self._content_list[i])
            topics.append(self._topic_list[i])
        return dists, topics, context
    
    def query(self, content: str):
        if len(content) < 5:
            return [], [], []
        embedding = embedding.embed_with_str(content)
        if embedding is None:
            return [], [], []
        distances, topics, context = self.get_texts(embedding, 15)
        return distances, topics, context
        
if __name__ == "__main__":
    kb = KnowledgeBase("xihukb.pkl")
    #kb.build_from_qa_excel("xihukb.xlsx")
    kb.load_from_kb_file()
    distance, topics, content = kb.query("西湖都有哪些景点")
    
    print(distance)
    print(topics)
    print(content)
        
                