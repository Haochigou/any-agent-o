import os
import pickle
import sys
import argparse

import pandas as pd
import openpyxl

sys.path.append(os.getcwd())
from agent.domain.entities import knowledge
from agent.infra.embedding_db import milvus
from agent.infra.utils.dbs import dbs

class KnowledgeManager():
    def __init__(self):
        self._knowledge_base_dir = os.getcwd() + "/knowledge-base"
        self._kbs = {}
        milvus.connect_to_milvus()
        for item in os.scandir(self._knowledge_base_dir):
            if item.is_file():
                kbf_name = os.path.basename(item)
                if kbf_name.endswith(".pkl"):
                    kb_name = kbf_name.rstrip(".pkl")                    
                    with open(item, 'rb') as handle:    
                        self._kbs[kb_name] = pickle.load(handle)
                        self._kbs[kb_name].start()
                
    def query(self, content: str, kb_names: list):
        result = []
        for kb_name in kb_names:
            if kb_name in self._kbs:
                result.extend(self._kbs[kb_name].query(content, 5))
        if len(kb_names) > 1:
            result = sorted(result)
        return result
                
    def build_knowledge(self, kb_name: str, table: list, model_name: str, storage_type: str = "local"):
        if kb_name in self._kbs:
            print("the knowledge is existed! pls check the content and try another name")
            return
        kg = knowledge.Knowledge(kb_name)
        kg._d = 1024
        data = kg.build_from_table(table, model_name, storage_type)
        
        with open(self._knowledge_base_dir + "/" + kb_name + ".pkl", 'wb') as handle: 
            pickle.dump(kg, handle)
        kg.start()
        self._kbs[kb_name] = kg
        
    def load_qa_table_from_excel(self, excel_path: str) -> list:
        try:
            wb = openpyxl.load_workbook(excel_path)
            sheets = wb.sheetnames
            result = []
            for sheet in sheets:
                df = pd.read_excel(excel_path, sheet_name=sheet, keep_default_na=False)
                for question, answer in zip(df["问"], df['答']):
                    print(question, answer)  
                    result.append((question, answer))
        except Exception as e:
            print(f"build from QA excel file {excel_path} fail!, the exception below:\n{e}")
            
        return result

kb_manager = KnowledgeManager()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fileqa", dest="fileqa", default=None, help="raw knowledge in QA excel")
    parser.add_argument("-c", "--collection", dest="collection", default="milian_ai_v1", help="collection name")
    parser.add_argument("-q", "--query", dest="query", default=None, help="string to query in collection")
    parser.add_argument("-t", "--type", dest="type", default="local", help="storage type: local or milvus")
    terminal_args = parser.parse_args()
    if terminal_args.fileqa:
        ks = kb_manager.load_qa_table_from_excel("docs/milian-knowledge.xlsx")
        kb_manager.build_knowledge(terminal_args.collection, model_name="ark", table=ks, storage_type=terminal_args.type)
    #qie = kb_manager.load_qa_table_from_excel("docs/milian-knowledge.xlsx")
    #print(f"total size:v{qie}")
    if terminal_args.query:
        print(kb_manager.query(terminal_args.query, [terminal_args.collection]))