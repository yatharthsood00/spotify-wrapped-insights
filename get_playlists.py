import csv
from spotipy import Spotify

def get_full_tracklist(sp: Spotify, playlists: dict) -> list:
    '''
    Get full tracklist from all playlists, by year
    '''

    MASTER_LIST = []
    for YEAR, playlist_id in playlists.items():
        try:
            cur_playlist = sp.playlist(playlist_id)
            print("loaded playlist", YEAR)
        except Exception as e:
            print(f"{e}\n Unable to load playlist for the year {YEAR}. Check if the playlist is public. (ID: {playlist_id})")

        # print(f"year {YEAR}")

        CURRENT_PLAYLIST_TRACKS = cur_playlist['tracks']['items']
        for RANK, CURRENT_TRACK_LISTING in enumerate(CURRENT_PLAYLIST_TRACKS):
            CURRENT_RANK = RANK+1
            CURRENT_TRACK = CURRENT_TRACK_LISTING['track']

            CURRENT_TRACK_NAME = CURRENT_TRACK['name']
            # CURRENT_TRACK_ARTISTS = ', '.join([i['name'] for i in CURRENT_TRACK['artists']])
            CURRENT_TRACK_ARTISTS =  [artist['name'] for artist in CURRENT_TRACK['artists']]
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
    
    return MASTER_LIST

def save_tracklist_to_csv(MASTER_LIST: list, filename: str) -> None:

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['year', 'index', 'name', 'artists', 'id', 'link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(MASTER_LIST)

