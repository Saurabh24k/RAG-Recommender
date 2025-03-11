# recommender.py
from typing import List, Dict, Any
import chromadb
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer
import json
import os

class RecommendationEngine:
    def __init__(self, collection_name: str = "products"):
        """Initialize the recommendation engine with a persistent ChromaDB client and SentenceTransformer model."""
        self.client = chromadb.PersistentClient(path="rag/knowledge_base/chroma_db")
        self.collection = self._get_or_create_collection(collection_name)
        self.model = SentenceTransformer('BAAI/bge-large-en-v1.5')

    def _get_or_create_collection(self, name: str) -> Collection:
        """Retrieve or create a ChromaDB collection with cosine similarity metric."""
        try:
            return self.client.get_collection(name)
        except Exception:
            print(f"Creating new collection: {name} with cosine metric")
            return self.client.create_collection(name, metadata={"hnsw:space": "cosine"})

    def _parse_metadata(self, raw_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Parse metadata from ChromaDB, providing defaults for missing fields."""
        return {
            "id": raw_meta.get("id", -1),
            "name": raw_meta.get("name", "Unknown Product"),
            "effects": raw_meta.get("effects", []),
            "ingredients": raw_meta.get("ingredients", []),
            "price": raw_meta.get("price", 0.0),
            "description": raw_meta.get("description", "No description available."),
            "type": raw_meta.get("type", "Unknown Type"),
            "sales_velocity": raw_meta.get("sales_velocity", 0.0),
            "similarity_score": 0.0,
            "weighted_score": 0.0
        }

    def _calculate_weighted_score(self, recommendations: List[Dict[str, Any]]) -> None:
        """Calculate weighted scores combining normalized similarity and sales velocity."""
        if not recommendations:
            return

        max_similarity = max(p["similarity_score"] for p in recommendations) or 1
        max_sales = max(p["sales_velocity"] for p in recommendations) or 1

        for product in recommendations:
            similarity_norm = product["similarity_score"] / max_similarity
            sales_norm = product["sales_velocity"] / max_sales
            product["weighted_score"] = (0.7 * similarity_norm) + (0.3 * sales_norm)

    def get_recommendations(self, query: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Retrieve top-N recommendations based on query, ranked by similarity and sales."""
        try:
            query_embedding = self.model.encode([query], normalize_embeddings=True).tolist()
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_n,
                include=["metadatas", "distances"]
            )

            recommendations = []
            for meta, distance in zip(results["metadatas"][0], results["distances"][0]):
                product = self._parse_metadata(meta)
                product["similarity_score"] = 1 - distance  # Cosine similarity (-1 to 1)
                recommendations.append(product)

            self._calculate_weighted_score(recommendations)
            return sorted(recommendations, key=lambda x: x["weighted_score"], reverse=True)

        except Exception as e:
            print(f"Recommendation error: {e}")
            return []

    def initialize_data(self, json_path: str = "products.json", days_period: int = 30):
        """Initialize or update ChromaDB with product data from JSON."""
        if not os.path.exists(json_path):
            print(f"Error: File {json_path} not found!")
            return
        
        with open(json_path) as f:
            products = json.load(f)

        # Identify current IDs to remove outdated products
        try:
            current_ids = set(self.collection.get()["ids"])
        except Exception:
            current_ids = set()
        new_ids = set(str(product.get("id", -1)) for product in products)
        ids_to_delete = list(current_ids - new_ids)
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)

        # Prepare data for upsert
        documents = []
        metadatas = []
        ids = []

        for product in products:
            sales_data = product.get("sales_data", {})
            try:
                units_sold = float(sales_data.get("units_sold", 0))
            except (ValueError, TypeError):
                units_sold = 0
            sales_velocity = units_sold / days_period if units_sold else 0

            metadata = {
                "id": product.get("id", -1),
                "name": product.get("name", "Unknown Product"),
                "effects": product.get("effects", []),
                "ingredients": product.get("ingredients", []),
                "price": product.get("price", 0.0),
                "description": product.get("description", ""),
                "type": product.get("type", "Unknown Type"),
                "sales_velocity": sales_velocity
            }

            doc_text = " ".join([
                metadata["description"],
                " ".join(metadata["effects"]),
                " ".join(metadata["ingredients"]),
                metadata["type"]
            ])

            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(str(product.get("id", -1)))

        # Generate embeddings and upsert
        try:
            embeddings = self.model.encode(documents, normalize_embeddings=True).tolist()
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            print(f"✅ Successfully indexed {len(products)} products")
        except Exception as e:
            print(f"Data initialization failed: {e}")