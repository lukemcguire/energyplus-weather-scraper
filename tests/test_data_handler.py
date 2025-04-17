import pytest

from src.data_handler import _clean_weather_source, add_location

# Define a sample priority map for tests
SAMPLE_PRIORITY = {"TMY3": 10, "TMY2": 9, "IWEC": 8}

# Define sample location data
LOCATION_A_TMY3 = {
    "location": "Location A",
    "region": "CA",
    "country": "USA",
    "weather_source": "TMY3",
    "wmo_index": "12345",
    "epw_url": "url_a_tmy3",
}
LOCATION_A_TMY2 = {
    "location": "Location A",
    "region": "CA",
    "country": "USA",
    "weather_source": "TMY2",
    "wmo_index": "12345",
    "epw_url": "url_a_tmy2",
}
LOCATION_A_IWEC = {
    "location": "Location A",
    "region": "CA",
    "country": "USA",
    "weather_source": "IWEC",
    "wmo_index": "12345",
    "epw_url": "url_a_iwec",
}
LOCATION_B_TMY3 = {
    "location": "Location B",
    "region": "NV",
    "country": "USA",
    "weather_source": "TMY3",
    "wmo_index": "67890",
    "epw_url": "url_b_tmy3",
}
LOCATION_C_UNKNOWN_SOURCE = {
    "location": "Location C",
    "region": "AZ",
    "country": "USA",
    "weather_source": "XYZ",
    "wmo_index": "11223",
    "epw_url": "url_c_xyz",
}


def test_add_location_new_entry():
    """Test adding a location with a WMO index not already present."""
    processed = {}
    add_location(LOCATION_A_TMY3, processed, SAMPLE_PRIORITY)
    assert len(processed) == 1
    assert "12345" in processed
    assert processed["12345"] == LOCATION_A_TMY3


def test_add_location_higher_priority_replaces():
    """Test adding a location that replaces an existing one due to higher priority."""
    processed = {"12345": LOCATION_A_TMY2}  # Start with TMY2
    add_location(LOCATION_A_TMY3, processed, SAMPLE_PRIORITY)  # Add TMY3 (higher)
    assert len(processed) == 1
    assert processed["12345"] == LOCATION_A_TMY3  # Should now be TMY3


def test_add_location_lower_priority_does_not_replace():
    """Test adding a location that does not replace an existing one due to lower priority."""
    processed = {"12345": LOCATION_A_TMY3}  # Start with TMY3
    add_location(LOCATION_A_TMY2, processed, SAMPLE_PRIORITY)  # Add TMY2 (lower)
    assert len(processed) == 1
    assert processed["12345"] == LOCATION_A_TMY3  # Should still be TMY3


def test_add_location_same_priority_does_not_replace():
    """Test adding a location with the same priority does not replace."""
    processed = {"12345": LOCATION_A_TMY3}  # Start with TMY3
    # Create a copy with a different URL but same source/priority
    location_a_tmy3_alt = LOCATION_A_TMY3.copy()
    location_a_tmy3_alt["epw_url"] = "url_a_tmy3_alt"
    add_location(location_a_tmy3_alt, processed, SAMPLE_PRIORITY)
    assert len(processed) == 1
    assert processed["12345"] == LOCATION_A_TMY3  # Should be the original one


def test_add_location_multiple_entries():
    """Test adding multiple distinct locations."""
    processed = {}
    add_location(LOCATION_A_TMY3, processed, SAMPLE_PRIORITY)
    add_location(LOCATION_B_TMY3, processed, SAMPLE_PRIORITY)
    assert len(processed) == 2
    assert "12345" in processed
    assert "67890" in processed
    assert processed["12345"] == LOCATION_A_TMY3
    assert processed["67890"] == LOCATION_B_TMY3


def test_add_location_unknown_source_priority_defaults_to_zero():
    """Test that sources not in the priority map are treated as priority 0."""
    processed = {"11223": LOCATION_C_UNKNOWN_SOURCE}  # Start with unknown source (prio 0)
    # Create a known source with priority > 0
    location_c_iwec = LOCATION_C_UNKNOWN_SOURCE.copy()
    location_c_iwec["weather_source"] = "IWEC"  # Priority 8
    location_c_iwec["epw_url"] = "url_c_iwec"

    add_location(location_c_iwec, processed, SAMPLE_PRIORITY)
    assert len(processed) == 1
    # IWEC (priority 8) should replace XYZ (priority 0)
    assert processed["11223"] == location_c_iwec

    # Now try adding unknown source again, should not replace IWEC
    add_location(LOCATION_C_UNKNOWN_SOURCE, processed, SAMPLE_PRIORITY)
    assert len(processed) == 1
    assert processed["11223"] == location_c_iwec  # Should still be IWEC


MALFORMED_WEATHER_SOURCES = [
    ("TMY2-23232", "TMY2"),
    ("IWEC Data", "IWEC"),
    ("--WYEC2-B-14636", "WYEC2"),
    ("  TMY--40309", "TMY"),
]


@pytest.mark.parametrize("test_input,expected", MALFORMED_WEATHER_SOURCES)
def test_clean_weather_source(test_input, expected):
    actual = _clean_weather_source(test_input)
    assert actual == expected
