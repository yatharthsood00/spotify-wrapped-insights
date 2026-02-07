import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from dotenv import load_dotenv


load_dotenv()
pd.set_option('mode.chained_assignment', None)

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

track = sp.track('5W7DOVGQLTigu09afW7QMT')
print(track)

artists = [artist['name'] for artist in track['artists']]
# artists = []
# for artist in track['artists']:
#     artists.append(artist['name'])

# print(artists)

