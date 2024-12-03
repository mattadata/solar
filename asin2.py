import requests
import json
import csv
import re

# Set up the request parameters
params = {
    'api_key': 'FC7BC161BEE04E3A84A95036A15AE035',
    'type': 'search',
    'amazon_domain': 'amazon.com',
    'search_term': 'LifePO4',
    'refinements': 'brand',
    'page': 1  # Start from the first page
}

def extract_voltage(title):
    """Extract voltage from the product title."""
    match = re.search(r'\b(12V|24V|36V|48V)\b', title)
    return match.group(0) if match else 'N/A'

# Gather all products
products = []

try:
    while True:
        response = requests.get('https://api.asindataapi.com/request', params=params)
        response.raise_for_status()
        data = response.json()

        # Extract and process product data
        for product in data.get('search_results', []):
            title = product.get('title', 'N/A')
            if 'generator' in title.lower():
                continue

            brand = product.get('brand', 'N/A')
            price = product.get('price', {}).get('value', 'N/A')
            link = product.get('link', 'N/A')
            voltage = extract_voltage(title)

            products.append([brand, voltage, price, title, link])

        # Check if there are more pages
        if params['page'] >= data.get('pagination', {}).get('total_pages', 0):
            break

        params['page'] += 1  # Move to the next page

    # Save to CSV
    csv_file = 'lifepo4_products_filtered.csv'
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Brand', 'Voltage', 'Price', 'Title', 'Link'])
        writer.writerows(products)

    print(f"Data successfully saved to {csv_file}")
except requests.exceptions.RequestException as e:
    print(f"HTTP Request failed: {e}")
