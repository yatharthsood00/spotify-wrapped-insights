# using the spotify library to get playlist tracks exported to csv
# csv is then used in the notebook
from dotenv import load_dotenv

import asyncio
import spotify
import csv
import os

load_dotenv()

# Spotify API credentials (secrets)
CLIENT_ID: str = os.environ.get('CLIENT_ID')
CLIENT_SECRET: str = os.environ.get('SECRET_ID')

client = spotify.HTTPClient(CLIENT_ID, CLIENT_SECRET)

# add to .env the playlist IDs with pl_{year} keys
# this function fetches them all from .env file

# NOTE: Playlists generated for and after 2021's Wrapped cannot be accessed
# by the API directly. You need to create a new playlist with all songs using
# "Add to Other Playlist" from the Spotify Web UI. The order will be preserved across playlists.
def get_playlists(prefix):
    return {key[len(prefix):]: value for key, value in os.environ.items() if key.startswith(prefix)}

prefix = "pl_" # prefix for playlist IDs to be taken from .env
playlist_ids = get_playlists(prefix)

print(playlist_ids)

async def main():
    result_data = []

    try:
        for year, id in playlist_ids.items():
            playlist = await client.get_playlist_tracks(playlist_id=id, limit=100)
            print(f"YEAR: {year}")
            for index, track in enumerate(playlist['items']):
                artists = [artist['name'] for artist in track['track']['artists']]
                item_data = {
                    'year': year,
                    'index': index + 1,  # Adding 1 to start index from 1
                    'name': track['track']['name'],
                    'artists': ', '.join(artists),
                    'id': track['track']['id'],
                    'link': track['track']['external_urls']['spotify']
                }
                result_data.append(item_data)

                print(f"{item_data['index']} - {item_data['name']} : {item_data['link']}")

    finally:
        await client.close()

    return result_data

def save_to_csv(result_data, file_path='list.csv'):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['year', 'index', 'name', 'artists', 'id', 'link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(result_data)

if __name__ == '__main__':
    result = asyncio.get_event_loop().run_until_complete(main())
    filename = 'list.csv'
    save_to_csv(result, filename)
    print("Result saved")

