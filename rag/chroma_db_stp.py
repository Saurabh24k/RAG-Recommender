import os
import json
import numpy as np
from tqdm import tqdm
import chromadb
from sentence_transformers import SentenceTransformer

EMBEDDINGS_FILE = "data/product_embeddings.npy"
PRODUCTS_FILE = "data/products.json"
CHROMA_DB_DIR = "rag/knowledge_base/chroma_db"

def load_products():
    print("Loading product data...")
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def setup_chroma_db():
    print("Initializing ChromaDB...")
    return chromadb.PersistentClient(path=CHROMA_DB_DIR)

def populate_chroma_db(products, collection_name="products"):
    model = SentenceTransformer('BAAI/bge-large-en-v1.5')
    client = setup_chroma_db()
    
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    print("Storing product data in ChromaDB...")
    for product in tqdm(products):
        # Data validation
        required_fields = ["id", "name", "effects", "ingredients", "description"]
        for field in required_fields:
            if field not in product:
                raise ValueError(f"Missing required field {field} in product {product.get('id','unknown')}")

        # Generate embedding
        text_to_embed = f"{product['name']}: {product['description']}"
        embedding = model.encode(text_to_embed, normalize_embeddings=True).tolist()
        
        # Format metadata
        formatted_meta = {
            "id": str(product["id"]),
            "name": product["name"],
            "effects": "|||".join(product["effects"]),
            "ingredients": "|||".join(product["ingredients"]),
            "price": float(product["price"]),
            "description": product["description"],
            "type": product["type"],
            "sales_velocity": float(product.get("sales_data", {}).get("last_month_revenue", 0.0))
        }

        # Add to collection
        collection.add(
            ids=[formatted_meta["id"]],
            embeddings=[embedding],
            metadatas=[formatted_meta]
        )

    print(f"ChromaDB updated with {len(products)} products")

if __name__ == '__main__':
    products = load_products()
    populate_chroma_db(products)
