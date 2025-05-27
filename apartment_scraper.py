import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import random
from notify import ping_me

class ApartmentScraper:
    def __init__(self, url):
        """Initialize scraper with target URL."""
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_data(self):
        """Fetch and parse webpage."""
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return self.parse_table(soup)

    def parse_table(self, soup):
        """Extract table data from HTML."""
        availabilities = []
        table = soup.find("table")

        if not table:
            print("No table found on the page.")
            return availabilities

        headers = [header.get_text(strip=True) for header in table.find_all('th')]
        availabilities.append(headers)

        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cols = row.find_all('td')
            if cols:
                row_data = [col.get_text(strip=True) for col in cols]
                availabilities.append(row_data)

        return availabilities

    def print_table(self, data):
        """Pretty print table to console."""
        if data:
            for row in data:
                print(" | ".join(row))
        else:
            print("No data to print.")

    def has_updated(self, previous_data, current_data):
        """Compare previous vs current data."""
        return previous_data != current_data

    def save_to_file(self, data, filename='apartment_data.txt'):
        """Save data to timestamped file."""
        script_directory = os.path.dirname(os.path.realpath(__file__))
        save_directory = os.path.join(script_directory, 'data')
        os.makedirs(save_directory, exist_ok=True)

        file_path = os.path.join(save_directory, filename)

        with open(file_path, 'a') as file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"Timestamp: {timestamp}\n")
            for row in data:
                file.write(" | ".join(row) + "\n")
            file.write("\n")

if __name__ == '__main__':
    # Using QLIC URL
    scraper = ApartmentScraper('https://qlic.com/availabilities/')
    previous_data = None

    while True:
        try:
            print("Checking for updates...")
            print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            data = scraper.fetch_data()

            if previous_data is None:
                print("First check - displaying table data:")
                scraper.print_table(data)
                scraper.save_to_file(data)

            elif scraper.has_updated(previous_data, data):
                print("Data has been updated!")
                ping_me("Apartment availability updated!")
                scraper.print_table(data)
                scraper.save_to_file(data)
            else:
                print("No updates found.")

            previous_data = data

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

        sleep_time = random.randint(120, 300)  # 2 to 5 minutes
        print(f"Waiting {sleep_time} seconds before the next check...\n")
        time.sleep(sleep_time)
