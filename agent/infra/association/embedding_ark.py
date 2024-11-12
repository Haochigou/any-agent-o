import os
from typing import List

import numpy as np

from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime._exceptions import ArkAPIError

ark = Ark(api_key = os.getenv("ARK_APP_KEY"))

def sliced_norm_l2(vec: List[float], dim=2048) -> List[float]:
    # dim 取值 512,1024,2048
    norm = float(np.linalg.norm(vec[:dim]))
    return [v / norm for v in vec[:dim]]

def embed_with_str(content: str, dim: int) -> list|None:
    try:
        #resp = ark.embeddings.create(model='ep-20241108140417-zwtnf', input=content)
        resp = ark.embeddings.create(model="ep-20241112173511-wzhlj", input=content)
        if dim != 0 and len(resp.data[0].embedding) != dim:
            return sliced_norm_l2(resp.data[0].embedding, dim)
        else:
            return resp.data[0].embedding
    except ArkAPIError as e:
        print(e)
        return None

def embed_with_list(content: list) -> list|None:
    try:
        resp = ark.embeddings.create(model='ep-20241112173511-wzhlj', input=content)
        embeddings = [item.embedding for item in resp.data]
        return embeddings
    except ArkAPIError as e:
        print(e)
        return None
        
if __name__ == "__main__":
    print(embed_with_str("你好！"))