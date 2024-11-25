class MemoryConfig:
    def __init__(self):
        self.chat_history_local_path = "./chat-history"
        self.chat_status_local_path = "./data"
    
    def get_chat_history_local_path(self) -> str:
        return self.chat_history_local_path
    
    def get_chat_status_local_path(self) -> str:
        return self.chat_status_local_path