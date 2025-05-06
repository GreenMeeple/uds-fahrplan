import re
import requests
import json
import csv
from util.profiles import hafas_profiles

def clean_lid(lid: str) -> str:
    # Extract only A, X, Y fields
    matches = re.findall(r'(?:^|@)([AXY]=[^@]+)', lid)
    return '@'.join(matches) + '@'

def getStations(keyword="mensa", region="saarvv"):
    profile = hafas_profiles[region]
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
            "meth": "LocMatch",
            "req": {
                "input": {
                    "field": "S",
                    "loc": {
                        "type": "ALL",
                        "name": keyword,
                    },
                    "maxLoc": 5
                }
            },
            "id": "1|3|"
        }]
    }

    try:
        res = requests.post(url, headers=headers, data=json.dumps(body))
        data = res.json()
        return data
    except Exception as e:
        print(f"❌ Error fetching location matches: {e}")
        return None

def parse_stations(data):

    locL = data.get("svcResL", [])[0].get("res", {}).get("match", {}).get("locL", [])
    output = {}

    for station in locL:
        try:
            output[station['name']] = clean_lid(station['lid'])
        except Exception as e:
            print(f"⚠️ Error parsing journey: {e}")
            continue

    return output

# test case
if __name__ == "__main__":
    bbox_region="saarvv" 

    # For small area
    stations = getStations("mensa", "saarvv")
    with open(f"search_{bbox_region}.json", "w", encoding="utf-8") as f:
        json.dump(stations, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON file saved as 'search_{bbox_region}.json'")
    print(parse_stations(stations))
