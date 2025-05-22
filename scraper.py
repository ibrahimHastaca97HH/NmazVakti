import requests
from bs4 import BeautifulSoup
import json
import unicodedata

def normalize(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("utf-8").lower().replace("ı", "i").replace("ç", "c").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o")

BASE_URL = "https://namazvakitleri.diyanet.gov.tr/tr-TR"
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "html.parser")

city_select = soup.find("select", {"id": "drpIl"})
cities = [(option['value'], option.text.strip()) for option in city_select.find_all("option") if option['value'] != ""]

result = {}

for city_id, city_name in cities:
    city_norm = normalize(city_name)
    r = requests.post("https://namazvakitleri.diyanet.gov.tr/tr-TR/Home/GetIlceler", data={"ilId": city_id})
    ilceler = r.json()
    result[city_norm] = {}

    for ilce in ilceler:
        district_norm = normalize(ilce['IlceAdi'])
        result[city_norm][district_norm] = ilce['IlceID']

with open("districts.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("✅ districts.json dosyası oluşturuldu.")
