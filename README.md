# Apartment Web Scraper

A web scraper for monitoring apartment availability.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/vincentren1/apt_web_scraper.git
cd apt_web_scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python apartment_scraper.py
```

The script will:
- Check for apartment availability updates
- Save current data to `data/apartment_data.txt`
- Log any changes to `data/change_log.txt`
- Notify you if there are any changes

## Features

- One-time check of apartment availability
- Compares against previous data
- Logs changes with timestamps
- Ignores timestamps in data comparison
- Clean output format

## Data Files

- `data/apartment_data.txt`: Current apartment data
- `data/change_log.txt`: History of changes with timestamps

## Note

The script runs once and compares against previously saved data. It will notify you if there are any changes in the apartment availability.
