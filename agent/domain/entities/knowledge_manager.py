import os
import pickle

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
                result.extend(self._kbs[kb_name].query(content, 5))
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
        

kb_manager = KnowledgeManager()

if __name__ == "__main__":
#    kb_manager.build_knowledge("haerbing", model_name="ark", table=[("西湖美景", "西湖有很多美景，能够吸引很多人前往旅游"), ("哈尔滨美景", "哈尔滨是著名的冰城，众多的冰雪风光能够吸引很多人前往旅游")])
    print(kb_manager.query("哈尔滨介绍", ["haerbing"]))