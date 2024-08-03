class MemoryConfig:
    def __init__(self):
        self.chat_history_local_path = "./chat-history"
    
    def get_chat_history_local_path(self) -> str:
        return self.chat_history_local_path