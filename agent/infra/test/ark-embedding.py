from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime._exceptions import ArkAPIError

ark = Ark(api_key = '1344d088-fbc6-4821-869b-7af92e0cfcf6')

def embed_with_str(content: str) -> list:
    try:
        resp = ark.embeddings.create(model='ep-20241108140417-zwtnf', input=content)
        return resp.data[0].embedding
    except ArkAPIError as e:
        print(e)

if __name__ == "__main__":
    print(embed_with_str("你好！"))