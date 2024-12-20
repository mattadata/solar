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
    'refinements': 'brand'
}

def extract_voltage(title):
    """Extract voltage from the product title."""
    match = re.search(r'\b(12V|24V|36V|48V)\b', title)
    return match.group(0) if match else 'N/A'

# Make the HTTP GET request to ASIN Data API
try:
    response = requests.get('https://api.asindataapi.com/request', params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    # Print the number of products in the search results
    print(f"Number of products found: {len(data.get('search_results', []))}")

    # Extract the relevant information for each product
    products = []
    for product in data.get('search_results', []):
        title = product.get('title', 'N/A')
        
        # Skip titles containing the word "generator"
        if 'generator' in title.lower():
            continue
        
        brand = product.get('brand', 'N/A')
        price = product.get('price', {}).get('value', 'N/A')
        link = product.get('link', 'N/A')
        voltage = extract_voltage(title)
        
        products.append([brand, voltage, price, title, link])
    
    # Write the data to a CSV file
    csv_file = 'lifepo4_products_filtered2.csv'
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Brand', 'Voltage', 'Price', 'Title', 'Link'])  # Header
        writer.writerows(products)

    print(f"Data successfully saved to {csv_file}")
except requests.exceptions.RequestException as e:
    print(f"HTTP Request failed: {e}")
except json.JSONDecodeError:
    print("Failed to parse JSON response")
except Exception as e:
    print(f"An error occurred: {e}")
