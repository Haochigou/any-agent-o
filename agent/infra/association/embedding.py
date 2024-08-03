from typing import Generator, List
import os

from http import HTTPStatus
import dashscope


dashscope.api_key = os.getenv("ALI_APP_KEY")

def embed_with_str(context: str) -> list:
    resp = dashscope.TextEmbedding.call(
        model=dashscope.TextEmbedding.Models.text_embedding_v2,
        input=context)
    if resp.status_code == HTTPStatus.OK:
        return resp.output["embeddings"][0]["embedding"]
    else:
        None

def embed_with_file(filepath: str) -> list:
    # 文件中最多支持25条，每条最长支持2048tokens
    with open(filepath, 'r', encoding='utf-8') as f:
        resp = dashscope.TextEmbedding.call(
            model = dashscope.TextEmbedding.Models.text_embedding_v1,
            input=f)
        if resp.status_code == HTTPStatus.OK:
            print(resp)
        else:
            print(resp)

if __name__ == "__main__":
    print(embed_with_str("你好！"))