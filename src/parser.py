"""Functions for parsing HTML content and EnergyPlus weather file (EPW) data.

Provides utilities to extract relevant navigation and file links from HTML pages
retrieved from the weather site, and to parse the specific 'LOCATION' line
from the header of EPW files to extract metadata.
"""


def extract_links(html: str, base_url: str) -> tuple[list[str], list[str]]:  # type: ignore[empty-body]
    """Finds all links on page."""
    ...


def extract_epw_location_line(epw_content: bytes) -> str | None:
    """Fetch the first line of an epw file."""
    ...


def parse_epw_location_line(line: str) -> dict[str, str]:
    """Extracts location metadata from an EPW LOCATION line.

    Parses a comma-separated string conforming to the EPW file format's
    LOCATION line specification, skipping the initial "LOCATION" identifier.

    Args:
        line (str): The LOCATION line string from an EPW file.

    Returns:
        dict[str, str]: A dictionary mapping standard EPW location fields to
            their corresponding string values extracted from the line.

    Raises:
        ValueError: If the epw location line format is unable to be parsed.
    """
    keys = [
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
    # Split the line by commas
    data = line.split(",")
    if data[0] != "LOCATION" or len(keys) != len(data) - 1:
        raise ValueError("unable to parse epw location")
    # Discard the first element ("LOCATION")
    data = data[1:]
    data[0] = data[0].title()
    if len(data[1]) < 2:
        data[1] = ""
    # Create a dictionary by zipping the predefined keys with the extracted data
    return dict(zip(keys, data, strict=False))
