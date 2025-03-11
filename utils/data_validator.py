import json
import os
from typing import List, Dict, Any
import pandas as pd

# File paths
PRODUCTS_FILE = "data/products.json"
INGREDIENTS_FILE = "data/ingredients.json"
SALES_FILE = "data/sales.json"

# Validation results
validation_results = {
    "products": [],
    "ingredients": [],
    "sales": [],
    "summary": []
}

# Load JSON files
def load_json(file_path: str) -> List[Dict[str, Any]]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        validation_results["summary"].append(f"Error loading {file_path}: {str(e)}")
        return []

# Load data
products_data = load_json(PRODUCTS_FILE)
ingredients_data = load_json(INGREDIENTS_FILE)
sales_data = load_json(SALES_FILE)

# Validate Products
product_ids = set()
product_names = set()
for product in products_data:
    if "id" not in product or not isinstance(product["id"], int):
        validation_results["products"].append(f"Invalid or missing 'id' in product: {product}")
    else:
        if product["id"] in product_ids:
            validation_results["products"].append(f"Duplicate product ID found: {product['id']}")
        product_ids.add(product["id"])

    if "name" not in product or not isinstance(product["name"], str):
        validation_results["products"].append(f"Invalid or missing 'name' in product: {product}")
    else:
        if product["name"] in product_names:
            validation_results["products"].append(f"Duplicate product name found: {product['name']}")
        product_names.add(product["name"])

    required_fields = ["type", "description", "effects", "ingredients", "price", "sales_data"]
    for field in required_fields:
        if field not in product:
            validation_results["products"].append(f"Missing field '{field}' in product ID: {product['id']}")

# Validate Ingredients
ingredient_names = set()
for ingredient in ingredients_data:
    if "name" not in ingredient or not isinstance(ingredient["name"], str):
        validation_results["ingredients"].append(f"Invalid or missing 'name' in ingredient: {ingredient}")
    else:
        if ingredient["name"] in ingredient_names:
            validation_results["ingredients"].append(f"Duplicate ingredient name found: {ingredient['name']}")
        ingredient_names.add(ingredient["name"])

    if "properties" not in ingredient or not isinstance(ingredient["properties"], str):
        validation_results["ingredients"].append(f"Invalid or missing 'properties' in ingredient: {ingredient}")

    if "common_effects" not in ingredient or not isinstance(ingredient["common_effects"], list):
        validation_results["ingredients"].append(f"Invalid or missing 'common_effects' in ingredient: {ingredient}")

# Validate Sales Data
for sale in sales_data:
    if "product_id" not in sale or not isinstance(sale["product_id"], int):
        validation_results["sales"].append(f"Invalid or missing 'product_id' in sales data: {sale}")
    elif sale["product_id"] not in product_ids:
        validation_results["sales"].append(f"Product ID {sale['product_id']} in sales data not found in products.json")

    if "daily_sales" not in sale or not isinstance(sale["daily_sales"], list):
        validation_results["sales"].append(f"Missing 'daily_sales' in sales data for product ID: {sale['product_id']}")

    for daily_sale in sale.get("daily_sales", []):
        if "date" not in daily_sale or "units_sold" not in daily_sale:
            validation_results["sales"].append(f"Invalid daily sales entry: {daily_sale}")

# Display DataFrame to user
def display_dataframe_to_user(name: str, dataframe: pd.DataFrame) -> None:
    """
    Displays a Pandas DataFrame to the user with a title.
    """
    print(f"\n{name}:")
    print(dataframe.to_string(index=False))

# Generate validation report
def generate_report() -> None:
    report_data = []
    for category, issues in validation_results.items():
        for issue in issues:
            report_data.append({"Category": category, "Issue": issue})

    df = pd.DataFrame(report_data)
    display_dataframe_to_user(name="Validation Report", dataframe=df)

generate_report()