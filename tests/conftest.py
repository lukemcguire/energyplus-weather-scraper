# tests/conftest.py
import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_epw_header_bytes() -> bytes:
    """Provides the raw byte content of a sample EPW file header.

    Returns:
        A string of bytes to be used as a test fixture.
    """
    header_file = FIXTURES_DIR / "sample_epw_header_tmy3.bin"
    try:
        # Read the file content as bytes
        return header_file.read_bytes()
    except FileNotFoundError:
        pytest.fail(f"Fixture file not found: {header_file}")
    except Exception as e:
        pytest.fail(f"Error reading fixture file {header_file}: {e}")


# You could add more fixtures for different header examples if needed


@pytest.fixture
def sample_geojson_data() -> dict:
    """Provides parsed Python object from the sample_master.geojson fixture file.

    Returns:
        A dictionary to be used as a test fixture.
    """
    json_file = FIXTURES_DIR / "sample_master.geojson"
    try:
        with json_file.open("r", encoding="utf-8") as f:
            # Parse the JSON file content into a Python object
            data = json.load(f)
    except FileNotFoundError:
        pytest.fail(f"Fixture file not found: {json_file}")
    except json.JSONDecodeError as e:
        pytest.fail(f"Error decoding JSON fixture file {json_file}: {e}")
    except Exception as e:
        pytest.fail(f"Error reading fixture file {json_file}: {e}")
    else:
        return data
