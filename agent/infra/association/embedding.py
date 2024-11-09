from embedding_ali import embed_with_str as ali
from embedding_ark import embed_with_str as ark

class Embedding():
    def __init__(self, model: str, dim: int = 0):
        self._d = dim
        self._model = model.upper()
        if dim == 0:
            if self._model == "ALI":
                self._d = 1024
            elif self._model == "ARK":
                self._d = 2560                
    
    async def embed_string(self, content: str) -> list|None:
        if self._model == "ALI":
            return ali(content, self._d)
        elif self._model == "ARK":
            return ark(content, self._d)
        else:
            return None
        