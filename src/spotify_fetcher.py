"""
Spotify API data fetcher for Wrapped playlists.

This module handles authentication with the Spotify API and fetches
complete track lists from Wrapped playlists for analysis.
"""

import csv
import logging
from typing import Dict, List, Optional

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

logger = logging.getLogger(__name__)


class SpotifyWrappedFetcher:
    """Fetches Spotify Wrapped playlist data from the Spotify API."""

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the Spotify API client.

        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret

        Raises:
            ValueError: If credentials are empty
        """
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials (CLIENT_ID and CLIENT_SECRET) are required")

        auth_manager = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
        self.sp = Spotify(auth_manager=auth_manager)
        logger.info("Spotify API client initialized")

    def get_full_tracklist(self, playlists: Dict[int, str]) -> List[Dict]:
        """
        Fetch complete tracklists from all Wrapped playlists.

        Args:
            playlists: Dictionary mapping year to playlist ID
                      (e.g., {2018: "spotify:playlist:...", ...})

        Returns:
            List of track dictionaries with keys:
            - year: Playlist year
            - index: Track rank (1-based)
            - name: Track name
            - artists: List of artist names
            - id: Spotify track ID
            - link: Spotify track URL

        Example:
            >>> fetcher = SpotifyWrappedFetcher(client_id, client_secret)
            >>> tracks = fetcher.get_full_tracklist({2023: "playlist_id"})
        """
        master_list = []

        for year, playlist_id in sorted(playlists.items()):
            try:
                playlist = self.sp.playlist(playlist_id)
                logger.info("Loaded playlist for %s", year)
            except Exception as e:
                logger.error(
                    "Failed to load playlist for %s (ID: %s). Ensure the playlist is public. Error: %s",
                    year,
                    playlist_id,
                    e
                )
                continue

            playlist_name = playlist["name"]
            tracks = playlist["tracks"]["items"]
            for rank, track_item in enumerate(tracks, start=1):
                track = track_item["track"]
                if track is None:  # Handle deleted tracks
                    logger.warning(f"Skipping deleted track at rank {rank} in {year}")
                    continue

                track_data = {
                    "year": year,
                    "index": rank,
                    "name": track["name"],
                    "artists": [artist["name"] for artist in track["artists"]],
                    "id": track["id"],
                    "link": track["external_urls"]["spotify"],
                }
                master_list.append(track_data)

            logger.info(f"Loading playlist '{playlist_name}' for {year}: {len(tracks)} tracks found")

        logger.info(f"Total tracks fetched: {len(master_list)}")
        return master_list

    @staticmethod
    def save_tracklist_to_csv(master_list: List[Dict], filepath: str) -> None:
        """
        Save fetched tracklist to CSV file.

        Args:
            master_list: List of track dictionaries
            filepath: Path to save CSV file

        Raises:
            IOError: If file cannot be written
        """
        if not master_list:
            logger.warning("Master list is empty; no CSV will be created")
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["year", "index", "name", "artists", "id", "link"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                # Convert artist lists to string representation for CSV
                for row in master_list:
                    row["artists"] = str(row["artists"])
                writer.writerows(master_list)

            logger.info(f"Tracklist saved to {filepath}")
        except IOError as e:
            logger.error(f"Failed to save tracklist to {filepath}: {e}")
            raise
