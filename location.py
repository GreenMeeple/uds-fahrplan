import requests
import json
from datetime import datetime, timedelta

# -----------------------
# Configuration
# -----------------------


bbox = {
    "saarvv": {"llx": 6900000, "lly": 49100000, "urx": 7420000, "ury": 49600000},
    "lux": {"llx": 6000000, "lly": 49560000, "urx": 6340000, "ury": 50030000}
}

locations = {
    "Johanneskirche/Rathaus": "A=1@O=Johanneskirche, Saarbrücken@X=6996295@Y=49236050@U=80@L=10619@B=1@p=1744897007@",
    "Mensa": "A=1@O=Universität Mensa, Saarbrücken@X=7043543@Y=49256356@U=80@L=10905@B=1@p=1744897007@",
    "Saarbasar": "A=1@O=Saarbasar, Saarbrücken@X=7036333@Y=49228849@U=80@L=11010@B=1@p=1744897007@",
    "HBF": "A=1@O=Saarbrücken Hbf@X=6991019@Y=49241066@U=80@L=8000323@B=1@p=1744897007@",
    "Waldhaus": "A=1@O=Waldhaus, Saarbrücken@X=7021528@Y=49246414@U=80@L=10803@B=1@p=1744897007@"
}

hafas_profiles = {
    "saarvv": {
        "url": "https://www.saarfahrplan.de/bin/mgate.exe",
        "auth": {"type": "AID", "aid": "yCW9qZFSye1wIv3gCzm5r7d2kJ3LIF"},
        "client": {
            "id": "ZPS-SAAR",
            "type": "WEB",
            "name": "webapp",
            "l": "vs_webapp",
            "v": 10004
        },
        "lang": "deu",
        "ver": "1.63"
    },
    "lux": {
        "url": "https://cdt.hafas.de/bin/mgate.exe",
        "auth": {"type": "AID", "aid": "SkC81GuwuzL4e0"},
        "client": {
            "id": "MMILUX",
            "type": "WEB",
            "name": "webapp",
            "l": "vs_webapp",
            "v": 10008
        },
        "lang": "eng",
        "ver": "1.77"
    }
}

# -----------------------
# Utility Functions
# -----------------------

def get_profile(region):
    if region not in hafas_profiles:
        raise ValueError(f"Unsupported region: {region}")
    return hafas_profiles[region]

def get_connection(region, from_key, to_key, extra_time=10, transport_mode=991):
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
                "maxChg": "1000",
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

    return url, headers, body

def get_stations(region="saarvv", bbox_key="saarland", transport_mode="regional", custom_bbox=None):
    profile = hafas_profiles[region]
    box = custom_bbox if custom_bbox else bbox[bbox_key]

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

    return url, headers, body
