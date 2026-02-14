"""
Analysis functions for Spotify Wrapped data.

This module provides various analysis capabilities to extract insights
from processed Wrapped playlist data, including trend analysis,
artist statistics, and track lifecycle tracking.
"""

import logging
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class WrappedAnalyzer:
    """Analyzes Spotify Wrapped data and extracts insights."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize analyzer with processed DataFrame.

        Args:
            df: Processed DataFrame from DataProcessor.preprocess()
                Must contain columns: name, artists, song_id, list_appearances,
                and year columns (2018, 2019, etc.)

        Raises:
            ValueError: If DataFrame structure is invalid
        """
        if df.empty:
            raise ValueError("DataFrame cannot be empty")

        self.df = df.copy()
        self.years = sorted([col for col in df.columns if isinstance(col, int)])

        if not self.years:
            raise ValueError("DataFrame must contain year columns (integers)")

        logger.info(f"Analyzer initialized with {len(df)} songs across {len(self.years)} years")

    def most_popular_artists(self) -> pd.DataFrame:
        """
        Get artists with multiple tracks across all Wrapped playlists.

        Returns:
            DataFrame with columns:
            - artist: Artist name
            - track_count: Number of unique tracks in playlists
            - list_appearances: Total appearances across all tracks

        Example:
            >>> analyzer = WrappedAnalyzer(df)
            >>> artists = analyzer.most_popular_artists()
            >>> artists[artists['track_count'] > 3]
        """
        # Explode artists (each artist becomes a row)
        exploded = self.df.explode("artists")
        exploded["artists"] = exploded["artists"].str.strip()

        # Count unique songs per artist
        artist_stats = (
            exploded.groupby("artists")
            .agg(
                track_count=("song_id", "count"),
                total_appearances=("list_appearances", "sum"),
                avg_score=("score", "mean"),
            )
            .reset_index()
            .rename(columns={"artists": "artist"})
            .sort_values("track_count", ascending=False)
        )

        logger.info(f"Found {len(artist_stats)} unique artists")
        return artist_stats

    def one_year_dream_runs(self) -> pd.DataFrame:
        """
        Identify tracks that were top 10 but completely disappeared next year.

        Ephemeral tracks that peaked early then vanished, capturing
        temporary obsessions and time-specific audio trends.

        Returns:
            DataFrame with columns:
            - name, artists, song_id, list_appearances, score
            - Year columns showing ranks
            - dream_year: Year of peak appearance
            - rank_in_dream_year: The rank achieved

        Example:
            >>> analyzer = WrappedAnalyzer(df)
            >>> dream_runs = analyzer.one_year_dream_runs()
        """
        # Find all tracks that were in top 10
        top_10_mask = self.df[self.years].apply(
            lambda x: x.between(1, 10).any(), axis=1
        )
        top_10_df = self.df[top_10_mask].copy()

        dream_runs = []

        for idx, row in top_10_df.iterrows():
            # Check for year-to-year drops
            for i in range(len(self.years) - 1):
                curr_year = self.years[i]
                next_year = self.years[i + 1]

                curr_rank = row[curr_year]
                next_rank = row[next_year]

                # Condition: in top 10 this year, completely absent next year
                if 1 <= curr_rank <= 10 and next_rank == 0:
                    dream_runs.append(
                        {
                            "name": row["name"],
                            "artists": row["artists"],
                            "song_id": row["song_id"],
                            "list_appearances": row["list_appearances"],
                            "score": row["score"],
                            "dream_year": curr_year,
                            "rank_in_dream_year": curr_rank,
                        }
                    )
                    break  # One dream run per song

        result = pd.DataFrame(dream_runs).sort_values("dream_year", ascending=False)
        logger.info(f"Found {len(result)} dream run tracks")
        return result

    def on_the_up(self) -> pd.DataFrame:
        """
        Find tracks that improved rank or returned after absence.

        Identifies tracks with >= 2 appearances that showed resilience
        by climbing ranks or making comebacks.

        Returns:
            DataFrame with columns:
            - name, artists, song_id, list_appearances, score
            - Year columns showing ranks
            - recovery_type: 'climbed' or 'returned'
            - recovery_year: Year of improvement/return

        Example:
            >>> analyzer = WrappedAnalyzer(df)
            >>> recoveries = analyzer.on_the_up()
        """
        # Filter tracks with >= 2 appearances
        multi_appearance = self.df[self.df["list_appearances"] >= 2].copy()

        on_the_up_list = []

        for idx, row in multi_appearance.iterrows():
            off_list = False
            for i in range(len(self.years) - 1):
                curr_year = self.years[i]
                next_year = self.years[i + 1]

                curr_rank = row[curr_year]
                next_rank = row[next_year]

                # Track if song was ever off the list
                if curr_rank > 0 and next_rank == 0:
                    off_list = True

                # Improvement detected
                if next_rank > 0:  # Song is back on list
                    if curr_rank > next_rank or off_list:  # Improved rank or returned
                        on_the_up_list.append(
                            {
                                "name": row["name"],
                                "artists": row["artists"],
                                "song_id": row["song_id"],
                                "list_appearances": row["list_appearances"],
                                "score": row["score"],
                                "recovery_type": "returned" if off_list else "climbed",
                                "recovery_year": next_year,
                                "previous_rank": curr_rank,
                                "new_rank": next_rank,
                            }
                        )
                        break

        result = pd.DataFrame(on_the_up_list).sort_values("recovery_year", ascending=False)
        logger.info(f"Found {len(result)} tracks on the up")
        return result

    def first_to_last_time(self) -> Dict[str, pd.DataFrame]:
        """
        Compare first Wrapped playlist with last, tracking persistence.

        Analyzes which songs stayed around, which disappeared, and
        which made unexpected comebacks between first and latest playlists.

        Returns:
            Dictionary with keys:
            - 'first_year_only': Tracks only in first year
            - 'persisted': Tracks from first year still in later lists
            - 'persisted_to_last': Tracks from first year in most recent list

        Example:
            >>> analyzer = WrappedAnalyzer(df)
            >>> comparison = analyzer.first_to_last_time()
            >>> comparison['persisted_to_last']
        """
        first_year = self.years[0]
        last_year = self.years[-1]

        # Tracks in first Wrapped
        first_year_tracks = self.df[self.df[first_year] > 0].copy()

        # Split into categories
        never_returned_mask = self.df[self.years[1:]].eq(0).all(axis=1)
        first_year_only = first_year_tracks[never_returned_mask & (first_year_tracks[first_year] > 0)]

        persisted = first_year_tracks[~never_returned_mask]

        persisted_to_last = first_year_tracks[
            (first_year_tracks[last_year] > 0) & (first_year_tracks[first_year] > 0)
        ]

        result = {
            "first_year_only": first_year_only,
            "persisted": persisted,
            "persisted_to_last": persisted_to_last,
        }

        logger.info(
            f"First to Last: {len(first_year_only)} disappeared, "
            f"{len(persisted)} persisted, {len(persisted_to_last)} still in latest"
        )

        return result

    def active_streaks(self, min_consecutive: int = 3) -> pd.DataFrame:
        """
        Find tracks present in consecutive years ending with most recent year.

        Identifies consistent favorites that have been in playlists
        continuously for multiple years up to the latest Wrapped.

        Args:
            min_consecutive: Minimum consecutive years required (default: 3)

        Returns:
            DataFrame with columns:
            - name, artists, song_id, list_appearances, score
            - Year columns showing ranks
            - streak_length: Number of consecutive years
            - streak_start_year: First year of streak

        Example:
            >>> analyzer = WrappedAnalyzer(df)
            >>> streaks = analyzer.active_streaks(min_consecutive=3)
        """
        active_streaks_list = []

        for idx, row in self.df.iterrows():
            # Check streak ending in most recent year
            if row[self.years[-1]] == 0:
                continue  # Must be in latest Wrapped

            # Count backwards from most recent year
            streak_length = 0
            for year in reversed(self.years):
                if row[year] > 0:
                    streak_length += 1
                else:
                    break

            if streak_length >= min_consecutive:
                streak_start_idx = len(self.years) - streak_length
                streak_start_year = self.years[streak_start_idx]

                active_streaks_list.append(
                    {
                        "name": row["name"],
                        "artists": row["artists"],
                        "song_id": row["song_id"],
                        "list_appearances": row["list_appearances"],
                        "score": row["score"],
                        "streak_length": streak_length,
                        "streak_start_year": streak_start_year,
                    }
                )

        result = pd.DataFrame(active_streaks_list).sort_values("streak_length", ascending=False)
        logger.info(f"Found {len(result)} active streaks")
        return result

    def one_timers(self) -> pd.DataFrame:
        """
        Get all tracks appearing in exactly one Wrapped playlist.

        One-off discoveries that never reappeared in later playlists.

        Returns:
            DataFrame with track info and their single appearance year

        Example:
            >>> analyzer = WrappedAnalyzer(df)
            >>> one_timers = analyzer.one_timers()
        """
        one_timers_df = self.df[self.df["list_appearances"] == 1].copy()

        # Find which year each one-timer appeared
        one_timers_df["appearance_year"] = one_timers_df[self.years].apply(
            lambda row: next((year for year in self.years if row[year] > 0), None), axis=1
        )

        result = one_timers_df.sort_values("appearance_year", ascending=False)
        logger.info(f"Found {len(result)} one-time appearances")
        return result

    def get_summary_stats(self) -> Dict:
        """
        Get high-level summary statistics for the dataset.

        Returns:
            Dictionary with keys:
            - total_unique_songs: Number of unique songs
            - total_tracks_fetched: Sum of all yearly tracks (may include duplicates)
            - avg_appearances: Mean appearances per song
            - most_consistent_artist: Artist with highest avg score
            - years_span: Tuple of (first_year, last_year)

        Example:
            >>> analyzer = WrappedAnalyzer(df)
            >>> stats = analyzer.get_summary_stats()
        """
        artist_stats = self.most_popular_artists()
        most_consistent_artist = artist_stats.iloc[0]["artist"] if not artist_stats.empty else "N/A"

        return {
            "total_unique_songs": len(self.df),
            "total_tracks_fetched": self.df[self.years].astype(bool).sum().sum(),
            "avg_appearances": self.df["list_appearances"].mean(),
            "years_span": (self.years[0], self.years[-1]),
            "years_count": len(self.years),
            "most_consistent_artist": most_consistent_artist,
        }
