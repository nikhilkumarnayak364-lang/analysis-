"""
data_generator.py
-----------------
Generates realistic retail transaction dataset for college project:
'Exploring Customer Purchasing Patterns for Understanding Product Preferences and Sales Trends in Retail Data'

Output format: CSV with >= 1,000 rows and internally consistent values:
- Total_Amount = Quantity * Unit_Price
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def generate_retail_data(num_records: int = 2500, random_seed: int = 42) -> pd.DataFrame:
    """
    Generate a realistic, consistent retail transaction dataset.
    
    Args:
        num_records: Number of transactions to generate (default: 2500, min 1000).
        random_seed: Seed for reproducibility.
        
    Returns:
        pd.DataFrame containing the generated retail transactions.
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    # 1. Product Catalog Definition (Category -> list of (Product Name, Base Price))
    catalog = {
        "Electronics": [
            ("Wireless Bluetooth Headphones", 79.99),
            ("Smart Fitness Watch", 129.50),
            ("4K Ultra HD Action Camera", 199.00),
            ("Portable Bluetooth Speaker", 49.99),
            ("USB-C Fast Charging Hub", 29.99),
            ("Noise-Cancelling Earbuds", 89.00),
            ("Mechanical Gaming Keyboard", 109.95),
            ("Ergonomic Wireless Mouse", 34.50),
        ],
        "Clothing & Apparel": [
            ("Classic Cotton T-Shirt", 24.99),
            ("Slim Fit Denim Jeans", 59.90),
            ("Breathable Running Hoodie", 45.00),
            ("Waterproof Winter Jacket", 119.99),
            ("Athletic Crew Socks (3-Pack)", 14.50),
            ("Casual Chino Trousers", 49.00),
            ("Formal Dress Shirt", 39.99),
        ],
        "Home & Kitchen": [
            ("Stainless Steel Electric Kettle", 39.99),
            ("Compact Digital Air Fryer", 89.99),
            ("Non-Stick Cookware Set", 129.00),
            ("Ceramic Coffee Mug Set", 22.50),
            ("Multi-Function Food Blender", 64.95),
            ("Aroma Oil Diffuser", 27.00),
            ("Memory Foam Bed Pillow", 35.00),
        ],
        "Beauty & Personal Care": [
            ("Hydrating Hyaluronic Face Serum", 28.50),
            ("SPF 50 Daily Sunscreen", 21.00),
            ("Herbal Shampoo & Conditioner Set", 24.99),
            ("Organic Botanical Face Wash", 18.50),
            ("Deep Nourishing Body Cream", 16.00),
            ("Electric Sonic Toothbrush", 45.00),
        ],
        "Books & Stationery": [
            ("Data Science & Python Handbook", 38.00),
            ("The Art of Modern Management", 24.50),
            ("Hardcover Dotted Journal", 15.99),
            ("Fine Tip Gel Pen Set (12-pack)", 12.50),
            ("Science Fiction Bestseller Novel", 18.00),
            ("Desk Planner & Calendar", 14.00),
        ],
        "Sports & Fitness": [
            ("Eco-Friendly Yoga Mat", 29.99),
            ("Adjustable Neoprene Dumbbell Set", 69.50),
            ("Insulated Stainless Steel Water Bottle", 24.00),
            ("Resistance Bands Exercise Kit", 19.95),
            ("Quick-Dry Sports Towel", 15.00),
            ("Jump Rope with Counter", 16.50),
        ],
    }

    categories = list(catalog.keys())
    category_weights = [0.26, 0.22, 0.18, 0.14, 0.10, 0.10]

    # 2. Demographics & Geographics
    cities = [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston",
        "Seattle",
        "Austin",
        "Miami",
        "San Francisco",
    ]
    city_weights = [0.20, 0.18, 0.14, 0.12, 0.10, 0.09, 0.09, 0.08]

    payment_methods = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash"]
    payment_weights = [0.38, 0.22, 0.20, 0.12, 0.08]

    genders = ["Female", "Male", "Other"]
    gender_weights = [0.50, 0.47, 0.03]

    # Pre-generate a customer pool of ~450 distinct customers to simulate recurring behavior
    num_customers = max(200, num_records // 5)
    customer_pool = []
    for i in range(1, num_customers + 1):
        c_id = f"CUST-{1000 + i}"
        c_gender = random.choices(genders, weights=gender_weights)[0]
        # Realistic age distribution (peaks around 25-45)
        c_age = int(np.clip(np.random.normal(loc=35, scale=12), 18, 72))
        c_city = random.choices(cities, weights=city_weights)[0]
        customer_pool.append({
            "Customer_ID": c_id,
            "Gender": c_gender,
            "Age": c_age,
            "City": c_city,
        })

    # 3. Transaction Generation across 12 months (e.g., 2024)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    total_days = (end_date - start_date).days

    records = []
    for i in range(1, num_records + 1):
        txn_id = f"TXN-{100000 + i}"

        # Select a customer (some customers buy more often)
        # Power-law distribution for recurring customers
        cust_index = int(np.random.exponential(scale=num_customers / 4)) % num_customers
        cust = customer_pool[cust_index]

        # Select date with seasonal lift towards Q4 (Nov/Dec) and weekends
        day_offset = random.randint(0, total_days)
        txn_date = start_date + timedelta(days=day_offset)

        # Category and Product
        chosen_cat = random.choices(categories, weights=category_weights)[0]
        product_list = catalog[chosen_cat]
        product_name, base_price = random.choice(product_list)

        # Quantity: 1 to 4 commonly, occasional 5
        qty = int(np.random.choice([1, 2, 3, 4, 5], p=[0.55, 0.25, 0.12, 0.05, 0.03]))

        # Unit price with subtle variation (+- 5%) rounded to 2 decimal places
        price_variation = round(base_price * random.uniform(0.95, 1.05), 2)
        total_amt = round(qty * price_variation, 2)

        # Payment method
        pay_method = random.choices(payment_methods, weights=payment_weights)[0]

        records.append({
            "Transaction_ID": txn_id,
            "Transaction_Date": txn_date.strftime("%Y-%m-%d"),
            "Customer_ID": cust["Customer_ID"],
            "Gender": cust["Gender"],
            "Age": cust["Age"],
            "Product_Category": chosen_cat,
            "Product_Name": product_name,
            "Quantity": qty,
            "Unit_Price": price_variation,
            "Total_Amount": total_amt,
            "Payment_Method": pay_method,
            "City": cust["City"],
        })

    df = pd.DataFrame(records)
    # Sort by date for logical chronological order
    df = df.sort_values("Transaction_Date").reset_index(drop=True)
    return df


def save_default_dataset(output_path: str = "data/retail_sales.csv", num_records: int = 2500) -> str:
    """Save generated retail transaction dataset to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = generate_retail_data(num_records=num_records)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} transactions and saved to '{output_path}'.")
    return output_path


if __name__ == "__main__":
    save_default_dataset()
