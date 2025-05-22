from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import json
import unicodedata
import os

app = FastAPI()

# DISTRICTS.JSON verisini yükle
with open("districts.json", "r", encoding="utf-8") as f:
    DISTRICTS = json.load(f)

def normalize_string(string):
    string = unicodedata.normalize("NFKD", string).encode("ASCII", "ignore").decode("utf-8")
    return string.lower().replace("ı", "i").replace("ç", "c").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o")

def get_district_id(city: str, district: str):
    city_n = normalize_string(city)
    district_n = normalize_string(district)

    city_data = DISTRICTS.get(city_n)
    if not city_data:
        return None

    return city_data.get(district_n)

def fetch_prayer_times(city_district_id):
    url = f"https://namazvakitleri.diyanet.gov.tr/tr-TR/{city_district_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.select_one('#tab-1 > div > table')
    if not table:
        return None

    result = []
    for row in table.select("tr"):
        cols = row.find_all("td")
        if len(cols) >= 8:
            result.append({
                "miladi_tarih": cols[0].text.strip(),
                "hicri_tarih": cols[1].text.strip(),
                "imsak": cols[2].text.strip(),
                "gunes": cols[3].text.strip(),
                "ogle": cols[4].text.strip(),
                "ikindi": cols[5].text.strip(),
                "aksam": cols[6].text.strip(),
                "yatsi": cols[7].text.strip()
            })
    return result

@app.get("/")
def root():
    return {"message": "✅ Ezan vakitleri API aktif"}

@app.get("/vakitler")
def get_vakitler(
    city: str = Query(..., description="Şehir adı"),
    district: str = Query(..., description="İlçe adı")
):
    try:
        district_id = get_district_id(city, district)
        if not district_id:
            return JSONResponse(
                status_code=404,
                content={"status": False, "error": "Şehir veya ilçe bulunamadı"}
            )

        data = fetch_prayer_times(district_id)
        if not data:
            return JSONResponse(
                status_code=500,
                content={"status": False, "error": "Vakitler alınamadı"}
            )

        return {"status": True, "city": city, "district": district, "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": False, "error": str(e)})
