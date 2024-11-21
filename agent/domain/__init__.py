from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from agent.domain.entities.history import HistoryManager
from agent.domain.entities.history import RobotHistoryManager
from agent.config.memory import MemoryConfig 


_history_manager: Optional[HistoryManager] = None
_robot_history_manager: Optional[RobotHistoryManager] = None
memory_config = MemoryConfig()

def init_global_resource():   
    global _history_manager
    _history_manager = HistoryManager(path=memory_config.get_chat_history_local_path())
    global _robot_history_manager
    _robot_history_manager = RobotHistoryManager(path="mysql")


def get_history_manager():
    return _history_manager

def get_robot_history_manager():
    return _robot_history_manager


__all__ = [
    "init_global_resource",
    "get_history_manager",
    "get_robot_history_manager",
]