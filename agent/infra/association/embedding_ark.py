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
        resp = ark.embeddings.create(model="ep-20241212165554-nwmql", input=content)
        if dim != 0 and len(resp.data[0].embedding) != dim:
            return sliced_norm_l2(resp.data[0].embedding, dim)
        else:
            return resp.data[0].embedding
    except ArkAPIError as e:
        print(e)
        return None

def embed_with_list(content: list) -> list|None:
    try:
        resp = ark.embeddings.create(model='ep-20241212165554-nwmql', input=content)
        embeddings = [item.embedding for item in resp.data]
        return embeddings
    except ArkAPIError as e:
        print(e)
        return None
        
if __name__ == "__main__":
    print(embed_with_str("你好延缓更年期的营养补充剂有哪些？适当的营养补充剂可能有帮助。比如维生素 D 和钙，它们可以预防骨质疏松，维持骨骼健康，对整体身体状态有益。对于一些可能缺乏维生素 B 族的人群，适当补充能改善神经系统功能和能量代谢。但补充营养剂要谨慎，最好在医生或营养师的指导下进行，避免过量。例如，过量的维生素 D 可能会导致中毒。", 1024))