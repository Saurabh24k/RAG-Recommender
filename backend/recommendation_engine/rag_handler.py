import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from tqdm import tqdm

# ChromaDB and embedding model setup
MODEL_NAME = "BAAI/bge-large-en-v1.5"
CHROMA_DB_DIR = "rag/knowledge_base/chroma_db"
COLLECTION_NAME = "products"

# Initialize embedding model
print(f"Loading model '{MODEL_NAME}'...")
model = SentenceTransformer(MODEL_NAME)

# Load ChromaDB collection
def get_chroma_collection():
    print("Connecting to ChromaDB collection...")
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)
    return collection

# Perform a query on the ChromaDB collection
def query_chroma_db(query: str, top_n: int = 5) -> list:
    collection = get_chroma_collection()

    # Generate embedding for the query
    print("Generating embedding for the query...")
    query_embedding = model.encode([query])

    print(f"Querying ChromaDB for the top {top_n} results...")
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_n,
        include=["metadata", "distance"]
    )
    
    # Extract relevant metadata from results
    recommendations = []
    for item in results['documents'][0]:
        recommendations.append(item)

    return recommendations

# Test the query function
if __name__ == '__main__':
    test_query = "relaxation"
    print(f"Testing query for '{test_query}'...")
    results = query_chroma_db(test_query, top_n=5)
    for i, result in enumerate(results):
        print(f"{i+1}. {result}")
