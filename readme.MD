# Spotify Wrapped Insights

Retrieve and analyse your Spotify Wrapped playlists over the years and get insights and trends about your favourite earworms over the years.

**Three-part project:**

1. **GitHub Pipeline** - Fetches Wrapped tracks across multiple years into a single CSV
2. **Kaggle Notebook** - Exploratory analysis showing insights from your data (WIP)
3. **Static Webpage** - Visual dashboard (future)

---

## Quick Start

### Prerequisites

- Python 3.12+
- Spotify Premium. You will be using the Spotify Web API, [which necessitates a Premium Account](https://developer.spotify.com/documentation/web-api)
- Spotify Developer account ([create here](https://developer.spotify.com/dashboard))
- Your Spotify Wrapped playlist IDs (see Setup below)

### Installation

1. **Clone and setup**

   ```bash
   git clone https://github.com/yatharthsood00/spotify-wrapped-insights.git
   cd spotify-wrapped-insights
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure credentials**

   ```bash
   cp .env.example .env
   # Edit .env with your Spotify API credentials and playlist IDs
   ```

3. **Quick test**

   ```bash
   python scripts/main.py --process     # Fetch and process your Wrapped data
   ```

---

## Testing & Validation

Complete test suite available in [TESTING.md](TESTING.md)

Quick validation:

```bash
# Test configuration
python -c "from src.config import SPOTIFY_CLIENT_ID; print('✓ Credentials configured')"

# Test data pipeline
python scripts/main.py --process

# Test OAuth (if configured)
python exploratory/oauth_explorer.py --user-profile
```

---

## Troubleshooting

### "Authentication failed" or "Credentials not found"

```bash
# Verify .env file
cat .env

# Check credentials are loaded
python -c "from src.config import SPOTIFY_CLIENT_ID; print(f'ID: {SPOTIFY_CLIENT_ID}')"
```

Should show your actual credentials (not empty)

### OAuth "redirect_uri_mismatch"

See [OAUTH_SETUP.md - Common Issues](OAUTH_SETUP.md#common-issues)

### "No module named 'spotipy'"

```bash
# Reinstall requirements
pip install -r requirements.txt
```

### Notebook won't run

```bash
# Ensure Jupyter is installed
pip install jupyter ipykernel
jupyter notebook notebooks/kaggle_export.ipynb
```

---

## Architecture

**Three-layer design:**

1. **Library (`src/`)** - Core Spotify interactions and data processing
2. **Scripts (`scripts/`)** - CLI executables for production use
3. **Exploratory (`exploratory/`)** - Experimentation and learning

**Data flow:**

```
Spotify API → list.csv (raw) → working.csv (processed) → Analysis
  ↓                              ↓
spotify_fetcher.py         data_processor.py
  ↓
main.py (CLI)
```

---

## Setup

### 1. Spotify Developer Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account (create if needed)
3. Create a new app and accept the terms
4. Copy **Client ID** and **Client Secret**
5. In your `.env` file, add:
   ```
   SPOTIPY_CLIENT_ID=your_client_id_here
   SPOTIPY_CLIENT_SECRET=your_client_secret_here
   ```

### 2. Wrapped Playlist IDs

Spotify's Wrapped playlists are "special" - you need to copy them to regular playlists before Spotify lets you access them via the API:

1. Go to your Wrapped playlist ("Your Top Songs [YEAR]")
2. Select all songs (Ctrl+A / Cmd+A)
3. Right-click → Add to Playlist → Create New Playlist
4. Get the playlist ID from the Spotify Share menu
   - Share → Copy Link → extract ID (between `/playlist/` and `?`)

5. Add to `.env`:
   ```
   pl_2023=your_playlist_id
   pl_2024=your_playlist_id
   pl_2025=your_playlist_id
   ```

You need at least one Wrapped playlist configured to run the pipeline

---

## Usage

### Part 1: Data Pipeline (GitHub)

**Process Wrapped playlists into analysis-ready data**

```bash
# Smart pipeline (fetches if needed, uses cache if available)
python scripts/main.py --process

# Force fresh fetch and processing
python scripts/main.py --process --force

# Fetch raw data only
python scripts/main.py --fetch
```

Outputs:

- `data/list.csv` - Raw data (100 tracks per year)
- `data/working.csv` - Processed data (all unique songs, deduplicated)

**Data format:**

- song_id: MD5 hash of name + artists (unique identifier). MD5 hash ensures unique track name. Yes, MD5 is overkill but that's the first thing I thought.
- list_appearances: How many years song appeared
- score: Weighted ranking score. Simple (and placeholder) scoring system for now.
- Year columns: Rank in each year (0 = not present)

### Part 2: Analysis Notebook (Kaggle)

**Run exploratory analysis on your data. Run it like a Jupyter Notebook**



