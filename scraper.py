import requests
from bs4 import BeautifulSoup
import json
import unicodedata
import time

def normalize_string(string):
    string = unicodedata.normalize("NFKD", string).encode("ASCII", "ignore").decode("utf-8")
    return string.lower().replace("ı", "i").replace("ç", "c").replace("ş", "s")\
        .replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace(" ", "").replace("-", "")

base_url = "https://namazvakitleri.diyanet.gov.tr/tr-TR"
headers = {"User-Agent": "Mozilla/5.0"}

# Şehirleri çek
response = requests.get(base_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

city_select = soup.find("select", {"id": "IlListesi"})
cities = {
    option.text.strip(): option["value"]
    for option in city_select.find_all("option") if option["value"]
}

data = {}

for city_name, city_id in cities.items():
    city_key = normalize_string(city_name)
    data[city_key] = {}

    print(f"[+] {city_name} ({city_key}) şehir işleniyor...")

    # Şehir sayfasına git ve ilçeleri çek
    city_url = f"{base_url}/Sehir/{city_id}"
    try:
        city_resp = requests.get(city_url, headers=headers)
        city_soup = BeautifulSoup(city_resp.text, "html.parser")
        district_select = city_soup.find("select", {"id": "IlceListesi"})

        if district_select:
            for option in district_select.find_all("option"):
                district_name = option.text.strip()
                district_id = option["value"]
                district_key = normalize_string(district_name)
                data[city_key][district_key] = district_id
    except Exception as e:
        print(f"[!] {city_name} ilçeleri çekilirken hata: {e}")

    time.sleep(0.5)  # Diyanet sunucusunu yormamak için bekle

# Dosyaya yaz
with open("districts.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ districts.json başarıyla oluşturuldu.")
