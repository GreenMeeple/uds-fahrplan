from rapidfuzz import fuzz

input_text = "uni"
station_name = "Uni-Hämostaseol.\/Vers.Zentr., Homburg"

def normalize(text):
    import unicodedata, re
    nfkd_form = unicodedata.normalize('NFKD', text)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return re.sub(r"[^\w\s]", "", only_ascii).lower()

score = fuzz.partial_ratio(normalize(input_text), normalize(station_name))
print(score)
