import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests


KEY_FILE = Path(__file__).parent / "riot_api_key.txt"


def load_api_key() -> str | None:
    if KEY_FILE.exists():
        return KEY_FILE.read_text(encoding="utf-8").strip() or None
    return os.environ.get("RIOT_API_KEY")


def get_json(
    session: requests.Session,
    url: str,
    api_key: str,
    params: dict[str, int] | None = None,
) -> Any:
    response = session.get(
        url,
        headers={"X-Riot-Token": api_key},
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download recent League of Legends match data as JSON."
    )
    parser.add_argument("--game-name", default="Hibala")
    parser.add_argument("--tag-line", default="NA1")
    parser.add_argument(
        "--count", type=int, default=5, help="Number of recent matches (1-100)."
    )
    parser.add_argument(
        "--region",
        choices=("americas", "asia", "europe", "sea"),
        default="americas",
        help="Match/account routing region (NA accounts use americas).",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("matches"))
    parser.add_argument(
        "--timeline",
        action="store_true",
        help="Also save <matchId>_timeline.json for each match.",
    )
    args = parser.parse_args()

    if not 1 <= args.count <= 100:
        parser.error("--count must be between 1 and 100")

    api_key = load_api_key()
    if not api_key:
        parser.error(f"Put your Riot API key in {KEY_FILE}")

    base_url = f"https://{args.region}.api.riotgames.com"
    account_url = (
        f"{base_url}/riot/account/v1/accounts/by-riot-id/"
        f"{quote(args.game_name, safe='')}/{quote(args.tag_line, safe='')}"
    )

    with requests.Session() as session:
        account = get_json(session, account_url, api_key)
        puuid = account["puuid"]
        match_ids = get_json(
            session,
            f"{base_url}/lol/match/v5/matches/by-puuid/{quote(puuid, safe='')}/ids",
            api_key,
            params={"start": 0, "count": args.count},
        )

        args.output_dir.mkdir(parents=True, exist_ok=True)
        for match_id in match_ids:
            match = get_json(
                session,
                f"{base_url}/lol/match/v5/matches/{quote(match_id, safe='')}",
                api_key,
            )
            output_path = args.output_dir / f"{match_id}.json"
            output_path.write_text(json.dumps(match, indent=2), encoding="utf-8")
            print(f"Saved {output_path}")

            if args.timeline:
                timeline = get_json(
                    session,
                    f"{base_url}/lol/match/v5/matches/{quote(match_id, safe='')}/timeline",
                    api_key,
                )
                timeline_path = args.output_dir / f"{match_id}_timeline.json"
                timeline_path.write_text(json.dumps(timeline, indent=2), encoding="utf-8")
                print(f"Saved {timeline_path}")

        if not match_ids:
            print("No matches were returned for this Riot ID.")


if __name__ == "__main__":
    main()
