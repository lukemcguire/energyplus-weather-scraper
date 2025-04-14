import pytest

from src.parser import parse_epw_location_line


def test_parse_valid_epw_line():
    """Test that a valid location line is parsed correctly."""
    line = "LOCATION,Paso Robles Municipal Arpt,CA,USA,TMY3,723965,35.67,-120.63,-8.0,244.0"
    expected = {
        "location": "Paso Robles Municipal Arpt",
        "region": "CA",
        "country": "USA",
        "weather_source": "TMY3",
        "wmo_index": "723965",
        "latitude": "35.67",
        "longitude": "-120.63",
        "tz_offset": "-8.0",
        "elevation": "244.0",
    }
    actual = parse_epw_location_line(line)
    assert actual == expected


def test_parse_location_title_case():
    """Test that the location is formatted in title case."""
    line = "LOCATION,GENEVA,-,CHE,IWEC Data,067000,46.25,6.13,1.0,416.0"
    expected = "Geneva"
    parsed = parse_epw_location_line(line)
    assert parsed["location"] == expected

    line = "LOCATION,PASO rObLeS municipal ARPt,CA,USA,TMY3,723965,35.67,-120.63,-8.0,244.0"
    expected = "Paso Robles Municipal Arpt"
    parsed = parse_epw_location_line(line)
    assert parsed["location"] == expected


def test_parse_no_region():
    """Test that locations without region are correctly set to None."""
    line = "LOCATION,GENEVA,-,CHE,IWEC Data,067000,46.25,6.13,1.0,416.0"
    expected = ""
    parsed = parse_epw_location_line(line)
    assert parsed["region"] == expected


def test_parse_line_missing_location_prefix_raises_error():
    """Test that a line not starting with 'LOCATION,' raises ValueError."""
    bad_line = "NOLOCATION,Paso Robles Municipal Arpt,CA,USA,TMY3,723965,35.67,-120.63,-8.0,244.0"
    # We expect a ValueError (or maybe a custom exception)
    with pytest.raises(ValueError):
        parse_epw_location_line(bad_line)


def test_parse_line_incorrect_field_count_raises_error():
    """Test that lines with too few or too many fields raise ValueError."""
    # Too few fields (should be 10 fields total, 9 after 'LOCATION,')
    bad_line_too_few = "LOCATION,Paso Robles Municipal Arpt,CA,USA,TMY3,723965,35.67,-120.63,-8.0"
    with pytest.raises(ValueError):
        parse_epw_location_line(bad_line_too_few)

    # Too many fields
    bad_line_too_many = "LOCATION,Paso Robles Municipal Arpt,CA,USA,TMY3,723965,35.67,-120.63,-8.0,244.0,EXTRA_FIELD"
    with pytest.raises(ValueError):
        parse_epw_location_line(bad_line_too_many)
