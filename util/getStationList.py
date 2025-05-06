import requests
import json
import csv
from profiles import hafas_profiles

bbox = {
    "saarvv": {"llx": 6900000, "lly": 49100000, "urx": 7420000, "ury": 49600000},
    "lux": {"llx": 6000000, "lly": 49560000, "urx": 6340000, "ury": 50030000}
}

# transport_mode = 991: everything except school bus, 2047: everything
def get_station_list(region="saarvv", transport_mode=991, custom_bbox=None):
    profile = hafas_profiles[region]
    box = custom_bbox if custom_bbox else bbox[region]

    url = profile["url"]
    headers = {
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
        "User-Agent": "HAFAS"
    }

    body = {
        "ver": profile["ver"],
        "lang": profile["lang"],
        "auth": profile["auth"],
        "client": profile["client"],
        "formatted": False,
        "svcReqL": [{
            "meth": "LocGeoPos",
            "req": {
                "rect": {
                    "llCrd": {"x": box["llx"], "y": box["lly"]},
                    "urCrd": {"x": box["urx"], "y": box["ury"]}
                },
                "locFltrL": [{
                    "type": "PROD",
                    "mode": "INC",
                    "value": transport_mode
                }],
                "getPOIs": False,
                "getStops": True,
                "zoom": 13
            },
            "id": "fetch_stops"
        }]
    }
    res = requests.post(url, headers=headers, data=json.dumps(body))
    data = res.json()
    locs = data.get("svcResL", [{}])[0].get("res", {}).get("locL", [])


    if not custom_bbox:
        print(f"🚌 Found {len(locs)} unique stops.")
        with open(f"stations_{region}_raw.json", "w", encoding="utf-8") as f:
            json.dump(locs, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON file saved as 'stations_{region}_raw.json'")
    return locs

def get_station_list_tile(region="saarvv", transport_mode=991, tile_count = 3):
    loc_by_lid = {}
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

            data = get_station_list(region=region, transport_mode=transport_mode, custom_bbox=tile_bbox)
            for stop in data:
                lid = stop.get("lid")
                if lid:
                    loc_by_lid[lid] = stop  # overwrites duplicates

    all_locs = list(loc_by_lid.values())
    print(f"🚌 Found {len(all_locs)} unique stops in {tile_count*tile_count} tiles.")

    return all_locs

def parse_stations(data, region="saarvv"):

    # Extract only needed fields
    cleaned_locs = [
        {
            "Station Name": stop.get("name", "unknown"),
            "LID": stop.get("lid", ""),
            "Modes of Transports": stop.get("pCls", "")
        }
        for stop in data
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

# Example use case
if __name__ == "__main__":
    bbox_region="saarvv" 

    # For small area
    stations = get_station_list(bbox_region, transport_mode=2047, custom_bbox=None)
    with open(f"stations_{bbox_region}_raw.json", "w", encoding="utf-8") as f:
        json.dump(stations, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON file saved as 'stations_{bbox_region}_raw.json'")
    
    # For bigger area, we need to slice into smaller region
    stations_wide = get_station_list_tile(bbox_region, transport_mode=2047, tile_count = 3)
    with open(f"stations_{bbox_region}_raw.json", "w", encoding="utf-8") as f:
        json.dump(stations_wide, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON file saved as 'stations_{bbox_region}_raw.json'")
    
    parse_stations(stations_wide, bbox_region)
