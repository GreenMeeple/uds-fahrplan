import requests
import json
import csv
from location import get_stations, bbox

region = "saarvv" # option: saarvv, lux
tile_count = 6  # split into n * n grids
transport_mode = 2047 
seen_lids = set()
all_locs = []

full_bbox = bbox[region]
x_step = (full_bbox["urx"] - full_bbox["llx"]) // tile_count
y_step = (full_bbox["ury"] - full_bbox["lly"]) // tile_count

for i in range(tile_count):
    for j in range(tile_count):
        tile_bbox = {
            "llx": full_bbox["llx"] + i * x_step,
            "lly": full_bbox["lly"] + j * y_step,
            "urx": full_bbox["llx"] + (i + 1) * x_step,
            "ury": full_bbox["lly"] + (j + 1) * y_step
        }

        url, headers, body = get_stations(region=region, bbox_key=region, transport_mode=transport_mode, custom_bbox=tile_bbox)
        response = requests.post(url, headers=headers, data=json.dumps(body))
        data = response.json()

        locs = data.get("svcResL", [{}])[0].get("res", {}).get("locL", [])
        for stop in locs:
            lid = stop.get("lid")
            if lid and lid not in seen_lids:
                seen_lids.add(lid)
                all_locs.append(stop)

print(f"🚌 Found {len(all_locs)} unique stops in {tile_count*tile_count} tiles.")

# Save raw merged result
with open(f"stations_{region}_raw.json", "w", encoding="utf-8") as f:
    json.dump({"locL": all_locs}, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON file saved as 'stations_{region}_raw.json'")

# Extract only needed fields
cleaned_locs = [
    {
        "Station Name": stop.get("name", "unknown"),
        "LID": stop.get("lid", ""),
        "Modes of Transports": stop.get("pCls", "")
    }
    for stop in all_locs
]

# Save to JSON
with open(f"stations_{region}.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_locs, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON file saved as 'stations_{region}.json'")

# Save to CSV
with open(f"stations_{region}.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["Station Name", "LID", "Modes of Transports"])
    writer.writeheader()
    writer.writerows(cleaned_locs)

print(f"✅ CSV file saved as 'stations_{region}.csv'")
