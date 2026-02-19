# Import the function we wrote to load and validate channels from the CSV
from app.utils.config import load_channels

# Load channel data from the CSV file into a list of dictionaries
channels = load_channels("channels.csv")

# Dictionary to store counts per category
category_count = {}

# Loop through each channel and count how many belong to each category
for ch in channels:
    category = ch["category"]

    # If this category has not been seen before, initialize it to 1
    if category not in category_count:
        category_count[category] = 1
    # Otherwise, increment the existing count
    else:
        category_count[category] += 1

# Print total number of valid channels loaded
print(f"Loaded {len(channels)} channels")

# Print category breakdown
for cat, count in category_count.items():
    print(f"{cat}: {count}")
