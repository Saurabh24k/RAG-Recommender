import json
import os

# Define the paths to the data files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_FILE = os.path.join(BASE_DIR, 'data', 'products.json')
INGREDIENTS_FILE = os.path.join(BASE_DIR, 'data', 'ingredients.json')
SALES_FILE = os.path.join(BASE_DIR, 'data', 'sales.json')

class DataLoader:
    def __init__(self):
        self.products = self.load_json(PRODUCTS_FILE)
        self.ingredients = self.load_json(INGREDIENTS_FILE)
        self.sales = self.load_json(SALES_FILE)

    @staticmethod
    def load_json(filepath: str):
        """Load data from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON file: {filepath}")
            return []

    def get_products(self):
        return self.products

    def get_ingredients(self):
        return self.ingredients

    def get_sales(self):
        return self.sales

# Test the DataLoader
if __name__ == '__main__':
    loader = DataLoader()
    print("Products:", loader.get_products())
    print("Ingredients:", loader.get_ingredients())
    print("Sales:", loader.get_sales())
