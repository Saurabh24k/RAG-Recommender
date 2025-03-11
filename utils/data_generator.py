import json
import os
import random
from faker import Faker
from datetime import datetime, timedelta
from ollama import Client  # Updated import
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# Initialize Faker for random data generation
fake = Faker()

# Define paths for generated data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_FILE = os.path.join(BASE_DIR, 'data', 'products.json')
INGREDIENTS_FILE = os.path.join(BASE_DIR, 'data', 'ingredients.json')
SALES_FILE = os.path.join(BASE_DIR, 'data', 'sales.json')

# Define data generation parameters
NUM_PRODUCTS = 500
NUM_INGREDIENTS = 200
NUM_SALES_DAYS = 90  # Generate sales data for the last 90 days

# Define realistic sample data
PRODUCT_TYPES = ['beverage', 'supplement', 'snack', 'vitamin', 'oil']
EFFECTS = [
    'relaxation', 'energy', 'focus', 'immunity', 'stress relief', 
    'sleep support', 'anti-inflammatory', 'detox', 'digestive health', 
    'skin health', 'weight management', 'mood enhancement'
]
INGREDIENTS_LIST = [
    'Chamomile', 'Ginseng', 'Lavender', 'Turmeric', 'Ashwagandha', 
    'Peppermint', 'Lemon Balm', 'Valerian Root', 'Green Tea', 'Caffeine',
    'Echinacea', 'Elderberry', 'Ginger', 'Aloe Vera', 'Coconut Oil'
]
PRODUCT_PREFIXES = ['Organic', 'Natural', 'Herbal', 'Advanced', 'Premium']
PRODUCT_SUFFIXES = ['Tea', 'Capsules', 'Oil', 'Drink', 'Powder']

# Function to generate product descriptions using Ollama
def generate_description(prompt: str) -> str:
    try:
        # Initialize Ollama client
        client = Client(host='http://localhost:11434')  # Default Ollama server URL
        response = client.generate(model="llama3.2:latest", prompt=prompt)
        return response['response'].strip()
    except Exception as e:
        print("Ollama Model Error:", e)
        return fake.sentence(nb_words=12)

# Function to generate random ingredients with unique names
def generate_ingredients(num_ingredients):
    ingredients = []
    used_names = set()

    print("Generating Ingredients...")
    for _ in tqdm(range(num_ingredients), desc="Ingredients"):
        name = random.choice(INGREDIENTS_LIST) + " Extract"
        if name not in used_names:
            properties = fake.sentence(nb_words=6)
            common_effects = random.sample(EFFECTS, random.randint(1, 3))
            ingredients.append({
                'name': name,
                'properties': properties,
                'common_effects': common_effects
            })
            used_names.add(name)
    return ingredients

# Function to generate random products with realistic descriptions
def generate_products(num_products, ingredients):
    products = []
    used_names = set()
    
    print("Generating Products...")
    for i in tqdm(range(1, num_products + 1), desc="Products"):
        max_attempts = 10
        name = ""
        
        # Ensure unique product name generation with retry mechanism
        for attempt in range(max_attempts):
            name = f"{random.choice(PRODUCT_PREFIXES)} {random.choice(PRODUCT_SUFFIXES)}"
            if name not in used_names:
                used_names.add(name)
                break
            if attempt == max_attempts - 1:
                name = f"{name} {i}"  # Force uniqueness by appending ID
        
        product_type = random.choice(PRODUCT_TYPES)
        effects = random.sample(EFFECTS, random.randint(1, 3))
        product_ingredients = random.sample([ing['name'] for ing in ingredients], random.randint(2, 5))
        price = round(random.uniform(5.0, 50.0), 2)
        units_sold = random.randint(50, 500)
        last_month_revenue = round(units_sold * price, 2)

        # Generate a realistic product description using the local model
        prompt = f"Generate a product description for a {product_type} called '{name}' that promotes {', '.join(effects)}."
        description = generate_description(prompt)

        products.append({
            'id': i,
            'name': name,
            'type': product_type,
            'description': description,
            'effects': effects,
            'ingredients': product_ingredients,
            'price': price,
            'sales_data': {
                'units_sold': units_sold,
                'last_month_revenue': last_month_revenue
            }
        })
    
    return products

# Function to generate random sales data
def generate_sales_data(products, num_days):
    sales_data = []
    start_date = datetime.today() - timedelta(days=num_days)
    
    print("Generating Sales Data...")
    for product in tqdm(products, desc="Sales Data"):
        daily_sales = []
        for day in range(num_days):
            date = (start_date + timedelta(days=day)).strftime('%Y-%m-%d')
            units_sold = random.randint(1, 10)
            daily_sales.append({'date': date, 'units_sold': units_sold})
        
        sales_data.append({
            'product_id': product['id'],
            'daily_sales': daily_sales
        })
    
    return sales_data

# Function to save data to JSON files
def save_data_to_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {file_path}")

# Main function to generate and save mock data
def generate_mock_data():
    # Generate data
    ingredients = generate_ingredients(NUM_INGREDIENTS)
    products = generate_products(NUM_PRODUCTS, ingredients)
    sales_data = generate_sales_data(products, NUM_SALES_DAYS)

    # Save data to JSON files
    save_data_to_json(INGREDIENTS_FILE, ingredients)
    save_data_to_json(PRODUCTS_FILE, products)
    save_data_to_json(SALES_FILE, sales_data)

# Run the data generation if this file is executed
if __name__ == '__main__':
    generate_mock_data()