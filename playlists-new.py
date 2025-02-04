# TODO: using the better maintained spotipy library for the same - getting all songs from all playlists

import spotipy
import os
import csv
from spotipy.oauth2 import SpotifyClientCredentials
import pprint

from dotenv import load_dotenv

load_dotenv()

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

playlists = {}

for key, value in os.environ.items():
    if key.startswith("pl_"):
        year_key = key[3:]
        playlists[year_key] = value

# print(playlists)

# sp becomes our spotify object with the auth to do stuff further
# Now we just get the playlist IDs and process them into our CSV list

MASTER_LIST = []
for YEAR, playlist_id in playlists.items():
    try:
        cur_playlist = sp.playlist(playlist_id)
        print("loaded playlist", YEAR)
    except:
        print(f"Unable to load playlist for the year {YEAR}. Check if the playlist is public. (ID: {playlist_id})")

    # print(f"year {YEAR}")

    CURRENT_PLAYLIST_TRACKS = cur_playlist['tracks']['items']
    for RANK, CURRENT_TRACK_LISTING in enumerate(CURRENT_PLAYLIST_TRACKS):
        CURRENT_RANK = RANK+1
        CURRENT_TRACK = CURRENT_TRACK_LISTING['track']

        CURRENT_TRACK_NAME = CURRENT_TRACK['name']
        CURRENT_TRACK_ARTISTS = ', '.join([i['name'] for i in CURRENT_TRACK['artists']])
        CURRENT_TRACK_ID = CURRENT_TRACK['id']
        CURRENT_TRACK_URL = CURRENT_TRACK['external_urls']['spotify']
        
        CURRENT_ELEMENT = {
            'year' : YEAR,
            'index' : CURRENT_RANK,
            'name' : CURRENT_TRACK_NAME,
            'artists' : CURRENT_TRACK_ARTISTS,
            'id' : CURRENT_TRACK_ID,
            'link' : CURRENT_TRACK_URL
        }

        MASTER_LIST.append(CURRENT_ELEMENT)
        # print(f"{YEAR} - {CURRENT_RANK} - {CURRENT_TRACK_ID} - {CURRENT_TRACK_NAME} - {CURRENT_TRACK_ARTISTS} - {CURRENT_TRACK_URL}")
    print(f"{YEAR} - {len(CURRENT_PLAYLIST_TRACKS)} tracks found in list")
print(f"Total Tracks found - {len(MASTER_LIST)}")


file_path = 'list.csv'
with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['year', 'index', 'name', 'artists', 'id', 'link']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(MASTER_LIST)
