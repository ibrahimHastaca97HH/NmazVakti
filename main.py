from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import unicodedata

app = Flask(__name__)

with open("districts.json", "r", encoding="utf-8") as f:
    district_data = json.load(f)

def normalize_string(string):
    string = unicodedata.normalize("NFKD", string).encode("ASCII", "ignore").decode("utf-8")
    return string.lower().replace("ı", "i").replace("ç", "c").replace("ş", "s")\
        .replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace(" ", "").replace("-", "")

@app.route("/")
def index():
    return jsonify({
        "message": "Namaz Vakti API",
        "endpoints": {
            "/vakitler?city=...&district=...": "İl ve ilçe için namaz vakitlerini getirir.",
            "/sehirler": "Tüm şehirleri listeler.",
            "/ilceler?city=...": "Belirtilen şehir için ilçeleri listeler."
        }
    })

@app.route("/sehirler")
def get_cities():
    cities = list(district_data.keys())
    return jsonify({
        "status": True,
        "cities": cities
    })

@app.route("/ilceler")
def get_districts():
    city = request.args.get("city")
    if not city:
        return jsonify({"status": False, "error": "Şehir belirtilmedi."})
    
    normalized_city = normalize_string(city)
    if normalized_city not in district_data:
        return jsonify({"status": False, "error": "Şehir bulunamadı."})
    
    districts = list(district_data[normalized_city].keys())
    return jsonify({
        "status": True,
        "city": normalized_city,
        "districts": districts
    })

@app.route("/vakitler")
def get_prayer_times():
    city = request.args.get("city")
    district = request.args.get("district")

    if not city or not district:
        return jsonify({"status": False, "error": "Şehir ve ilçe gerekli."})

    normalized_city = normalize_string(city)
    normalized_district = normalize_string(district)

    if normalized_city not in district_data or \
       normalized_district not in district_data[normalized_city]:
        return jsonify({"status": False, "error": "Şehir veya ilçe bulunamadı"})

    district_id = district_data[normalized_city][normalized_district]
    url = f"https://namazvakitleri.diyanet.gov.tr/tr-TR/{district_id}/vakitler"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    times = {}
    try:
        for row in soup.select("tbody tr"):
            tds = row.find_all("td")
            if len(tds) >= 7:
                date = tds[0].text.strip()
                times[date] = {
                    "imsak": tds[1].text.strip(),
                    "gunes": tds[2].text.strip(),
                    "ogle": tds[3].text.strip(),
                    "ikindi": tds[4].text.strip(),
                    "aksam": tds[5].text.strip(),
                    "yatsi": tds[6].text.strip(),
                }
    except Exception as e:
        return jsonify({"status": False, "error": str(e)})

    today = datetime.now().strftime("%d.%m.%Y")
    return jsonify({
        "status": True,
        "location": {
            "city": city,
            "district": district
        },
        "date": today,
        "times": times.get(today, {})
    })

if __name__ == "__main__":
    app.run(debug=True)
