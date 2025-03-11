from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import pandas as pd
import logging
import chromadb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import DataLoader
from backend.recommendation_engine.recommender import RecommendationEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize components
data_loader = DataLoader()
recommendation_engine = RecommendationEngine()

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to ChromaDB
client = chromadb.PersistentClient(path="rag/knowledge_base/chroma_db")
collection = client.get_collection("products")

# Predefined Popular Keywords
POPULAR_KEYWORDS = ["relaxation", "stress relief", "energy boost", "sleep aid", "focus", "hydration"]

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/products")
def get_products():
    return data_loader.get_products()

@app.get("/ingredients")
def get_ingredients():
    return data_loader.get_ingredients()

@app.get("/sales")
def get_sales():
    return data_loader.get_sales()

@app.get("/suggestions")
async def get_suggestions(query: str = Query(..., min_length=1)):
    """Returns suggested search keywords based on user input."""
    query_lower = query.lower()

    # Fetch all metadata entries
    results = collection.get(include=["metadatas"])

    # Extract product names
    all_names = [meta["name"].lower() for meta in results["metadatas"] if "name" in meta]

    # Filter names that contain the query
    filtered_suggestions = [name.title() for name in all_names if query_lower in name]

    # Combine with predefined keywords
    suggestions = list(set(POPULAR_KEYWORDS + filtered_suggestions))[:5]

    return suggestions


@app.get("/recommendations")
async def get_recommendations(query: str = Query(..., min_length=1)):
    recommendations = recommendation_engine.get_recommendations(query)

    if not recommendations:
        logger.warning("No recommendations found.")
        return []

    df = pd.DataFrame(recommendations)

    # Log column names to check missing fields
    logger.info(f"DataFrame Columns: {df.columns.tolist()}")

    # Ensure essential fields exist
    for col in ["description", "effects", "ingredients", "type", "price"]:
        if col not in df.columns:
            logger.warning(f"Warning: '{col}' column is missing. Filling with default values.")
            df[col] = "Unknown" if col != "price" else 1.0  # Default price to 1.0

    # Convert necessary columns to correct types
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(1.0)
    
    # Ensure `effects` and `ingredients` are lists (not empty strings)
    df["effects"] = df["effects"].apply(lambda x: x if isinstance(x, list) else [])
    df["ingredients"] = df["ingredients"].apply(lambda x: x if isinstance(x, list) else [])

    # Calculate weighted score (favoring similarity and price)
    df["weighted_score"] = (
        df["similarity_score"] * 0.8 +  # 80% similarity
        (1 / df["price"].replace(0, 1)) * 0.2  # 20% price influence (avoiding division by zero)
    )

    # Sort results by weighted score
    df = df.sort_values(by="weighted_score", ascending=False)

    # Log top recommendations
    logger.info(f"Top Recommendations:\n{df[['name', 'weighted_score']].head(5)}")

    return df.head(10).to_dict(orient="records")
