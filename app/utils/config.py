import csv

def load_channels(path: str) -> list[dict]:
    with open(path,'r',newline='',encoding="utf-8-sig") as channel_file:
        reader = csv.DictReader(channel_file)
        channels = []
        allowed_categories = {"finance","fitness", "golf"}

        for row in reader:
            channel_id = row["channel_id"].strip()
            channel_name = row["channel_name"].strip()
            channel_category = row["category"].strip().lower()
            
            if not channel_id:
                continue
            if channel_id.startswith("UC") and len(channel_id)>=10:
                if channel_category in allowed_categories:
                    channels.append({
                        "channel_id": channel_id,
                        "channel_name": channel_name,
                        "category": channel_category
                    })
                else:
                    raise ValueError(f"Invalid category: {channel_category}")
            else:
                raise ValueError(f"Invalid channel_id: {channel_id}")
            
        return channels
            

        
