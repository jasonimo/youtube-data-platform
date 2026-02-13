import os
import json
from datetime import datetime, timezone

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


def main():
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing YOUTUBE_API_KEY (put it in .env).")

    # For quick testing, we’ll use Google Developers channel
    channel_id = os.getenv("TEST_CHANNEL_ID", "UC_x5XG1OV2P6uZZ5FSM9Ttw")

    result = get_channel_stats(api_key, channel_id)

    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", f"channel_{channel_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Wrote {out_path}")
    print(f"{result['title']} | subs={result['subscriber_count']} views={result['view_count']}")


if __name__ == "__main__":
    main()
