import os
import json
from tqdm import tqdm
import numpy as np
from sentence_transformers import SentenceTransformer

# Define file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_FILE = os.path.join(BASE_DIR, 'data', 'products.json')
EMBEDDINGS_FILE = os.path.join(BASE_DIR, 'rag', 'knowledge_base', 'product_embeddings.npy')
METADATA_FILE = os.path.join(BASE_DIR, 'rag', 'knowledge_base', 'product_metadata.json')

# Load product data
def load_product_data(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Generate embeddings for product descriptions
def generate_embeddings(model_name: str = 'BAAI/bge-large-en-v1.5'):
    print("Loading product data...")
    products = load_product_data(PRODUCTS_FILE)

    descriptions = [product['description'] for product in products]
    product_ids = [product['id'] for product in products]
    metadata = [{'id': product['id'], 'name': product['name']} for product in products]

    # Load the embedding model
    print(f"Loading model '{model_name}'...")
    model = SentenceTransformer(model_name)

    # Generate embeddings with progress indicator
    print("Generating embeddings...")
    embeddings = []
    for desc in tqdm(descriptions, desc="Embedding Descriptions", unit="desc"):
        embedding = model.encode(desc)
        embeddings.append(embedding)

    # Convert to numpy array for efficient storage
    embeddings = np.array(embeddings)

    # Save embeddings and metadata
    os.makedirs(os.path.dirname(EMBEDDINGS_FILE), exist_ok=True)
    np.save(EMBEDDINGS_FILE, embeddings)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"Embeddings saved to {EMBEDDINGS_FILE}")
    print(f"Metadata saved to {METADATA_FILE}")

# Run the embedding generation
if __name__ == '__main__':
    generate_embeddings()
