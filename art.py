import spotipy
import os
import csv
from spotipy.oauth2 import SpotifyClientCredentials
import pprint

from dotenv import load_dotenv

load_dotenv()

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

album = sp.album('5TF3a1VrbsQ68hUMrdNqeo')

print(album)
