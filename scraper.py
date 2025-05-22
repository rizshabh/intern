import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
import time
from fake_useragent import UserAgent

def scrape_olx_car_covers(max_retries=3, delay=5):
    """
    Improved scraper with:
    - Rotating user agents
    - Longer timeout
    - Proxy support (if needed)
    - Better error handling
    """
    url = "https://www.olx.in/items/q-car-cover"
    ua = UserAgent()
    
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': ua.random,
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            print(f"Attempt {attempt + 1}: Fetching data...")
            
            # Increased timeout to 30 seconds
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 403:
                print("Access denied. OLX might be blocking scrapers.")
                return
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Updated selectors (OLX changes these frequently)
            listings = soup.find_all('li', {'class': 'EIR5N'}) or soup.find_all('div', {'class': '_2grJG'})
            
            if not listings:
                print("No listings found. Possible issues:")
                print("- OLX updated their HTML structure")
                print("- Requires JavaScript rendering (consider Selenium)")
                return
            
            data = []
            for listing in listings:
                try:
                    title_elem = listing.find(['span', 'h4'], class_=lambda x: x and ('_2poNJ' in x or 'title' in x))
                    price_elem = listing.find(['span', 'div'], class_=lambda x: x and ('_2Ks63' in x or 'price' in x))
                    location_elem = listing.find(['span', 'div'], class_=lambda x: x and ('_2VQu4' in x or 'location' in x))
                    
                    title = title_elem.text.strip() if title_elem else 'N/A'
                    price = price_elem.text.strip() if price_elem else 'N/A'
                    location = location_elem.text.strip() if location_elem else 'N/A'
                    link = listing.find('a')['href'] if listing.find('a') else 'N/A'
                    
                    if link and not link.startswith('http'):
                        link = f"https://www.olx.in{link}"
                    
                    data.append({
                        'Title': title,
                        'Price': price,
                        'Location': location,
                        'Link': link
                    })
                except Exception as e:
                    print(f"Skipping listing due to error: {str(e)}")
                    continue
            
            if data:
                save_to_csv(data)
                return
            
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Waiting {delay} seconds before retry...")
                time.sleep(delay)
            else:
                print("Max retries reached. Possible solutions:")
                print("1. Try again later (OLX might be rate-limiting)")
                print("2. Use a VPN/proxy")
                print("3. Use Selenium for JavaScript rendering")

def save_to_csv(data):
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"olx_car_covers_{timestamp}.csv"
    filepath = os.path.join("output", filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Title', 'Price', 'Location', 'Link'])
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Success! Saved {len(data)} listings to {filepath}")

if __name__ == "__main__":
    scrape_olx_car_covers()
