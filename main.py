import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime


def scrape_olx_car_covers():

    url = "https://www.olx.in/items/q-car-cover"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')


        listings = soup.find_all('div', {'class': '_2grJG'})  # OLX listing class


        data = []
        for listing in listings:
            title = listing.find('span', {'class': '_2poNJ'}).text.strip() if listing.find('span', {
                'class': '_2poNJ'}) else 'N/A'
            price = listing.find('span', {'class': '_2Ks63'}).text.strip() if listing.find('span', {
                'class': '_2Ks63'}) else 'N/A'
            location = listing.find('span', {'class': '_2VQu4'}).text.strip() if listing.find('span', {
                'class': '_2VQu4'}) else 'N/A'
            link = listing.find('a')['href'] if listing.find('a') else 'N/A'
            if not link.startswith('http'):
                link = f"https://www.olx.in{link}"

            data.append({
                'Title': title,
                'Price': price,
                'Location': location,
                'Link': link
            })

       
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"olx_car_covers_{timestamp}.csv"

        # Write data to CSV file
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Price', 'Location', 'Link']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for item in data:
                writer.writerow(item)

        print(f"Successfully scraped {len(data)} car cover listings. Saved to {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from OLX: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    scrape_olx_car_covers()