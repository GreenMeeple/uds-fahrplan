import sys, os
import requests
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from util.profiles import hafas_profiles, locations, parse_delay, parse_time

def get_departures(region="saarvv", station="Mensa", extra_time=0):
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
                    "lid": locations[station] if station in locations else station,
                },
                "type": "DEP",
                "sort": "PT",
                "maxJny": 5
            },
            "meth": "StationBoard",
            "id": "1|4|"
        }]
    }

    res = requests.post(url, headers=headers, json=body)
    data = res.json()
    return data

def parse_departures(data, max_items=10):
    jnyL = data["svcResL"][0]["res"]["jnyL"]

    common = data.get("svcResL", [])[0].get("res", {}).get("common", {})
    prodL = common.get("prodL", [])
    locL = common.get("locL", [])

    output = [f"Departures from {locL[0]['name']}"]

    for jny in jnyL[:max_items]:
        try:

            prod = prodL[jny["prodX"]]
            line_name = prod.get("name", "unknown").replace(" ", "")
            direction = jny.get("dirTxt", "")
            dep = jny["stbStop"]
            dep_time = dep.get("dTimeS", "")
            delay = parse_delay(dep_time, dep.get('dTimeR')) if dep.get('dTimeR') else "+0"                      

            output.append(f"⏱️ {parse_time(dep_time)}({delay}): {line_name} to {direction}")
        except Exception as e:
            print(f"⚠️ Error parsing journey: {e}")
            continue

    return "\n".join(output) if output else "❌ No valid journeys found."

# Example use case
if __name__ == "__main__":
    departures = get_departures("saarvv", "Mensa", 10)
    with open("departures.json", "w", encoding="utf-8") as f:
        json.dump(departures, f, indent=2, ensure_ascii=False)
    print(parse_departures(departures))
