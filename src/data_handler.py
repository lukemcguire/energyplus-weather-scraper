"""Manages the storage and prioritization of scraped weather location data.

This module contains the logic for maintaining the collection of unique weather
locations, keyed by WMO index, and ensuring that only the entry with the highest
priority source type is kept when duplicates are encountered.
"""

import logging

logger = logging.getLogger(__name__)


def add_location(new_location: dict[str, str], processed_locations: dict[str, dict], priority: dict[str, int]) -> None:
    """Add location to existing locations dictionary.

    Takes a new location dictionary and compares its WMO Index to the existing
    locations dictionary. If the WMO Index is not in the existing locations
    dictionary the new location is added. If the location is existing the new
    location and existing location are comapared based on the type of weather
    file utilized with the precedence determined by the priority dictionary.

    Args:
        new_location: A dictionary representing the new location to be added to
                      the total location dictionary.
        processed_locations: A dictionary of location dictionaries.
        priority: A dictionary with a ranking score based on the type of weather
                  file.
    """
    wmo_index = new_location["wmo_index"]
    location = new_location["location"]

    if wmo_index not in processed_locations:
        processed_locations[wmo_index] = new_location
        logger.debug("%s added to processed locations with WMO Index : %s", location, wmo_index)
        return

    new_weather_source = new_location["weather_source"]
    existing_weather_wource = processed_locations[wmo_index]["weather_source"]

    if priority.get(new_weather_source, 0) > priority.get(existing_weather_wource, 0):
        processed_locations[wmo_index] = new_location
        logger.info(
            "%s replaced in processed locations because %s has higher priority than %s",
            location,
            new_weather_source,
            existing_weather_wource,
        )
    else:
        logger.debug(
            "%s not updated in processed locations because weather file with higher priority already present.", location
        )
