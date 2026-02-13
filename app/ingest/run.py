import os
import csv
import json
from datetime import datetime, timezone, date
from typing import List, Dict

import requests
from dotenv import load_dotenv

YOUTUBE_API = "https://www.googleapis.com/youtube/v3"


def get_channel_stats(api_key: str, channel_id: str) -> dict:
    params = {
        "part": "snippet,statistics",
        "id": channel_id,
        "key": api_key,
    }
    r = requests.get(f"{YOUTUBE_API}/channels", params=params, timeout=30)
    r.raise_for_status()
    payload = r.json()

    items = payload.get("items", [])
    if not items:
        raise ValueError(f"No channel found for channel_id={channel_id}")

    item = items[0]
    stats = item.get("statistics", {})
    snippet = item.get("snippet", {})

    return {
        "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
        "channel_id": channel_id,
        "title": snippet.get("title"),
        "published_at": snippet.get("publishedAt"),
        "country": snippet.get("country"),
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "view_count": int(stats.get("viewCount", 0)),
        "video_count": int(stats.get("videoCount", 0)),
        "raw": item,
    }


def read_channels_csv(path: str = "channels.csv") -> List[Dict[str, str]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Create it in repo root.")

    channels: List[Dict[str, str]] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"channel_id", "channel_name", "category"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"{path} must have columns: {sorted(required)}")

        for row in reader:
            # Skip blank lines
            if not row.get("channel_id"):
                continue
            channels.append(
                {
                    "channel_id": row["channel_id"].strip(),
                    "channel_name": (row.get("channel_name") or "").strip(),
                    "category": (row.get("category") or "").strip().lower(),
                }
            )

    if not channels:
        raise ValueError(f"{path} contained zero channels.")
    return channels


def write_json(out_path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main():
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing YOUTUBE_API_KEY (put it in .env).")

    channels = read_channels_csv("channels.csv")

    run_date = date.today().isoformat()
    base_dir = os.path.join("data", "raw", "youtube", f"date={run_date}")

    successes = 0
    failures = 0

    for ch in channels:
        channel_id = ch["channel_id"]
        try:
            stats = get_channel_stats(api_key, channel_id)

            # attach your config metadata (category/name) so it flows downstream
            stats["category"] = ch["category"]
            stats["channel_name_config"] = ch["channel_name"]

            out_path = os.path.join(base_dir, f"channel_{channel_id}.json")
            write_json(out_path, stats)
            successes += 1
            print(f"[OK] {channel_id} -> {out_path}")
        except Exception as e:
            failures += 1
            print(f"[FAIL] {channel_id}: {e}")

    print(f"\nDone. successes={successes} failures={failures} total={len(channels)}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
