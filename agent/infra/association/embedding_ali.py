from typing import Generator, List
import os

from http import HTTPStatus
import dashscope

dashscope.api_key = os.getenv("ALI_API_KEY")
def sliced_norm_l2(vec: List[float], dim=2048) -> List[float]:
    # dim 取值 512,1024,2048
    norm = float(np.linalg.norm(vec[:dim]))
    return [v / norm for v in vec[:dim]]

def embed_with_str(context: str, dim: int) -> list:
    resp = dashscope.TextEmbedding.call(
        model=dashscope.TextEmbedding.Models.text_embedding_v3,
        input=context)
    if resp.status_code == HTTPStatus.OK:
        if len(resp.output["embeddings"][0]["embedding"]) == dim:
            return resp.output["embeddings"][0]["embedding"]
        else:
            return sliced_norm_l2(resp.output["embeddings"][0]["embedding"])
    else:
        return None

def embed_with_file(filepath: str) -> list:
    # 文件中最多支持25条，每条最长支持2048tokens
    embeddings = []
    with open(filepath, 'r', encoding='utf-8') as f:
        resp = dashscope.TextEmbedding.call(
            model = dashscope.TextEmbedding.Models.text_embedding_v3,
            input=f)
        if resp.status_code == HTTPStatus.OK:
            embeddings = [item["embedding"] for item in resp.output["embeddings"]] 
        else:
            print(resp)        
    return embeddings

if __name__ == "__main__":
    print(embed_with_str("你好！"))
    embed_with_file("data/测试.txt")