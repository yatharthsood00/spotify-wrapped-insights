"""
Data processing and preprocessing for Spotify Wrapped data.

This module handles CSV input, data cleaning, deduplication,
and transformation into analysis-ready formats.
"""

import hashlib
import logging
from typing import List, Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes and cleans Spotify Wrapped track data."""

    @staticmethod
    def load_raw_data(filepath: str) -> pd.DataFrame:
        """
        Load raw CSV data from Spotify API fetch.

        Args:
            filepath: Path to raw CSV file

        Returns:
            DataFrame with columns: year, index, name, artists, id, link

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If CSV format is invalid
        """
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} rows from {filepath}")

            # Parse artists string representation back to lists
            df["artists"] = df["artists"].apply(
                lambda x: eval(x) if isinstance(x, str) else x
            )

            return df
        except FileNotFoundError as e:
            logger.error(f"Raw data file not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse CSV: {e}")
            raise ValueError(f"Invalid CSV format: {e}")

    @staticmethod
    def create_song_id(row: pd.Series) -> str:
        """
        Create unique song ID from name and artists.

        Handles duplicate Spotify IDs, capitalization differences,
        and single vs. album track variations by creating a hash
        of the lowercase name + sorted artist names.

        Args:
            row: DataFrame row with 'name' and 'artists' columns

        Returns:
            MD5 hash string representing unique song identity

        Note:
            Taylor's Version and other re-releases with different
            names would need manual matching.
        """
        try:
            name = str(row["name"]).lower()
            artists = " ".join(sorted([str(a).lower() for a in row["artists"]]))
            combined = f"{name} {artists}"
            return hashlib.md5(combined.encode("utf-8")).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to create song_id for {row['name']}: {e}")
            return None

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Comprehensive data preprocessing and cleaning.

        Performs:
        1. Song ID creation (deduplication)
        2. Year-based pivoting
        3. Metrics calculation (appearances, score)
        4. Output formatting

        Args:
            df: Raw DataFrame from load_raw_data()

        Returns:
            Processed DataFrame ready for analysis with structure:
            - name, artists, song_id, id, list_appearances, score
            - Year columns (2018, 2019, ...) with ranks

        Example:
            >>> processor = DataProcessor()
            >>> raw_df = processor.load_raw_data("list.csv")
            >>> processed_df = processor.preprocess(raw_df)
        """
        if df.empty:
            logger.warning("Input DataFrame is empty")
            return df

        df = df.copy()
        years = sorted(df["year"].unique().tolist())
        logger.info(f"Processing data for years: {years}")

        # Step 1: Create song IDs
        df["song_id"] = df.apply(self.create_song_id, axis=1)
        df = df.dropna(subset=["song_id"])
        logger.info(f"Created song IDs; {len(df)} valid rows")

        # Step 2: Pivot by song_id and year
        pivot_df = df.pivot_table(
            index="song_id", columns="year", values="index", fill_value=0
        )
        pivot_df = pivot_df.reset_index()

        # Convert to integers
        pivot_df[years] = pivot_df[years].astype(int)
        logger.info(f"Pivoted data to {len(pivot_df)} unique songs")

        # Step 3: Remove duplicate song_ids and merge metadata
        df_unique = df.drop_duplicates(subset="song_id")
        pivot_df = pd.merge(
            pivot_df,
            df_unique[["name", "artists", "song_id", "id"]],
            on="song_id",
            how="left",
        )

        # Step 4: Calculate metrics
        pivot_df["list_appearances"] = pivot_df[years].apply(
            lambda row: (row > 0).sum(), axis=1
        )

        # Simple scoring: sum of (100 - rank + 1) for each appearance
        pivot_df["score"] = (
            (100 - pivot_df[years].replace(0, pd.NA) + 1)
            .fillna(0)
            .sum(axis=1)
        )

        # Step 5: Reorder columns
        cols = ["name", "artists", "song_id", "id", "list_appearances", "score"] + years
        pivot_df = pivot_df[cols]

        logger.info(f"Processing complete: {len(pivot_df)} unique songs")
        return pivot_df

    @staticmethod
    def save_processed_data(df: pd.DataFrame, filepath: str) -> None:
        """
        Save processed DataFrame to CSV.

        Args:
            df: Processed DataFrame from preprocess()
            filepath: Path to save CSV

        Raises:
            IOError: If file cannot be written
        """
        try:
            df.to_csv(filepath, index=False, encoding="utf-8")
            logger.info(f"Processed data saved to {filepath}")
        except IOError as e:
            logger.error(f"Failed to save processed data to {filepath}: {e}")
            raise
