import os

import yaml

from agent.infra.log.local import getLogger

logger = getLogger("dbs")

class DBS:
    def __init__(self):
        self._dbs = {}
       
    def load_dbs_from_yaml(self, file: str) -> bool:
        if not os.path.exists(file):
            return False
        try:
            with open(file, "r") as f:
                cfg = f.read()
                self._dbs = yaml.safe_load(cfg)
        except Exception as e:
            logger.error(e)
            print(e)
            return False
        return True


    def get_db(self, name: str):
        
        if name not in self._dbs:
            return None
        return self._dbs[name]

dbs = DBS()
dbs.load_dbs_from_yaml("agent/config/dbs.yaml")

if __name__ == "__main__":    
    
    print(dbs.get_db("milvus"))