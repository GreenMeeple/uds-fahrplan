import sys, os
import requests
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from util.profiles import hafas_profiles, locations, parse_delay, parse_time

def get_trips(region="saarvv", from_key="Mensa", to_key="HBF", extra_time=10, transport_mode=991):
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
            "meth": "TripSearch",
            "req": {
                "depLocL": [{"lid": locations[from_key]}],
                "arrLocL": [{"lid": locations[to_key]}],
                "minChgTime": "-1",
                "liveSearch": False,
                "maxChg": "2",
                "jnyFltrL": [{
                    "type": "PROD",
                    "mode": "INC",
                    "value": transport_mode
                }],
                "gisFltrL": [
                    {"type": "P", "mode": "FB", "profile": {"type": "F", "enabled": True, "maxdist": "2000"}},
                    {"type": "M", "mode": "FBT", "meta": "foot_speed_normal"},
                    {"type": "M", "mode": "FBT", "meta": "bike_speed_normal"},
                    {"type": "P", "mode": "FB", "profile": {"type": "B", "enabled": False, "maxdist": "0"}},
                    {"type": "P", "mode": "FB", "profile": {"type": "K", "enabled": False, "maxdist": "0"}},
                    {"type": "P", "mode": "FB", "profile": {"type": "P", "enabled": False, "maxdist": "0"}},
                    {"type": "M", "mode": "FBT", "meta": "car_speed_normal"}
                ],
                "getPolyline": True,
                "outFrwd": True,
                "outTime": now.strftime("%H%M%S"),
                "outDate": now.strftime("%Y%m%d"),
                "ushrp": True,
                "getPasslist": True,
                "getTariff": True
            },
            "id": "1|3|"
        }]
    }
    res = requests.post(url, headers=headers, data=json.dumps(body))
    data = res.json()
    return data


def parse_trips_detail(data, start="HBF", ziel="Saarbasar"):

    try:
        outConL = data["svcResL"][0]["res"]["outConL"]
        common = data["svcResL"][0]["res"]["common"]
        locL = common["locL"]
        prodL = common["prodL"]
        details = [f"📍 {start} -> {ziel}:"]

        for con in outConL:
            details.append("-" * 35)
            arr_time = "--:--"
            for sec in con.get("secL", []):
                if sec["type"] == "JNY":
                    dep, arr, jny = sec["dep"], sec["arr"], sec["jny"]
                    arr_time = parse_time(arr.get('aTimeS'))
                    dep_time = dep.get('dTimeS')
                    delay = parse_delay(dep_time, dep.get('dTimeR')) if dep.get('dTimeR') else "+0"     
                    details.append(
                        f"⏱️ {parse_time(dep_time)}({delay}): {prodL[jny['prodX']]['name'].replace(" ", "")}\n"
                        f"📍 {locL[dep['locX']]['name']}\n"
                        f"➡️ {locL[arr['locX']]['name']}"
                    )
                elif "chg" in sec:
                    walk = sec["chg"].get("durFS", {}).get("txt", "")
                    if walk:
                        details.append(f"⏱️ {arr_time} Walk {walk} ")

        return "\n".join(details[:-1])

    except Exception as e:
        print(f"❌ Error parsing trip results: {e}")
        return None
    
def parse_trips_basic(data, start="HBF", ziel="Saarbasar"):

    try:
        outConL = data["svcResL"][0]["res"]["outConL"]
        common = data["svcResL"][0]["res"]["common"]
        prodL = common["prodL"]

        basic = [f"📍 {start} -> {ziel}:"]

        for con in outConL:
            basic.append("\n"+"-" * 35+"\n⏱️ ")
            for sec in con.get("secL", []):
                if sec["type"] == "JNY":
                    dep, jny = sec["dep"], sec["jny"]
                    dep_time = dep.get('dTimeS')
                    delay = parse_delay(dep_time, dep.get('dTimeR')) if dep.get('dTimeR') else "+0"                      
                    basic.append(f"{parse_time(dep_time)}({delay}): {prodL[jny['prodX']]['name'].replace(" ", "")}")
                elif "chg" in sec:
                    walk = sec["chg"].get("durFS", {}).get("txt", "")
                    if walk:
                        basic.append(f" ➡️ ")

        return "".join(basic[:-1])

    except Exception as e:
        print(f"❌ Error parsing trip results: {e}")
        return None

# Example use case

if __name__ == "__main__":
    # Allow running this file directly for local dev/testing
    trip = get_trips(region="saarvv", from_key="Mensa", to_key="Waldhaus", extra_time=0, transport_mode=991)
    with open("trips.json", "w", encoding="utf-8") as f:
        json.dump(trip, f, indent=2, ensure_ascii=False)
    print(parse_trips_detail(trip))
    print(parse_trips_basic(trip))
