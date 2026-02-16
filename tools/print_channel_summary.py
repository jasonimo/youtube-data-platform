from app.utils.config import load_channels

channels = load_channels("channels.csv")

category_count = {}

for ch in channels:
    category = ch["category"]
    if category not in category_count:
        category_count[category] = 1
    else:
        category_count[category] += 1

print(f"Loaded {len(channels)} channels")
for cat, count in category_count.items():
    print(f"{cat}: {count}")


