#!/usr/bin/env python
"""
Spotify API Explorer - Exploratory data queries using Spotify's API.

This script demonstrates various ways to query and explore data available
through Spotify's API using the credentials and tools from src/.

Examples:
    python scripts/explore.py --user-playlists
    python scripts/explore.py --playlist-details <playlist_id>
    python scripts/explore.py --search "artist_name"
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def init_spotify_client():
    """Initialize and return Spotify API client."""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        logger.error("Spotify credentials not found in .env file")
        logger.error("Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in .env")
        sys.exit(1)
    
    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    sp = Spotify(auth_manager=auth_manager)
    logger.info("✓ Spotify API client initialized")
    return sp


def explore_user_playlists(sp):
    """
    Get current user's playlists with their names, track counts, and first 5 tracks.
    
    Note: This requires User authentication (OAuth), not just Client Credentials.
    For now, use 'search' command to find playlists, or 'playlist-details' with a playlist ID.
    
    Args:
        sp: Spotify client instance
    """
    print("\n" + "=" * 80)
    print("YOUR PLAYLISTS - USER AUTHENTICATION REQUIRED")
    print("=" * 80 + "\n")
    
    logger.info("⚠️  Note: Getting your personal playlists requires User Authentication (OAuth)")
    logger.info("Available alternatives:")
    logger.info("  - python scripts/explore.py search 'your playlist name' --type playlist")
    logger.info("  - python scripts/explore.py playlist-details <playlist_id>")
    
    print("\n❌ This feature requires Spotify user authentication (OAuth).")
    print("To enable it, you would need to:")
    print("  1. Set up OAuth callback in your Spotify app settings")
    print("  2. Implement authorization code flow in this script")
    print("\nAlternatively, you can:")
    print("  • Search for playlists: python scripts/explore.py search 'playlist name' --type playlist")
    print("  • Get playlist details: python scripts/explore.py playlist-details <playlist_id>")
    print(f"\n{'=' * 80}\n")


def explore_playlist_details(sp, playlist_id):
    """
    Get detailed information about a specific playlist.
    
    Args:
        sp: Spotify client instance
        playlist_id: Spotify playlist ID
    """
    print("\n" + "=" * 80)
    print(f"PLAYLIST DETAILS: {playlist_id}")
    print("=" * 80 + "\n")
    
    try:
        playlist = sp.playlist(playlist_id)
        
        print(f"Name: {playlist['name']}")
        print(f"Owner: {playlist['owner']['display_name']}")
        print(f"Description: {playlist['description'] or '(No description)'}")
        print(f"Total Tracks: {playlist['tracks']['total']}")
        print(f"Public: {playlist['public']}")
        print(f"Collaborative: {playlist['collaborative']}")
        print(f"URL: {playlist['external_urls']['spotify']}")
        
        print(f"\nFirst 10 tracks:")
        tracks_response = sp.playlist_tracks(playlist_id, limit=10)
        tracks = tracks_response['items']
        
        for idx, track_item in enumerate(tracks, 1):
            track = track_item['track']
            if track is None:
                print(f"  {idx}. [Deleted track]")
                continue
            
            track_name = track['name']
            artists = ", ".join([artist['name'] for artist in track['artists']])
            print(f"  {idx}. {track_name} - {artists}")
        
        if playlist['tracks']['total'] > 10:
            print(f"  ... and {playlist['tracks']['total'] - 10} more")
            
    except Exception as e:
        logger.error(f"Failed to fetch playlist details: {e}")
        sys.exit(1)


def search_spotify(sp, query, search_type="track"):
    """
    Search Spotify for tracks, artists, or playlists.
    
    Args:
        sp: Spotify client instance
        query: Search query string
        search_type: Type of search - "track", "artist", or "playlist"
    """
    print("\n" + "=" * 80)
    print(f"SEARCH RESULTS: {query} ({search_type.upper()}S)")
    print("=" * 80 + "\n")
    
    try:
        results = sp.search(q=query, type=search_type, limit=10)
        
        if search_type == "track":
            items = results['tracks']['items']
            for idx, track in enumerate(items, 1):
                artists = ", ".join([artist['name'] for artist in track['artists']])
                print(f"{idx}. {track['name']} - {artists}")
                print(f"   Album: {track['album']['name']}")
                print(f"   URL: {track['external_urls']['spotify']}\n")
                
        elif search_type == "artist":
            items = results['artists']['items']
            for idx, artist in enumerate(items, 1):
                genres = ", ".join(artist['genres'][:3]) if artist['genres'] else "Unknown"
                print(f"{idx}. {artist['name']}")
                print(f"   Genres: {genres}")
                print(f"   Followers: {artist['followers']['total']:,}")
                print(f"   URL: {artist['external_urls']['spotify']}\n")
                
        elif search_type == "playlist":
            items = results['playlists']['items']
            for idx, playlist in enumerate(items, 1):
                print(f"{idx}. {playlist['name']}")
                print(f"   Owner: {playlist['owner']['display_name']}")
                print(f"   Tracks: {playlist['tracks']['total']}")
                print(f"   URL: {playlist['external_urls']['spotify']}\n")
        
        if not items:
            print(f"No results found for '{query}'")
            
    except Exception as e:
        logger.error(f"Search failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Spotify API Explorer - Explore your Spotify data"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # User playlists command
    subparsers.add_parser(
        "user-playlists",
        help="List your playlists with their first 5 tracks"
    )
    
    # Playlist details command
    playlist_parser = subparsers.add_parser(
        "playlist-details",
        help="Get details about a specific playlist"
    )
    playlist_parser.add_argument(
        "playlist_id",
        help="Spotify playlist ID"
    )
    
    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search Spotify for tracks, artists, or playlists"
    )
    search_parser.add_argument(
        "query",
        help="Search query"
    )
    search_parser.add_argument(
        "--type",
        choices=["track", "artist", "playlist"],
        default="track",
        help="Type of search (default: track)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Initialize Spotify client
    sp = init_spotify_client()
    
    # Execute commands
    if args.command == "user-playlists":
        explore_user_playlists(sp)
        
    elif args.command == "playlist-details":
        explore_playlist_details(sp, args.playlist_id)
        
    elif args.command == "search":
        search_spotify(sp, args.query, args.type)


if __name__ == "__main__":
    main()
