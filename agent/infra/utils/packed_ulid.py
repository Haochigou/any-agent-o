import ulid

def get_packed_ulid() -> int:
    str_ulid = ulid.new()
    return str_ulid.bytes

if __name__ == "__main__":
    id = get_packed_ulid()
    print(id)
    