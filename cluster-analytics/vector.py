# !python3 -m pip install -qU openai pinecone-client
import openai
import pinecone
import uuid
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
import numpy as np
from openai.embeddings_utils import get_embedding

openai.api_key = "<open-api-key>"
pinecone.init(      
	api_key='<pinecone-api-key>',      
	environment='gcp-starter'      
)

# embedding model parameters
embedding_model = "text-similarity-ada-002"
max_tokens = 8000 
cluster_size = 5

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def insert_vector_db(patient_id, symptom):
    index = pinecone.Index("clustering")
    insert_emb = get_embedding(symptom)
    result = index.upsert([(str(uuid.uuid1()), insert_emb, {
                'patientId': patient_id,
                'symptom': symptom
            })])
    print(f"Insert completed {result}")
    return "Data inserted"

def sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if int(arr[j]['clusterCount']) < int(arr[j + 1]['clusterCount']):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

def kmean_cluster(embeddings):
    kmeans = KMeans(n_clusters=cluster_size, 
                random_state=0, 
                n_init = 'auto').fit(embeddings)
    kmeans_labels = kmeans.labels_
    label_counts = np.bincount(kmeans_labels)
    return [kmeans_labels, label_counts]

def find_index(array, element):
    for index in range(len(array)):
        if array[index] == element:
            return index
    return -1

def list_all_embeddings():
    index = pinecone.Index("clustering")
    stats = index.describe_index_stats()
    namespace_map = stats['namespaces']
    vectors = []
    values = []
    metadata = []
    for namespace in namespace_map:
        vector_count = namespace_map[namespace]['vector_count']
        res = index.query(vector=[0 for _ in range(1536)], top_k=10000, namespace=namespace, include_values=True, include_metadata=True)
        for match in res['matches']:
            vectors.append(match)
            values.append(match['values'])
            metadata.append(match['metadata'])
    return [vectors, values, metadata]

def search_vector_db():
    cluster_results = []
    [vectors, values, metadata] = list_all_embeddings()
    [kmeans_labels, label_counts] = kmean_cluster(values)

    for index in range(len(label_counts)):
        count = label_counts[index]
        vector_index = find_index(kmeans_labels, index)
        cluster_results.append({
            "clusterIndex": str(index),
            "clusterCount": str(count),
            "symptom": metadata[vector_index]['symptom']
        })
    sort(cluster_results)
    return cluster_results

def flush_vector_db():
    pinecone.delete_index('clustering')
    pinecone.create_index("clustering", dimension=1536)

def isolation_cluster(embeddings):
    isolation = IsolationForest(random_state=0, contamination=float(0.01))
    isolation.fit(embeddings)
    anomaly = isolation.predict(embeddings)
    print(anomaly)
    return anomaly

def find_isolation():
    isolation_results = []
    [vectors, values, metadata] = list_all_embeddings()
    isolations = isolation_cluster(values)
    for index in range(len(isolations)):
        isolation = isolations[index]
        if isolation == -1:
            isolation_results.append(metadata[index]['symptom'])
    return isolation_results

def handle_insert(data):
    try:
        for symptom in data['symptoms']:
            insert_vector_db(data['patientId'], symptom)
    except Exception as error:
        print(f"Error in handle insert {error}")
        return error

def handle_search():
    try:
        return search_vector_db()
    except Exception as error:
        print(f"Error in handle search {error}")
        return error

def handle_isolation():
    try:
        return find_isolation()
    except Exception as error:
        print(f"Error in handle isolation {error}")
        return error