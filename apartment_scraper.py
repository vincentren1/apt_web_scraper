import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import random
from notify import ping_me
import json

class ApartmentScraper:
    def __init__(self, url):
        """Initialize scraper with target URL."""
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_data(self):
        """Fetch apartment data from the URL."""
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        data = self.parse_table(soup)
        # Add a test change to force detection
        data[2][1] = "Starting from $3,759"  # Change the price slightly
        return data

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
        """Compare only the table data (ignoring timestamps and headers)."""
        # Get only the table data rows (skip headers and timestamps)
        previous_data_clean = []
        current_data_clean = []
        
        # Process previous data
        for row in previous_data:
            if not row:
                continue
            # Skip timestamp row (any cell containing timestamp)
            if any('timestamp' in cell.lower() for cell in row):
                continue
            # Skip header row (check for common header patterns)
            if 'type' in row[0].lower() and 'price' in row[1].lower():
                continue
            # Skip empty rows
            if not any(cell.strip() for cell in row):
                continue
            previous_data_clean.append(row)
        
        # Process current data
        for row in current_data:
            if not row:
                continue
            # Skip timestamp row (any cell containing timestamp)
            if any('timestamp' in cell.lower() for cell in row):
                continue
            # Skip header row (check for common header patterns)
            if 'type' in row[0].lower() and 'price' in row[1].lower():
                continue
            # Skip empty rows
            if not any(cell.strip() for cell in row):
                continue
            current_data_clean.append(row)
        
        # Normalize the data
        def normalize_row(row):
            # Convert to string and handle special characters
            normalized = []
            for cell in row:
                try:
                    # Convert to string and normalize
                    cell = str(cell)
                    # Remove whitespace and special characters
                    cell = ''.join(c for c in cell if c.isalnum() or c.isspace())
                    # Convert to lowercase
                    cell = cell.lower()
                    # Remove multiple spaces
                    cell = ' '.join(cell.split())
                    normalized.append(cell)
                except:
                    normalized.append('')
            # Remove any empty cells
            normalized = [cell for cell in normalized if cell]
            return normalized
        
        # Normalize both datasets
        previous_data_normalized = [normalize_row(row) for row in previous_data_clean]
        current_data_normalized = [normalize_row(row) for row in current_data_clean]
        
        # Sort both datasets for reliable comparison
        previous_data_normalized.sort()
        current_data_normalized.sort()
        
        # Compare the normalized data
        return previous_data_normalized != current_data_normalized

    def save_to_file(self, data, filename='apartment_data.txt'):
        """Save data to text file."""
        # Get the absolute path to the repository root
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        save_directory = os.path.join(repo_root, 'data')
        os.makedirs(save_directory, exist_ok=True)

        file_path = os.path.join(save_directory, filename)

        # Save in text format
        with open(file_path, 'w') as file:
            # Save headers first
            headers = data[0]
            file.write(" | ".join(headers) + "\n")
            
            # Save data rows
            for row in data[1:]:  # Skip headers
                if any(cell.strip() for cell in row):  # Only write rows that have data
                    file.write(" | ".join(row) + "\n")
            
            # Add timestamp at the end
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"\nTimestamp: {timestamp}\n")

if __name__ == '__main__':
    # Using QLIC URL
    scraper = ApartmentScraper('https://qlic.com/availabilities/')
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Checking for updates at {timestamp}")

        # Try to load previous data if it exists
        previous_data = None
        try:
            # Get the absolute path to the repository root
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(repo_root, 'data', 'apartment_data.txt')
            with open(file_path, 'r') as file:
                lines = file.readlines()
                # Skip the timestamp line at the end
                previous_data = [line.strip().split(' | ') for line in lines[:-2] if line.strip()]
                # Add back the headers
                if previous_data:
                    previous_data.insert(0, previous_data[0])
        except FileNotFoundError:
            print("No previous data found.")

        # Fetch current data and save it
        current_data = scraper.fetch_data()
        scraper.print_table(current_data)
        scraper.save_to_file(current_data)
        
        # Save changes to git
        try:
            import subprocess
            
            # Configure git if not already configured
            subprocess.run(['git', 'config', '--global', 'user.name', 'github-actions[bot]'], check=True)
            subprocess.run(['git', 'config', '--global', 'user.email', 'github-actions[bot]@users.noreply.github.com'], check=True)
            
            # Add and commit changes
            subprocess.run(['git', 'add', 'data/'], check=True)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            subprocess.run(['git', 'commit', '-m', f'Update apartment data at {timestamp}'], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print("\nData files updated and pushed to git!")
        except subprocess.CalledProcessError as e:
            print(f"\nWarning: Failed to push changes to git: {e}")
            
        # Check for changes
        if previous_data is None:
            print("\nThis is the first run. No previous data to compare against.")
        elif scraper.has_updated(previous_data, current_data):
            # Save changes to log
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_path = os.path.join(repo_root, 'data', 'change_log.txt')
            with open(log_path, 'a') as log_file:
                log_file.write(f"\n=== Changes detected at {timestamp} ===\n")
                for row in current_data:
                    if any(cell.strip() for cell in row):
                        log_file.write(" | ".join(row) + "\n")
            
            # Commit and push changes to git
            try:
                import subprocess
                subprocess.run(['git', 'add', '-f', 'data/apartment_data.txt', 'data/change_log.txt'], check=True)
                subprocess.run(['git', 'commit', '-m', f'Update apartment data at {timestamp}'], check=True)
                subprocess.run(['git', 'push', 'origin', 'main'], check=True)
                print("\nData has been updated and changes pushed to git!")
            except subprocess.CalledProcessError as e:
                print(f"\nWarning: Failed to push changes to git: {e}")
            ping_me("Apartment availability updated!")
        else:
            print("\nNo changes detected from previous data.")
        
        print("\nScraping completed successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        print("\nScraping failed.")
