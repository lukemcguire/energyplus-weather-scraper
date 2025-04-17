from unittest.mock import MagicMock, patch

import pytest
import requests

from src.scraper import _extract_url_from_anchor, _fetch_epw_header, _fetch_geojson, _get_epw_file_urls

TEST_URL = "https://fake.epw/url"

invalid_json_scenarios = [
    pytest.param({"type": "FeatureCollection", "metadata": "some info"}, id="missing_features_key"),
    pytest.param({"type": "FeatureCollection", "features": "I should be a list!"}, id="features_not_list"),
    pytest.param([{"id": 1}, {"id": 2}], id="toplevel_not_dict"),  # JSON is a list
]

invalid_anchor_tags = [
    pytest.param(None, id="none_as_argument"),
    pytest.param("", id="empty_string"),
    pytest.param("<a>bad anchor</a>", id="no_href"),
    pytest.param("<p>some lovely text here</a>", id="no_anchor_tag"),
]


@patch("src.scraper.requests.get")
def test_fetch_geojson_success(mock_get, sample_geojson_data: dict):
    """Test successful retrieval of GeoJSON data."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = sample_geojson_data
    mock_get.return_value = mock_response

    actual = _fetch_geojson(TEST_URL)
    expected = sample_geojson_data.get("features", [])

    mock_get.assert_called_once_with(TEST_URL, timeout=15)
    assert actual == expected


@pytest.mark.parametrize("json_return", invalid_json_scenarios)
@patch("src.scraper.requests.get")
def test_fetch_geojson_failure(mock_get, json_return):
    """Tests various failure conditions."""
    # JSON missing features key
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = json_return
    mock_get.return_value = mock_response

    actual = _fetch_geojson(TEST_URL)

    mock_get.assert_called_once_with(TEST_URL, timeout=15)
    assert actual == []


@patch("src.scraper.requests.get")
def test_fetch_geojson_requests_failure(mock_get):
    """Test failure for non 200 status code."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.url = "https://fake.epw/not_found"
    http_error_instance = requests.exceptions.HTTPError(
        "404 Client Error: Not Found for url: https://fake.epw/not_found"
    )
    mock_response.raise_for_status.side_effect = http_error_instance
    mock_get.return_value = mock_response

    bad_url = "https://fake.epw/not_found"
    actual = _fetch_geojson(bad_url)

    mock_get.assert_called_once_with(bad_url, timeout=15)
    mock_response.raise_for_status.assert_called_once()
    assert actual == []


def test_extract_url_from_anchor_success():
    """Test successful url extraction."""
    anchor = "<a href=https://energyplus-weather.s3.amazonaws.com/africa_wmo_region_1/DZA/DZA_Algiers.603900_IWEC/DZA_Algiers.603900_IWEC.epw>Download Weather File</a>"
    expected = "https://energyplus-weather.s3.amazonaws.com/africa_wmo_region_1/DZA/DZA_Algiers.603900_IWEC/DZA_Algiers.603900_IWEC.epw"
    actual = _extract_url_from_anchor(anchor)
    assert actual == expected


@pytest.mark.parametrize("html_snippet", invalid_anchor_tags)
def test_extract_url_from_anchor_failure(html_snippet):
    """Tests various failure conditions."""
    anchor = html_snippet
    actual = _extract_url_from_anchor(anchor)
    assert actual is None


def test_get_epw_file_urls(sample_geojson_data: dict):
    locations = sample_geojson_data.get("features", [])
    expected = [
        "https://energyplus-weather.s3.amazonaws.com/africa_wmo_region_1/DZA/DZA_Algiers.603900_IWEC/DZA_Algiers.603900_IWEC.epw",
        "https://energyplus-weather.s3.amazonaws.com/africa_wmo_region_1/EGY/EGY_Al.Minya.623870_ETMY/EGY_Al.Minya.623870_ETMY.epw",
    ]
    actual = _get_epw_file_urls(locations)
    assert actual == expected


@patch("src.scraper.requests.get")  # Mock requests.get within scraper module
def test_fetch_epw_header_handles_partial(mock_get, sample_epw_header_bytes: bytes):
    # Configure the mock response
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 206
    mock_response.url = TEST_URL
    mock_response.content = sample_epw_header_bytes
    mock_get.return_value = mock_response

    # Call the function under test
    actual_bytes = _fetch_epw_header(TEST_URL)

    # Assertions
    mock_get.assert_called_once_with(TEST_URL, headers={"Range": "bytes=0-512"}, timeout=15, stream=True)
    assert mock_get.return_value.status_code == 206
    assert actual_bytes is not None
    assert actual_bytes == sample_epw_header_bytes


@patch("src.scraper.requests.get")
def test_fetch_epw_header_network_error(mock_get):
    """Test _fetch_epw_header returns None on requests.exceptions.RequestException."""
    # Configure mock_get to raise a network-related exception
    network_error = requests.exceptions.Timeout("Connection timed out")
    mock_get.side_effect = network_error

    actual = _fetch_epw_header(TEST_URL)

    mock_get.assert_called_once_with(TEST_URL, headers={"Range": "bytes=0-512"}, timeout=15, stream=True)
    assert actual is None


@patch("src.scraper.requests.get")
def test_fetch_epw_header_http_error(mock_get):
    """Test _fetch_epw_header returns None on HTTPError (e.g., 404)."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.url = TEST_URL
    # Configure raise_for_status to raise HTTPError
    http_error = requests.exceptions.HTTPError(f"404 Client Error: Not Found for url: {TEST_URL}")
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    actual = _fetch_epw_header(TEST_URL)

    mock_get.assert_called_once_with(TEST_URL, headers={"Range": "bytes=0-512"}, timeout=15, stream=True)
    mock_response.raise_for_status.assert_called_once()
    assert actual is None


@patch("src.scraper.requests.get")
def test_fetch_epw_header_unexpected_error(mock_get):
    """Test _fetch_epw_header returns None on unexpected exceptions."""
    # Configure mock_get to raise a generic exception
    unexpected_error = ValueError("Something unexpected happened")
    mock_get.side_effect = unexpected_error

    actual = _fetch_epw_header(TEST_URL)

    mock_get.assert_called_once_with(TEST_URL, headers={"Range": "bytes=0-512"}, timeout=15, stream=True)
    assert actual is None
