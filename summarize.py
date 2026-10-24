import argparse
import json
from datetime import datetime
from pathlib import Path

QUEUES = {
    400: "Normal Draft",
    420: "Ranked Solo/Duo",
    430: "Normal Blind",
    440: "Ranked Flex",
    450: "ARAM",
    490: "Quickplay",
    700: "Clash",
    900: "URF",
    1700: "Arena",
}


def summarize(path: Path, game_name: str, tag_line: str) -> tuple[int, str] | None:
    info = json.loads(path.read_text(encoding="utf-8"))["info"]
    me = next(
        (
            p
            for p in info["participants"]
            if p.get("riotIdGameName", "").lower() == game_name.lower()
            and p.get("riotIdTagline", "").lower() == tag_line.lower()
        ),
        None,
    )
    if me is None:
        return None

    start = info["gameStartTimestamp"]
    when = datetime.fromtimestamp(start / 1000).strftime("%Y-%m-%d %H:%M")
    queue = QUEUES.get(info["queueId"], f"Queue {info['queueId']}")
    result = "WIN " if me["win"] else "LOSS"
    kda = f"{me['kills']}/{me['deaths']}/{me['assists']}"
    cs = me["totalMinionsKilled"] + me["neutralMinionsKilled"]
    line = (
        f"{when}  {queue:<16} {result}  {me['championName']:<14} "
        f"{me['teamPosition'] or '-':<8} KDA {kda:<9} CS {cs:<4} "
        f"{info['gameDuration'] // 60:>2} min  {path.stem}"
    )
    return start, line


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize saved LoL match JSON files.")
    parser.add_argument("--game-name", default="Hibala")
    parser.add_argument("--tag-line", default="NA1")
    parser.add_argument("--matches-dir", type=Path, default=Path(__file__).parent / "matches")
    args = parser.parse_args()

    rows = []
    for path in args.matches_dir.glob("*.json"):
        if path.stem.endswith("_timeline"):
            continue
        row = summarize(path, args.game_name, args.tag_line)
        if row:
            rows.append(row)

    for _, line in sorted(rows, reverse=True):
        print(line)

    if not rows:
        print(f"No matches found for {args.game_name}#{args.tag_line} in {args.matches_dir}")


if __name__ == "__main__":
    main()
