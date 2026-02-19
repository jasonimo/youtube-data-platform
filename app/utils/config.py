import csv

def load_channels(path: str) -> list[dict]:
    with open(path, "r", newline="", encoding="utf-8-sig") as channel_file:
        reader = csv.DictReader(channel_file)
        channels: list[dict] = []
        allowed_categories = {"finance", "fitness", "golf"}

        for row in reader:
            channel_id = (row.get("channel_id") or "").strip()
            channel_name = (row.get("channel_name") or "").strip()
            channel_category = (row.get("category") or "").strip().lower()

            if not channel_id:
                continue

            if not (channel_id.startswith("UC") and len(channel_id) >= 10):
                raise ValueError(f"Invalid channel_id: {channel_id}")

            if channel_category not in allowed_categories:
                raise ValueError(f"Invalid category: {channel_category}")

            channels.append({
                "channel_id": channel_id,
                "channel_name": channel_name,
                "category": channel_category,
            })

        return channels
