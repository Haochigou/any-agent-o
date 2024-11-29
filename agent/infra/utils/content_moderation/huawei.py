import httpx
import time
import json

from agent.infra.log import local

m_logger = local.getLogger("moderation")
huawei_token = ''
token_expire_datetime = time.time()
async def get_huawei_token():
    token_url = "https://iam.cn-north-4.myhuaweicloud.com/v3/auth/tokens"
    headers = {"Content-Type":"application/json;charset=utf8"}
    #body = "{ \"auth\": {\"identity\": {\"methods\": [\"password\"], \"password\": {\"user\": {\"domain\": {\"name\": \"hid_xe8asnl_gz-cmbk\"},\"name\": \"text\",\"password\": \"0U7PvOBnyCrlJ\"}}},\"scope\": {\"domain\": {\"name\": \"hid_xe8asnl_gz-cmbk\"}}}}"
    body = "{ \"auth\": {\"identity\": {\"methods\": [\"password\"], \"password\": {\"user\": {\"domain\": {\"name\": \"hid_xe8asnl_gz-cmbk\"},\"name\": \"text\",\"password\": \"0U7PvOBnyCrlJ\"}}},\"scope\": {\"project\": {\"name\": \"cn-north-4\"}}}}"
    global huawei_token, token_expire_datetime
    if time.time() < token_expire_datetime:
        return huawei_token
    try:
        async with httpx.AsyncClient() as client:            
            token_request = await client.post(token_url, headers=headers, data=body)
            huawei_token = token_request.headers.get("X-Subject-Token")
        token_expire_datetime = time.time() + 3600 * 5
    except Exception as e:
        print(e)
        huawei_token = ''
    return huawei_token

        
async def check_words_by_huawei(text):
    huawei_token = await get_huawei_token()
    if huawei_token is None or len(huawei_token) == 0:
        return True
    check_url = "https://moderation.cn-north-4.myhuaweicloud.com/v3/a31ea41b66f94dada7a9e93e0d152087/moderation/text"
    # headers = {"Content-Type":"application/json;charset=utf8"}
    headers = {"Content-Type":"application/json;charset=utf8", "X-Auth-Token":huawei_token}
    body = "{\"event_type\":\"comment\", \"glossary_names\":[\"dialog-refuse\"], \"biz_type\":\"biz_type _ai taotao\", \"white_glossary_names\":[\"Dialog\"],\"data\":{\"text\":\"" + text + "\"}}"
    try:
        async with httpx.AsyncClient() as client:
            check_request = await client.post(check_url, headers=headers, data=body.encode())
            m_logger.info(check_request)
            res = json.loads(check_request.text)
            max_confidence = 0
            for evidence in res["result"]["details"]:
                if max_confidence < evidence["confidence"]:
                    max_confidence = evidence["confidence"]
            if res["result"]["suggestion"] == "block" and max_confidence > 0.95:
                m_logger.info(f"content:{res}, block score:{max_confidence}")                
                return False
    except Exception as e:
        print(e)
        return True
    return True

