# EnergyPlus Weather Data Scraper

A Python script to scrape weather station metadata from [energyplus.net/weather](https://energyplus.net/weather) and compile it into a CSV file.

### Personal Note

> I had actually intended my personal project to be something quite different from this. However, I realized that I needed
> to get this data as a starting point for the project I had actually intended.  As this turned out to be more complex
> than I was originally expecting, I decided to turn this into its own full-blown project. I also used this project as an
> opportunity to practice a few things that I've been wanting more work on.  Specifically:
> - Testing and Test-Driven Development
> - Logging and error handling
> - Partial file downloads
>
> That said my eventual plan is to use this data to create a CLI which will automatically download the closest weather
> file to the requested location, run a solar PV analysis, and perform energy cost payback analysis and system sizing
> for PV and battery systems.  So... we'll get there.

## Description

This project fetches weather station information provided by EnergyPlus. Instead of crawling the website structure, it efficiently utilizes the `master.geojson` file published on the site, which contains metadata and links for numerous weather locations.

For each location listed in the GeoJSON file, the script:
1.  Extracts the direct URL to the EnergyPlus Weather (`.epw`) file.
2.  Fetches the header (first ~512 bytes) of the `.epw` file using HTTP Range requests (falling back to full download if ranges aren't supported).
3.  Attempts to decode the header bytes, handling potential UTF-8 and ISO-8859-1 encoding issues.
4.  Parses the `LOCATION` line within the header to extract key metadata fields.
5.  Handles potential duplicate entries for the same WMO index by prioritizing based on the weather data source type (e.g., TMY3 > IWEC > TMY2).
6.  Outputs the final, unique list of locations and their associated metadata into a CSV file.

The target metadata fields include:
- Location Name
- Region/State/Province
- Country
- Data Source Type
- WMO Index
- Latitude
- Longitude
- Time Zone Offset
- Elevation
- EPW File URL

## Features

*   Efficiently fetches data source list from `master.geojson`.
*   Uses HTTP Range requests to minimize downloads when fetching EPW headers.
*   Robust decoding with fallbacks for common text encodings.
*   Prioritizes data sources to handle duplicate WMO indices.
*   Polite scraping with configurable random delays between requests.
*   Configurable retry mechanism for fetching EPW headers.
*   Detailed logging for monitoring progress and errors.
*   Outputs data to a clean CSV format.
*   Includes unit tests for key components.

## Requirements

*   Python 3.13+ (or your specific version)
*   [uv](https://github.com/astral-sh/uv) (for environment and dependency management)
*   Git (for cloning the repository)

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [your-repository-url]
    cd [project-directory-name]
    ```

2.  **Create environment and install dependencies:**

    **Using `uv` (Recommended):**
    ```bash
    uv sync
    ```
    *(This command creates a virtual environment and installs dependencies based on `pyproject.toml`)*

    **Using standard `venv` and `pip`:**
    *   Create a virtual environment:
        ```bash
        python -m venv .venv
        ```
        *(You can replace `.venv` with `venv` or another name if you prefer)*
    *   Activate the virtual environment:
        *   **Linux/macOS:** `source .venv/bin/activate`
        *   **Windows (Command Prompt/PowerShell):** `.venv\Scripts\activate`
    *   Install dependencies from `requirements.txt`:
        ```bash
        pip install -r requirements.txt
        ```

## Usage

**Using `uv`:**

Ensure you are in the project's root directory.
```bash
uv run python -m src.main
```

The script will:
*   Fetch the GeoJSON data.
*   Process each EPW file URL found.
*   Log progress and any errors to the console and potentially a log file (check `src/main.py` for logging configuration).
*   Generate the output CSV file upon completion.

**Using standard `venv` and `pip`:**

1.  Ensure you are in the project's root directory.
2.  **Activate the virtual environment** (if not already active):
    *   **Linux/macOS:** `source .venv/bin/activate`
    *   **Windows:** `.venv\Scripts\activate`
3.  Run the main script using Python's `-m` flag:
    ```bash
    python -m src.main
    ```

The script will then execute as described previously (logging, processing, generating CSV). Don't forget to deactivate the environment when done (`deactivate`).


## Project Structure

```
├── output/               # Default directory for output files (CSV)
├── src/                  # Main source code
│   ├── __init__.py
│   ├── config.py         # Configuration variables (URLs, delays, priorities)
│   ├── data_handler.py   # Logic for storing and prioritizing location data
│   ├── main.py           # Main script entry point, logging setup
│   ├── parser.py         # Functions for parsing EPW lines, HTML snippets
│   ├── scraper.py        # Core fetching (GeoJSON, EPW headers) and orchestration logic
│   └── utils.py          # Utility functions (CSV writing, delays)
├── tests/                # Unit tests
│   ├── fixtures/         # Sample data files for tests (e.g., sample EPW header)
│   ├── __init__.py
│   ├── conftest.py       # Pytest fixtures
│   └── test_*.py         # Test files for different modules
├── .gitignore
├── LICENSE               # [Important: Add your chosen license file here]
├── pyproject.toml        # Project metadata and dependencies (for uv/pip)
├── requirements.txt      # Project dependencies (pip)
└── README.md             # This file
```

## Configuration

Key settings can be adjusted in `src/config.py`:

*   `GEOJSON_URL`: The URL for the `master.geojson` file.
*   `OUTPUT_CSV_FILENAME`: Name of the output CSV file.
*   `FIELD_NAMES`: List of column headers for the output CSV.
*   `SOURCE_PRIORITY`: Dictionary mapping weather source types (e.g., "TMY3") to numerical priority scores.
*   `MIN_DELAY`, `MAX_DELAY`: Minimum and maximum delay (in seconds) between HTTP requests.
*   `MAX_RETRIES`: Number of times to retry fetching an EPW header if it fails.

## Output

The script generates a CSV file (default: `output/locations.csv`) containing the scraped metadata. The columns are determined by the `FIELD_NAMES` list in `src/config.py`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
