"""
Configuration and constants for Spotify Wrapped Insights.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_CSV_NAME = "list.csv"
PROCESSED_CSV_NAME = "working.csv"

# Paths
RAW_DATA_PATH = DATA_DIR / RAW_CSV_NAME
PROCESSED_DATA_PATH = DATA_DIR / PROCESSED_CSV_NAME

# CSV field names
RAW_CSV_FIELDS = ["year", "index", "name", "artists", "id", "link"]
PROCESSED_CSV_FIELDS = ["name", "artists", "song_id", "id", "list_appearances"]

# API configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "")

# Load playlist IDs from environment (format: pl_{year}=<playlist_id>)
# Example: pl_2018=<id>, pl_2019=<id>, etc.
PLAYLIST_IDS = {
    int(key.split("_")[1]): value
    for key, value in os.environ.items()
    if key.startswith("pl_")
}

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Analysis configuration
ANALYSIS_CONFIG = {
    "dream_run_threshold": 10,  # Top N tracks considered for dream runs
    "min_appearances": 2,  # Minimum appearances for "on the up" analysis
}
