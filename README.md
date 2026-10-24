# LoL Match Coach

Small scripts that download your League of Legends match data from the Riot API and summarize it to help you find what to improve.

## Setup

```bash
pip install -r requirements.txt
cp riot_api_key.example.txt riot_api_key.txt   # then paste your key into riot_api_key.txt
```

Get a key at https://developer.riotgames.com. Development keys expire every 24 hours.
`riot_api_key.txt` is git-ignored. You can also set the `RIOT_API_KEY` environment variable as a fallback.

## Usage

```bash
# Download recent matches (and optionally their timelines) into matches/
python3 lol.py --game-name YourName --tag-line NA1 --count 10 --timeline

# One-line summary per saved match
python3 summarize.py --game-name YourName --tag-line NA1

# Your deaths in a match, with time, position, and gold/level context
python3 deaths.py [MATCH_ID] --game-name YourName --tag-line NA1
```

Use `--region` (americas, asia, europe, sea) for non-NA accounts.

## Files

- `lol.py` - fetches match and timeline JSON from the Riot API
- `summarize.py` - per-match summary
- `deaths.py` - per-death analysis from the timeline
