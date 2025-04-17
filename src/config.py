"""Configuration settings for the EnergyPlus weather scraper.

Stores constants used throughout the application, such as base URLs, API keys (if any),
request delays, retry settings, output filenames, and data source priorities.
"""

GEOJSON_URL = "https://energyplus.net/assets/weather/master.geojson"
OUTPUT_CSV_FILENAME = "weather_file_locations.csv"
MIN_DELAY = 2
MAX_DELAY = 5
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
FIELD_NAMES = [
    "location",
    "region",
    "country",
    "weather_source",
    "wmo_index",
    "latitude",
    "longitude",
    "tz_offset",
    "elevation",
]
