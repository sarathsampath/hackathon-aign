# !python3 -m pip install -qU openai pinecone-client
import openai
import pinecone
import uuid

from openai.embeddings_utils import get_embedding

openai.api_key = "---------api-key------------"
pinecone.init(      
	api_key='-------pinecone-api-key---------',      
	environment='gcp-starter'      
)

# embedding model parameters
embedding_model = "text-similarity-ada-002"
max_tokens = 8000  # the maximum for text-embedding-ada-002 is 8191

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def insert_vector_db(patient_id, summary, diagnosis):
    index = pinecone.Index("test1")
    insert_emb = get_embedding(summary + diagnosis)
    result = index.upsert([(str(uuid.uuid1()), insert_emb, {
                'patientId': patient_id,
                'summary': summary,
                'diagnosis': diagnosis
            })])
    print(f"Insert completed {result}")
    return "Data inserted"


def search_vector_db(search_text, limit=1):
    index = pinecone.Index("test1")
    search_emb = get_embedding(search_text)
    results = []
    query_result = index.query(vector = search_emb,top_k=limit, include_values=True, include_metadata=True,)
    for result in query_result['matches']:
        results.append(result['metadata'])
    return results

def handle_insert(data):
    try:
        return insert_vector_db(data['patientId'], data['summary'], data['diagnosis'])
    except Exception as error:
        print(f"Error in handle insert {error}")
        return error

def handle_search(data):
    try:
        return search_vector_db(data["text"], int(data.get('limit',1)))
    except Exception as error:
        print(f"Error in handle search {error}")
        return error
