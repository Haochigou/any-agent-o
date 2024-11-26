import os

import yaml

from agent.domain.entities.scene import Scene
from agent.infra.log.local import getLogger

logger = getLogger("chat")

_scenes = {}

def load_scenes_from_yaml(file: str) -> bool:
    global _scenes
    if not os.path.exists(file):
        return False
    try:
        with open(file, "r") as f:
            cfg = f.read()
            _scenes = yaml.safe_load(cfg)
    except Exception as e:
        logger.error(e)
        print(e)
        return False
    return True


def get_scene(name: str) -> Scene | None:
    global _scenes
    if name not in _scenes:
        return None
    return _scenes[name]


if __name__ == "__main__":    
    load_scenes_from_yaml("agent/config/scene.yaml")
    print(_scenes)