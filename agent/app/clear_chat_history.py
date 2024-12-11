import os

from agent.config.memory import MemoryConfig 

def clear_chat_history(user, robot):
    filepath = os.path.join(MemoryConfig.get_chat_history_local_path(), f"dialogue-{str(user)}-{str(robot)}.json")
    if os.path.exists(filepath):
        os.remove(filepath)