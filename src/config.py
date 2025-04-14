"""Configuration settings for the EnergyPlus weather scraper.

Stores constants used throughout the application, such as base URLs, API keys (if any),
request delays, retry settings, output filenames, and data source priorities.
"""

BASE_URL = "https://energyplus.net/weather"
OUTPUT_CSV_FILENAME = "weather_file_locations.csv"
REQUEST_DELAY = 0.5  # seconds
MAX_RETRIES = 3
SOURCE_PRIORITY = {
    "TMY3": 10,
    "CWEC": 9,
    "CSWD": 8,
    "IWEC": 7,
    "SWERA": 6,
    "TMY2": 5,
    "TMY": 4,
    "CTZRV2": 3,
}
