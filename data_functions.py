'''
So this is all the parts that can be asynchronously run
i.e. All function calls made for the functions present here will be made simultaneously
So they can be run all together at once, and we can wait and collect the outputs
Collecting would mean pushing it to the frontend 
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def most_popular_artists(df):
    '''
    Get list of artists with the number of songs they have in the list
    '''

    song_artists = df.explode('artists')['artists'].value_counts()
    grouped_artists = song_artists.groupby(song_artists.values).apply(lambda x: ", ".join(f'"{i}"' for i in x.index))
    op = pd.Series(grouped_artists.index.values, index=grouped_artists.values)
    # print(op)

    print(op[op >= 4])

    # print(sum(song_artists.values()))

def one_year_dream_run(df, years):
    '''
    Tracks (return df) with one appearance in the top 10 
    Followed by a drop off the list/down to below 66
    '''
    runs_df = df[df[years].apply(lambda x: x.between(1, 10)).any(axis=1)]
    print(runs_df)

# TODO: playlist making "algorithm" that curates songs from a year that don't make it too far in the subsequent ones (so are very temporally constricted)