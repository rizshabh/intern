import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
import time

def scrape_olx_car_covers(max_retries=3, delay=2):
    """
    Scrapes car cover listings from OLX and saves them to a CSV file.
    
    Args:
        max_retries (int): Max retries if request fails.
        delay (int): Delay between retries (seconds).
    """
    url = "https://www.olx.in/items/q-car-cover"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    data = []
    retries = 0
    
    while retries < max_retries:
        try:
            print("Fetching data from OLX...")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = soup.find_all('li', {'class': 'EIR5N'})  # Updated class for listings
            
            if not listings:
                print("No listings found. Check if OLX structure changed.")
                return
            
            for listing in listings:
                try:
                    title = listing.find('span', {'class': '_2poNJ'}).text.strip() if listing.find('span', {'class': '_2poNJ'}) else 'N/A'
                    price = listing.find('span', {'class': '_2Ks63'}).text.strip() if listing.find('span', {'class': '_2Ks63'}) else 'N/A'
                    location = listing.find('span', {'class': '_2VQu4'}).text.strip() if listing.find('span', {'class': '_2VQu4'}) else 'N/A'
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
                    print(f"Error parsing listing: {e}")
                    continue
            
            break  # Success, exit retry loop
            
        except requests.exceptions.RequestException as e:
            retries += 1
            print(f"Attempt {retries} failed: {e}")
            if retries < max_retries:
                time.sleep(delay)
            else:
                print("Max retries reached. Exiting.")
                return
    
    if not data:
        print("No data scraped.")
        return
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"olx_car_covers_{timestamp}.csv"
    
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Price', 'Location', 'Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Success! Saved {len(data)} listings to {filepath}")

if __name__ == "__main__":
    scrape_olx_car_covers()
