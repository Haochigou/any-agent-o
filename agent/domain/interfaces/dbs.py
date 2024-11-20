import os

import yaml

from agent.domain.entities.scene import Scene
from agent.infra.log.local import getLogger

logger = getLogger("dbs")

_dbs = {}

def load_dbs_from_yaml(file: str) -> bool:
    global _dbs
    if not os.path.exists(file):
        return False
    try:
        with open(file, "r") as f:
            cfg = f.read()
            _dbs = yaml.safe_load(cfg)
    except Exception as e:
        logger.error(e)
        print(e)
        return False
    return True


def get_db(name: str) -> Scene | None:
    global _dbs
    if name not in _dbs:
        return None
    return _dbs[name]


if __name__ == "__main__":    
    load_dbs_from_yaml("agent/config/dbs.yaml")
    print(_dbs)