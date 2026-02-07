import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from dotenv import load_dotenv

from get_playlists import get_full_tracklist, save_tracklist_to_csv
from data_prep import df_preprocessing
from data_functions import most_popular_artists, one_year_dream_run



def main():

    load_dotenv()
    pd.set_option('mode.chained_assignment', None)

    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    playlists = {}

    for key, value in os.environ.items():
        # TODO: change it to take params from call later + move it to its own function
        if key.startswith("pl_"):
            year_key = key[3:]
            playlists[year_key] = value

    MASTER_LIST = get_full_tracklist(sp, playlists)

    file_path = 'list.csv'
    save_tracklist_to_csv(MASTER_LIST, file_path)
    COLUMN_LIST = ['year', 'index', 'name', 'artists', 'id', 'link']
    MAIN_DF = pd.DataFrame(MASTER_LIST, columns=COLUMN_LIST)

    YEARS = MAIN_DF['year'].unique().tolist() # final value, used quite often in the data analysis section

    # preprocess the dataframe to make it workable for the actual data
    WORKING_DF = df_preprocessing(MAIN_DF, YEARS)

    # print(WORKING_DF.head())
    WORKING_DF.to_csv('working.csv')
    
    most_popular_artists(WORKING_DF)

    one_year_dream_run(WORKING_DF, YEARS)



main()