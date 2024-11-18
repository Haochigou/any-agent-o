import uuid

def get_packed_uuid() -> int:
    str_uuid = uuid.uuid1()
    print(str_uuid)
    return str_uuid.bytes
    

if __name__ == "__main__":
    dict = {}
    key = None
    for i in range(10):
        key = get_packed_uuid()
        dict[key] = i
    print(dict.keys())
