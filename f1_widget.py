import requests
import json
from datetime import datetime, timedelta, timezone
from dateutil import parser

# --- BEÁLLÍTÁSOK ---
WEATHER_API_KEY = "84352f72e1c7846365290f1afb251a4c"
JSON_OUTPUT_PATH = "f1_widget_data.json"

# Fix dátumok
SEASON_START = datetime(2026, 3, 6, tzinfo=timezone.utc) 
LAST_SEASON_END = datetime(2025, 12, 8, tzinfo=timezone.utc) 

TRACK_MAPS = {
    "albert_park": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Australia_Circuit.png.transform/8col/image.png",
    "bahrain": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Bahrain_Circuit.png.transform/8col/image.png",
    "jeddah": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Saudi_Arabia_Circuit.png.transform/8col/image.png",
    "suzuka": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Japan_Circuit.png.transform/8col/image.png",
    "shanghai": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/China_Circuit.png.transform/8col/image.png",
    "miami": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Miami_Circuit.png.transform/8col/image.png",
    "hungaroring": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Hungary_Circuit.png.transform/8col/image.png",
}

# Pálya infók: Körök | Hossz | Rekord
TRACK_SPECS = {
    "albert_park": "58 KÖR | 5.278 KM | 1:19.813",
    "bahrain": "57 KÖR | 5.412 KM | 1:31.447",
    "jeddah": "50 KÖR | 6.174 KM | 1:30.734",
    "suzuka": "53 KÖR | 5.807 KM | 1:30.983",
    "shanghai": "56 KÖR | 5.451 KM | 1:32.238",
    "miami": "57 KÖR | 5.412 KM | 1:29.708",
    "hungaroring": "70 KÖR | 4.381 KM | 1:16.627",
}

def get_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e: return None

def get_weather_detailed(lat, lon):
    if not WEATHER_API_KEY: return "", "", "", ""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=hu"
    data = get_json(url)
    if data:
        temp = f"{round(data['main']['temp'])}°C"
        desc = data['weather'][0]['description'].capitalize()
        icon = data['weather'][0]['icon']
        wind = f"{round(data['wind']['speed'] * 3.6)} km/h" # m/s -> km/h
        humidity = f"{data['main']['humidity']}%"
        return temp, desc, icon, wind, humidity
    return "", "", "", "", ""

def format_date_range(start_date, end_date):
    months = ["JAN", "FEB", "MÁRC", "ÁPR", "MÁJ", "JÚN", "JÚL", "AUG", "SZEP", "OKT", "NOV", "DEC"]
    s_month = months[start_date.month - 1]
    e_month = months[end_date.month - 1]
    if s_month == e_month: return f"{s_month} {start_date.day} - {end_date.day}"
    return f"{s_month} {start_date.day} - {e_month} {end_date.day}"

def main():
    widget_data = {
        "status_title": "F1 WIDGET", 
        "location": "",
        "race_dates": "",
        "track_info": "",
        # Időjárás mezők
        "w_temp": "", "w_desc": "", "w_icon": "", "w_wind": "", "w_hum": "",
        # Státusz
        "status_text": "",
        "progress": 33,
        "schedule": "",
        "track_map": "",
        "is_weekend_mode": 0, # EZ A KULCS! (0 = Alap, 1 = Verseny Mód)
        "podium_title": "",
        "d1_c": "", "d1_p": "", "d2_c": "", "d2_p": "", "d3_c": "", "d3_p": "",
        "c1_c": "", "c1_p": "", "c2_c": "", "c2_p": "", "c3_c": "", "c3_p": ""
    }

    next_data = get_json("https://api.jolpi.ca/ergast/f1/current/next.json")
    if not next_data:
        with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(widget_data, f)
        return

    try:
        race = next_data['MRData']['RaceTable']['Races'][0]
        race_name = race['raceName'].replace("Grand Prix", "GP")
        circuit_id = race['Circuit']['circuitId']
        circuit_name = race['Circuit']['Location']['locality']
        
        if circuit_id in TRACK_MAPS: widget_data['track_map'] = TRACK_MAPS[circuit_id]
        if circuit_id in TRACK_SPECS: widget_data['track_info'] = TRACK_SPECS[circuit_id]
        else: widget_data['track_info'] = "ADATOK HAMAROSAN..."

        now = datetime.now(timezone.utc)
        
        # --- MENETREND ---
        sessions = []
        def add_session(name, date_str, time_str, duration_min):
            start = parser.parse(f"{date_str} {time_str}")
            end = start + timedelta(minutes=duration_min)
            sessions.append({"name": name, "start": start, "end": end})

        add_session("Futam", race['date'], race['time'], 120)
        if 'Qualifying' in race: add_session("Időmérő", race['Qualifying']['date'], race['Qualifying']['time'], 60)
        # ... (Többi edzés hozzáadása ha szükséges, a kód rövidítése miatt kihagyva, de maradhat a te verziódban) ...
        # A lényeg a dátumok meghatározása:
        
        first_session_date = parser.parse(f"{race['date']} {race['time']}") - timedelta(days=2) # Péntek becslése
        # (A pontos session lista jobb lenne, de a logika a dátumtartomány)
        
        # PROFI DÁTUM TARTOMÁNY (Péntek 00:00 - Vasárnap 23:59)
        # Az API 'date' mezője a VASÁRNAPI futam.
        race_date = parser.parse(race['date']).date()
        friday_date = race_date - timedelta(days=2)
        
        # Aktuális dátum (csak a nap)
        today = now.date()

        # --- WEEKEND MODE LOGIKA ---
        # Csak akkor legyen aktív, ha a MAI nap Péntek, Szombat vagy Vasárnap ÉS ez a versenyhétvége
        if friday_date <= today <= race_date:
            widget_data['is_weekend_mode'] = 1
            # Ha versenyhétvége van, kérjük le a részletes időjárást
            widget_data['w_temp'], widget_data['w_desc'], widget_data['w_icon'], widget_data['w_wind'], widget_data['w_hum'] = get_weather_detailed(race['Circuit']['Location']['lat'], race['Circuit']['Location']['long'])
        else:
            widget_data['is_weekend_mode'] = 0
            # Ha nincs verseny, sima időjárás (csak az ikonhoz, ha kell)
            widget_data['w_temp'], widget_data['w_desc'], widget_data['w_icon'], _, _ = get_weather_detailed(race['Circuit']['Location']['lat'], race['Circuit']['Location']['long'])

        # Adatok kitöltése
        widget_data['status_title'] = race_name.upper()
        widget_data['location'] = circuit_name.upper()
        widget_data['race_dates'] = format_date_range(friday_date, race_date) + f", {race_date.year}"

        # Status text (Visszaszámláló vagy LIVE)
        time_left = parser.parse(f"{race['date']} {race['time']").replace(tzinfo=timezone.utc) - now
        days = time_left.days
        if days < 0: widget_data['status_text'] = "FUTAM VÉGE"
        elif days == 0: widget_data['status_text'] = "MA VAN A FUTAM!"
        else: widget_data['status_text'] = f"{days} NAP VAN HÁTRA"

        # ... (A Menetrend generálás, Konstruktőrök, Pilóták maradhat a régi kódodból!) ...
        
        # Progress
        # ... (Maradhat a régi) ...

    except Exception as e: print(e)

    with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(widget_data, f)

if __name__ == "__main__":
    main()
