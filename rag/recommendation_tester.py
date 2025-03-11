import pandas as pd
import json
import os
from tqdm import tqdm
from tabulate import tabulate
from rag.recommendation_engine import RecommendationEngine

# File paths
RESULTS_FILE = "recommendation_test_results_advanced.csv"

# Initialize the recommendation engine
recommendation_engine = RecommendationEngine()

# Test queries, including a mix of general, specific, and edge cases
test_queries = [
    "relaxation", "energy", "focus", "detox", "skin health",
    "stress relief", "sleep", "digestive health", "mood enhancement",
    "weight management", "immunity", "anti-inflammatory",
    "boost immunity", "enhance focus", "improve sleep"
]

# Weights for advanced ranking
WEIGHTS = {
    "similarity_score": 0.5,
    "units_sold": 0.2,
    "revenue": 0.2,
    "price": 0.1
}

# Function to calculate weighted score
def calculate_weighted_score(row, weights):
    return (
        row["similarity_score"] * weights["similarity_score"] +
        row["units_sold"] * weights["units_sold"] +
        row["revenue"] * weights["revenue"] +
        (1 / row["price"]) * weights["price"]  # Lower price is better
    )

# Collect results
results = []
print("Testing recommendation engine with various queries...")
for query in tqdm(test_queries, desc="Testing Queries"):
    recommendations = recommendation_engine.get_recommendations(query)
    for rec in recommendations:
        results.append({
            "query": query,
            "product_id": rec["id"],
            "product_name": rec["name"],
            "description": rec["description"],
            "price": rec["price"],
            "units_sold": rec["sales_data"]["units_sold"],
            "revenue": rec["sales_data"]["last_month_revenue"],
            "similarity_score": rec.get("similarity_score", 1.0)  # Default to 1.0 if not present
        })

# Create DataFrame
df = pd.DataFrame(results)

# Apply advanced ranking
print("Applying advanced scoring and ranking...")
df["weighted_score"] = df.apply(lambda row: calculate_weighted_score(row, WEIGHTS), axis=1)
df = df.sort_values(by=["weighted_score"], ascending=False)

# Display top recommendations
top_recommendations = df.head(10)
print("\nTop Recommendations Based on Advanced Scoring:")
print(tabulate(top_recommendations, headers="keys", tablefmt="psql"))

# Save results to CSV
df.to_csv(RESULTS_FILE, index=False)
print(f"Test results saved to {RESULTS_FILE}")
