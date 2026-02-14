#!/usr/bin/env python
"""
Spotify Wrapped Insights - Main Orchestrator

Orchestrates the complete data pipeline: fetching and processing Spotify Wrapped playlists.

The script intelligently picks up where it left off:
- If list.csv exists, skips fetching
- If working.csv exists, skips processing
- Run with appropriate flags based on your needs

Usage:
    python scripts/main.py --process  # Get working.csv (fetches if needed, ready for Kaggle)
    python scripts/main.py --fetch    # Just fetch raw data (list.csv only)
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    PLAYLIST_IDS,
    RAW_DATA_PATH,
    PROCESSED_DATA_PATH,
)
from src.spotify_fetcher import SpotifyWrappedFetcher
from src.data_processor import DataProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_playlists(client_id: str, client_secret: str, playlist_ids: dict, force: bool = False) -> bool:
    """
    Fetch Wrapped playlists from Spotify API and save to CSV.
    
    Args:
        client_id: Spotify API client ID
        client_secret: Spotify API client secret
        playlist_ids: Dictionary of year -> playlist ID
        force: If True, re-fetch even if list.csv exists
        
    Returns:
        True if fetch succeeded or was skipped (file already exists)
    """
    if RAW_DATA_PATH.exists() and not force:
        logger.info(f"✓ Raw data already exists at {RAW_DATA_PATH} (use --fetch --force to re-fetch)")
        return True

    if not client_id or not client_secret:
        logger.error("Spotify credentials not found in environment variables")
        logger.error("Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env")
        return False

    if not playlist_ids:
        logger.error("No playlist IDs found in environment")
        logger.error("Define environment variables in format: pl_2018=<id>, pl_2019=<id>, etc.")
        return False

    try:
        fetcher = SpotifyWrappedFetcher(client_id, client_secret)
        logger.info(f"Fetching playlists for years: {sorted(playlist_ids.keys())}")

        tracks = fetcher.get_full_tracklist(playlist_ids)
        fetcher.save_tracklist_to_csv(tracks, str(RAW_DATA_PATH))

        logger.info(f"✓ Raw data saved to {RAW_DATA_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to fetch playlists: {e}")
        return False


def process_data(force: bool = False) -> bool:
    """
    Process raw CSV to analysis-ready format.
    
    Args:
        force: If True, re-process even if working.csv exists
        
    Returns:
        True if process succeeded or was skipped (file already exists)
    """
    if PROCESSED_DATA_PATH.exists() and not force:
        logger.info(f"✓ Processed data already exists at {PROCESSED_DATA_PATH} (use --process --force to re-process)")
        return True

    if not RAW_DATA_PATH.exists():
        logger.error(f"Raw data file not found at {RAW_DATA_PATH}")
        logger.error("Run --fetch first to fetch playlist data")
        return False

    try:
        processor = DataProcessor()
        logger.info("Loading raw data...")
        raw_df = processor.load_raw_data(str(RAW_DATA_PATH))

        logger.info("Processing data...")
        processed_df = processor.preprocess(raw_df)

        processor.save_processed_data(processed_df, str(PROCESSED_DATA_PATH))
        logger.info(f"✓ Processed data saved to {PROCESSED_DATA_PATH}")
        logger.info("✓ Data is ready for Kaggle notebook analysis!")
        return True
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Spotify Wrapped Insights - Fetch and process playlist data"
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch playlists from Spotify API (creates list.csv)",
    )
    parser.add_argument(
        "--process",
        action="store_true",
        help="Process data for analysis (creates working.csv). Auto-fetches if needed.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-fetch or re-process even if files already exist",
    )

    args = parser.parse_args()

    # If no arguments, show help
    if not any([args.fetch, args.process]):
        parser.print_help()
        sys.exit(0)

    # Handle --process (prioritize): fetch + process pipeline
    if args.process:
        logger.info("Processing data for analysis...")
        success = fetch_playlists(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, PLAYLIST_IDS, force=args.force)
        if success:
            success = process_data(force=args.force)
        
        if not success:
            sys.exit(1)

    # Handle --fetch only: just get raw data
    elif args.fetch:
        logger.info("Fetching playlist data...")
        success = fetch_playlists(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, PLAYLIST_IDS, force=args.force)
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
