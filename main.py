from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

API_BASE_URL = "https://awqatsalah.diyanet.gov.tr/api"

def get_city_id(city_name: str):
    response = requests.get(f"{API_BASE_URL}/Place/Cities")
    if response.status_code != 200:
        return None
    cities = response.json()
    for city in cities:
        if city["name"].lower() == city_name.lower():
            return city["id"]
    return None

def get_district_id(city_id: int, district_name: str):
    response = requests.get(f"{API_BASE_URL}/Place/Districts/{city_id}")
    if response.status_code != 200:
        return None
    districts = response.json()
    for district in districts:
        if district["name"].lower() == district_name.lower():
            return district["id"]
    return None

def fetch_prayer_times(district_id: int):
    response = requests.get(f"{API_BASE_URL}/PrayerTime/Daily/{district_id}")
    if response.status_code != 200:
        return None
    return response.json()

@app.get("/")
def root():
    return {"message": "Ezan API çalışıyor"}

@app.get("/vakitler")
def get_vakitler(
    city: str = Query(..., description="Şehir adı"),
    district: str = Query(..., description="İlçe adı")
):
    try:
        city_id = get_city_id(city)
        if not city_id:
            return JSONResponse(status_code=404, content={"status": False, "error": "Şehir bulunamadı"})

        district_id = get_district_id(city_id, district)
        if not district_id:
            return JSONResponse(status_code=404, content={"status": False, "error": "İlçe bulunamadı"})

        data = fetch_prayer_times(district_id)
        if not data:
            return JSONResponse(status_code=500, content={"status": False, "error": "Veri alınamadı"})

        return {"status": True, "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": False, "error": str(e)})
