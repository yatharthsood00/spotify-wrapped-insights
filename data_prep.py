import pandas as pd
import hashlib

def df_preprocessing(df, years):
    '''
    Big singular function to clean and process the CSV for more accurate processing. Addresses the following issues:

    1. Single vs. Album releases.
    2. Minor spelling differences (the/The).
    X. Can be modified to address remasters/re-releases (i.e. Taylor's Versions), but 
    that may be too complex for now.
    
    '''

    # Combine "name" and "artists" columns into a new column "combined"
    # TODO: this messes with the new artist cleanup thing

    # changing this logic into lowercase name + alphabetical order lowercase artists names

    df['combined'] = (df['name'] + ' '.join([str(artist) for artist in sorted(df['artists'])])).str.lower()

    # df['combined'] = (df['name'] + ' - ' + df['artists']).str.lower() # addressing the "the"/"The" issue
    # Hash the combined values to create a unique song_id - some songs have different spotify IDs but are the exact same track
    df['song_id'] = df['combined'].apply(lambda x: hashlib.md5(x.encode()).hexdigest())
    df = df.drop(columns=['combined'])

    # pivoting table, for years on song_id
    pivot_df = df.pivot_table(index='song_id', columns='year', values='index', fill_value=0)

    # Reset the index to make 'song_id' a regular column
    pivot_df = pivot_df.reset_index()

    # convert floats to int to make data cleaner
    pivot_df[years] = pivot_df[years].astype(int)

    if df['song_id'].duplicated().any():
        df = df.drop_duplicates(subset='song_id')
        
    pivot_df = pd.merge(pivot_df, df[['name', 'artists', 'song_id', 'id']], on='song_id', how='left')

    pivot_df['list_appearances'] = pivot_df[years].apply(lambda row: row.astype(bool).sum(), axis=1)

    # Scoring system implementation - simple approach

    pivot_df['score'] = (100 - pivot_df[[col for col in years]].replace(0, pd.NA) + 1).fillna(0).sum(axis=1)

    # rearranging df to have all year indices to the end
    cols = ['name', 'artists', 'song_id', 'id', 'list_appearances', 'score'] + years
    pivot_df = pivot_df[cols]

    # print(pivot_df.sort_values(by='score', ascending=False))

    return pivot_df

