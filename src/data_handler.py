"""Manages the storage and prioritization of scraped weather location data.

This module contains the logic for maintaining the collection of unique weather
locations, keyed by WMO index, and ensuring that only the entry with the highest
priority source type is kept when duplicates are encountered.
"""


def add_location(new_location: dict[str, str], locations: dict[str, dict], priority: dict[str, int]) -> None:
    """Add location to existing locations dictionary."""
    ...
