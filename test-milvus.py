from pymilvus import connections, utility, FieldSchema, CollectionSchema, DataType, Collection

#from agent.domain.interfaces import dbs
from agent.infra.association.embedding_ark import embed_with_str


def connect_to_milvus():
    try:
        #connections.connect(dbs.get_db["milvus"]["db_name"], dbs.get_db["milvus"]["host"], dbs.get_db["milvus"]["port"])
        connections.connect("default", host="172.16.10.128", port="19530")
        print("Connected to Milvus.")
    except Exception as e:
        print(f"Failed to connect to Milvus: {e}")
        raise

def create_collection(name, description, consistency_level="Strong"):
    rec_id = FieldSchema(
    name="rec_id",
    dtype=DataType.INT64,
    is_primary=True,
    auto_id=True
    )
    qa_id = FieldSchema(
    name="qa_id",
    dtype=DataType.INT64,
    )
    question = FieldSchema(
    name="question",
    dtype=DataType.VARCHAR,
    max_length=2048,
    )
    answer = FieldSchema(
    name="answer",
    dtype=DataType.VARCHAR,
    max_length=4096,
    )
    vector = FieldSchema(
    name="vector",
    dtype=DataType.FLOAT_VECTOR,
    dim=1024
    )
    entities = FieldSchema(
    name="entities",
    dtype=DataType.JSON,  
    )
    schema = CollectionSchema(
    fields=[rec_id, qa_id, question, answer, vector, entities],
    description=description,
    enable_dynamic_field=True
    )
    collection = Collection(name, schema, consistency_level=consistency_level)
    return collection

def insert_data(collection, entities):
    insert_result = collection.insert(entities)
    collection.flush()
    print(
        f"Inserted data into '{collection.name}'. Number of entities: {collection.num_entities}")
    return insert_result

index_params = {
  "metric_type":"IP",
  "index_type":"IVF_FLAT",
  "params":{"nlist":1024}
}
def create_index(collection, field_name, index_type, metric_type, params):
    index = {"index_type": index_type,
             "metric_type": metric_type, "params": params}
    collection.create_index(field_name, index)
    print(f"Index '{index_type}' created for field '{field_name}'.")

def search_and_query(collection, search_vectors, search_field, search_params):
    collection.load()

    # Vector search
    result = collection.search(
        search_vectors, search_field, search_params, limit=3, output_fields=["source"])
    print_search_results(result, "Vector search results:")

def print_search_results(results, message):
    print(message)
    for hits in results:
        for hit in hits:
            print(f"Hit: {hit}, source field: {hit.entity.get('source')}")

connect_to_milvus()

collection = create_collection("milian_test", "milian kownledge")

documents = [
    "A group of vibrant parrots chatter loudly, sharing stories of their tropical adventures.",
    "The mathematician found solace in numbers, deciphering the hidden patterns of the universe.",
    "The robot, with its intricate circuitry and precise movements, assembles the devices swiftly.",
    "The chef, with a sprinkle of spices and a dash of love, creates culinary masterpieces.",
    "The ancient tree, with its gnarled branches and deep roots, whispers secrets of the past.",
    "The detective, with keen observation and logical reasoning, unravels the intricate web of clues.",
    "The sunset paints the sky with shades of orange, pink, and purple, reflecting on the calm sea.",
    "In the dense forest, the howl of a lone wolf echoes, blending with the symphony of the night.",
    "The dancer, with graceful moves and expressive gestures, tells a story without uttering a word.",
    "In the quantum realm, particles flicker in and out of existence, dancing to the tunes of probability."
]

embeddings = [embed_with_str(doc, 1024) for doc in documents]
entities = [
    [i for i in range(len(documents))],
    ['' for i in range(len(documents))],
    [str(doc) for doc in documents],
    embeddings,
    [{} for i in range(len(documents))]
]
insert_result = insert_data(collection, entities)
create_index(collection, "vector", "IVF_FLAT", "L2", {"nlist": 1024})

query = "Give me some content about the ocean"
query_vector = embed_with_str(content=query, dim=1024)
search_and_query(collection, [query_vector], "vector", {
                 "metric_type": "L2", "params": {"nprobe": 2}})
