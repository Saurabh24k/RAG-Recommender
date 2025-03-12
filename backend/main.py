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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize components
data_loader = DataLoader()
recommendation_engine = RecommendationEngine()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = chromadb.PersistentClient(path="rag/knowledge_base/chroma_db")
collection = client.get_collection("products")

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

    results = collection.get(include=["metadatas"])

    all_names = [meta["name"].lower() for meta in results["metadatas"] if "name" in meta]

    filtered_suggestions = [name.title() for name in all_names if query_lower in name]

    suggestions = list(set(POPULAR_KEYWORDS + filtered_suggestions))[:5]

    return suggestions


@app.get("/recommendations")
async def get_recommendations(query: str = Query(..., min_length=1)):
    recommendations = recommendation_engine.get_recommendations(query)

    if not recommendations:
        logger.warning("No recommendations found.")
        return []

    df = pd.DataFrame(recommendations)

    logger.info(f"DataFrame Columns: {df.columns.tolist()}")

    for col in ["description", "effects", "ingredients", "type", "price"]:
        if col not in df.columns:
            logger.warning(f"Warning: '{col}' column is missing. Filling with default values.")
            df[col] = "Unknown" if col != "price" else 1.0  # Default price to 1.0

    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(1.0)
    
    df["effects"] = df["effects"].apply(lambda x: x if isinstance(x, list) else [])
    df["ingredients"] = df["ingredients"].apply(lambda x: x if isinstance(x, list) else [])

    df["weighted_score"] = (
        df["similarity_score"] * 0.8 +  # 80% similarity
        (1 / df["price"].replace(0, 1)) * 0.2  # 20% price influence
    )

    df = df.sort_values(by="weighted_score", ascending=False)

    logger.info(f"Top Recommendations:\n{df[['name', 'weighted_score']].head(5)}")

    return df.head(10).to_dict(orient="records")


if __name__ == "__main__":
    import uvicorn

    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
