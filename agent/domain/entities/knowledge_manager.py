import os
import pickle

import pandas as pd
import openpyxl

from agent.domain.entities import knowledge

class KnowledgeManager():
    def __init__(self):
        self._knowledge_base_dir = os.getcwd() + "/knowledge-base"
        self._kbs = {}
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
                result.extend(self._kbs[kb_name].query(content, 20))
        if len(kb_names) > 1:
            result = sorted(result)
        return result
                
    def build_knowledge(self, kb_name: str, table: list, model_name: str):
        if kb_name in self._kbs:
            print("the knowledge is existed! pls check the content and try another name")
            return
        kg = knowledge.Knowledge(kb_name)
        kg._d = 1024
        kg.build_from_table(table, model_name)
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
                    result.append((question, answer))
        except Exception as e:
            print(f"build from QA excel file {excel_path} fail!, the exception below:\n{e}")
            
        return result

kb_manager = KnowledgeManager()


if __name__ == "__main__":
    #qie = kb_manager.load_qa_table_from_excel("docs/企鹅知识汇总_20241202.xlsx")
    #kb_manager.build_knowledge("haerbing-v1", model_name="ark", table=qie)
    
    print(kb_manager.query("2025年哈尔滨亚东会的吉祥物是谁呀?", ["haerbing-v1"]))