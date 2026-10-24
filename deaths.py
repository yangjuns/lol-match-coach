import argparse
import json
from pathlib import Path


def fmt_time(ms: int) -> str:
    return f"{ms // 60000:02d}:{ms // 1000 % 60:02d}"


def latest_match_id(matches_dir: Path) -> str:
    best = max(
        (p for p in matches_dir.glob("*.json") if not p.stem.endswith("_timeline")),
        key=lambda p: json.loads(p.read_text(encoding="utf-8"))["info"]["gameStartTimestamp"],
    )
    return best.stem


def main() -> None:
    parser = argparse.ArgumentParser(description="List your deaths in a match with context.")
    parser.add_argument("match_id", nargs="?", help="Defaults to the most recent saved match.")
    parser.add_argument("--game-name", default="Hibala")
    parser.add_argument("--tag-line", default="NA1")
    parser.add_argument("--matches-dir", type=Path, default=Path(__file__).parent / "matches")
    args = parser.parse_args()

    match_id = args.match_id or latest_match_id(args.matches_dir)
    match = json.loads((args.matches_dir / f"{match_id}.json").read_text(encoding="utf-8"))
    timeline_path = args.matches_dir / f"{match_id}_timeline.json"
    if not timeline_path.exists():
        parser.error(f"{timeline_path} not found; run lol.py with --timeline")
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))

    participants = match["info"]["participants"]
    me = next(
        p
        for p in participants
        if p.get("riotIdGameName", "").lower() == args.game_name.lower()
        and p.get("riotIdTagline", "").lower() == args.tag_line.lower()
    )
    my_id = me["participantId"]
    by_id = {p["participantId"]: p for p in participants}
    frames = timeline["info"]["frames"]

    print(f"{match_id}: {me['championName']} {me['kills']}/{me['deaths']}/{me['assists']}")

    deaths = [
        e
        for f in frames
        for e in f["events"]
        if e["type"] == "CHAMPION_KILL" and e["victimId"] == my_id
    ]
    for e in deaths:
        # The frame at the start of that minute is the closest snapshot before the death.
        frame = frames[min(e["timestamp"] // 60000, len(frames) - 1)]
        mine = frame["participantFrames"][str(my_id)]
        killer = by_id.get(e.get("killerId", 0))
        killer_name = killer["championName"] if killer else "Executed (minion/tower)"
        helpers = ", ".join(
            by_id[a]["championName"] for a in e.get("assistingParticipantIds", [])
        )
        enemy_frame = (
            frame["participantFrames"][str(killer["participantId"])] if killer else None
        )
        pos = e["position"]
        print(
            f"\n[{fmt_time(e['timestamp'])}] Died to {killer_name}"
            + (f" (+ {helpers})" if helpers else "")
        )
        print(f"  position: ({pos['x']}, {pos['y']})")
        print(f"  you: level {mine['level']}, total gold {mine['totalGold']}, unspent {mine['currentGold']}")
        if enemy_frame:
            print(f"  killer: level {enemy_frame['level']}, total gold {enemy_frame['totalGold']}")
        print(f"  bounty given: {e.get('bounty', 0)}")

    if not deaths:
        print("No deaths found.")


if __name__ == "__main__":
    main()
