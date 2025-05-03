import requests
import json
from datetime import datetime, timedelta
from profiles import hafas_profiles, locations

def get_departures(region="saarvv", station="Mensa", extra_time=0, max_journeys=10):
    now = datetime.now() + timedelta(minutes=extra_time)

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
            "req": {
                "jnyFltrL": [
                    {
                        "type": "PROD",
                        "mode": "INC",
                        "value": 991
                    }
                ],
                "stbLoc": {
                    "lid": locations[station],
                },
                "type": "DEP",
                "sort": "PT",
                "maxJny": max_journeys
            },
            "meth": "StationBoard",
            "id": "1|4|"
        }]
    }

    res = requests.post(url, headers=headers, json=body)
    data = res.json()
    with open("departures.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return data

# Example use case
if __name__ == "__main__":
    departures = get_departures("saarvv", "Mensa", 10, 991)
    # print(parse_departures(departures))
