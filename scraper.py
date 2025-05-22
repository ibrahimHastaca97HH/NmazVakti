import requests
from bs4 import BeautifulSoup
import json
import unicodedata

BASE_URL = "https://namazvakitleri.diyanet.gov.tr"

def normalize(text):
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    return text.lower().replace(" ", "-").replace("ı", "i").replace("ç", "c") \
               .replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o")

def get_cities():
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    select = soup.find("select", {"id": "ddlIlList"})
    options = select.find_all("option")[1:]  # skip the first placeholder
    cities = [{"name": opt.text.strip(), "value": opt["value"]} for opt in options]
    return cities

def get_districts(city_value):
    res = requests.get(f"{BASE_URL}/tr-TR/{city_value}")
    soup = BeautifulSoup(res.text, "html.parser")
    select = soup.find("select", {"id": "ddlIlceList"})
    if not select:
        return []
    options = select.find_all("option")[1:]  # skip first
    return [{"name": opt.text.strip(), "value": opt["value"]} for opt in options]

def build_district_data():
    result = {}
    cities = get_cities()
    for city in cities:
        city_key = normalize(city["name"])
        result[city_key] = {}
        districts = get_districts(city["value"])
        for district in districts:
            district_key = normalize(district["name"])
            result[city_key][district_key] = district["value"]
        print(f"{city['name']} ✓")
    return result

if __name__ == "__main__":
    print("Veriler çekiliyor...")
    data = build_district_data()
    with open("districts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ districts.json oluşturuldu.")
