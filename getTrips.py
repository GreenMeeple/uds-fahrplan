import requests
import json
from datetime import datetime, timedelta
from location import get_connection

def parse_trips(start="HBF", ziel="Saarbasar", extra_time=10):
    region = "saarvv"
    url, headers, body = get_connection(region, start, ziel, extra_time)
    response = requests.post(url, headers=headers, data=json.dumps(body))
    data = response.json()
    save_trips(data)

    try:
        outConL = data["svcResL"][0]["res"]["outConL"]
        common = data["svcResL"][0]["res"]["common"]
        locL = common["locL"]
        prodL = common["prodL"]

        output = [f"From {start} to {ziel}:\n"]

        for con in outConL:
            output.append("-" * 35+"\n")
            arr_time = "--:--"
            for sec in con.get("secL", []):
                if sec["type"] == "JNY":
                    dep, arr, jny = sec["dep"], sec["arr"], sec["jny"]

                    def parse_time(ts): return f"{ts[:2]}:{ts[2:4]}" if ts else "--:--"
                    arr_time = parse_time(arr.get('aTimeS'))
                    output.append(
                        f"🚌 {prodL[jny['prodX']]['name']}, ⏱️ {parse_time(dep.get('dTimeS'))}\n"
                        f"🧭 {locL[dep['locX']]['name']}\n"
                        f"📍 {locL[arr['locX']]['name']}\n"
                    )
                elif "chg" in sec:
                    walk = sec["chg"].get("durFS", {}).get("txt", "")
                    if walk:
                        output.append(f"🚶 Walk {walk} ⏱️ {arr_time}\n")

        return "\n".join(output)

    except Exception as e:
        return f"❌ Error parsing trip results: {e}"

def save_trips(data):
    with open("trips.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    print(parse_trips())