locations = {
    "Johanneskirche/Rathaus": "A=1@O=Johanneskirche, Saarbrücken@X=6996295@Y=49236050@U=80@L=10619@B=1@p=1744897007@",
    "Mensa": "A=1@O=Universität Mensa, Saarbrücken@X=7043543@Y=49256356@U=80@L=10905@B=1@p=1744897007@",
    "Saarbasar": "A=1@O=Saarbasar, Saarbrücken@X=7036333@Y=49228849@U=80@L=11010@B=1@p=1744897007@",
    "HBF": "A=1@O=Saarbrücken Hbf@X=6991019@Y=49241066@U=80@L=8000323@B=1@p=1744897007@",
    "Waldhaus": "A=1@O=Waldhaus, Saarbrücken@X=7021528@Y=49246414@U=80@L=10803@B=1@p=1744897007@",
    "Test": "test"
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
    },
}

def parse_time(time): 
    return f"{time[:2]}:{time[2:4]}" if time else "--:--"

def parse_delay(plan_time, actual_time):
    def to_seconds(t):
        h, m, s = int(t[:2]), int(t[2:4]), int(t[4:])
        return h * 3600 + m * 60 + s
    delay = (to_seconds(plan_time) - to_seconds(actual_time)) // 60
    return f"{delay:+d}"
