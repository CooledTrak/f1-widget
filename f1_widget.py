import requests
import json
from datetime import datetime, timedelta, timezone
from dateutil import parser

# --- BEÁLLÍTÁSOK ---
WEATHER_API_KEY = "84352f72e1c7846365290f1afb251a4c"
JSON_OUTPUT_PATH = "f1_widget_data.json"

# Fix dátumok (Szezon határok)
SEASON_START = datetime(2026, 3, 6, tzinfo=timezone.utc) 
LAST_SEASON_END = datetime(2025, 12, 8, tzinfo=timezone.utc) 

# Pályarajzok (Képek)
TRACK_MAPS = {
    "albert_park": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Australia_Circuit.png.transform/8col/image.png",
    "bahrain": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Bahrain_Circuit.png.transform/8col/image.png",
    "jeddah": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Saudi_Arabia_Circuit.png.transform/8col/image.png",
    "suzuka": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Japan_Circuit.png.transform/8col/image.png",
    "shanghai": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/China_Circuit.png.transform/8col/image.png",
    "miami": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Miami_Circuit.png.transform/8col/image.png",
    "imola": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Emilia_Romagna_Circuit.png.transform/8col/image.png",
    "monaco": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Monaco_Circuit.png.transform/8col/image.png",
    "catalunya": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Spain_Circuit.png.transform/8col/image.png",
    "villeneuve": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Canada_Circuit.png.transform/8col/image.png",
    "red_bull_ring": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Austria_Circuit.png.transform/8col/image.png",
    "silverstone": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Great_Britain_Circuit.png.transform/8col/image.png",
    "hungaroring": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Hungary_Circuit.png.transform/8col/image.png",
    "spa": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Belgium_Circuit.png.transform/8col/image.png",
    "zandvoort": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Netherlands_Circuit.png.transform/8col/image.png",
    "monza": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Italy_Circuit.png.transform/8col/image.png",
    "baku": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Baku_Circuit.png.transform/8col/image.png",
    "marina_bay": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Singapore_Circuit.png.transform/8col/image.png",
    "americas": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/USA_Circuit.png.transform/8col/image.png",
    "rodriguez": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Mexico_Circuit.png.transform/8col/image.png",
    "interlagos": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Brazil_Circuit.png.transform/8col/image.png",
    "vegas": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Las_Vegas_Circuit.png.transform/8col/image.png",
    "losail": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Qatar_Circuit.png.transform/8col/image.png",
    "yas_marina": "https://media.formula1.com/content/dam/fom-website/2018-redesign-assets/Circuit%20maps%2016x9/Abu_Dhabi_Circuit.png.transform/8col/image.png"
}

# Pálya Specifikációk (Körszám | Hossz | Rekord)
TRACK_SPECS = {
    "albert_park": "58 KÖR | 5.278 KM | 1:19.813",
    "bahrain": "57 KÖR | 5.412 KM | 1:31.447",
    "jeddah": "50 KÖR | 6.174 KM | 1:30.734",
    "suzuka": "53 KÖR | 5.807 KM | 1:30.983",
    "shanghai": "56 KÖR | 5.451 KM | 1:32.238",
    "miami": "57 KÖR | 5.412 KM | 1:29.708",
    "imola": "63 KÖR | 4.909 KM | 1:15.484",
    "monaco": "78 KÖR | 3.337 KM | 1:12.909",
    "catalunya": "66 KÖR | 4.657 KM | 1:16.330",
    "villeneuve": "70 KÖR | 4.361 KM | 1:13.078",
    "red_bull_ring": "71 KÖR | 4.318 KM | 1:05.619",
    "silverstone": "52 KÖR | 5.891 KM | 1:27.097",
    "hungaroring": "70 KÖR | 4.381 KM | 1:16.627",
    "spa": "44 KÖR | 7.004 KM | 1:46.286",
    "zandvoort": "72 KÖR | 4.259 KM | 1:11.097",
    "monza": "53 KÖR | 5.793 KM | 1:21.046",
    "baku": "51 KÖR | 6.003 KM | 1:43.009",
    "marina_bay": "62 KÖR | 4.940 KM | 1:35.867",
    "americas": "56 KÖR | 5.513 KM | 1:36.169",
    "rodriguez": "71 KÖR | 4.304 KM | 1:17.774",
    "interlagos": "71 KÖR | 4.309 KM | 1:10.540",
    "vegas": "50 KÖR | 6.201 KM | 1:35.490",
    "losail": "57 KÖR | 5.419 KM | 1:24.319",
    "yas_marina": "58 KÖR | 5.281 KM | 1:26.103"
}

def get_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"HIBA: {e}")
        return None

# Részletes időjárás lekérése (Hőfok, Leírás, Ikon, Szél, Pára)
def get_weather_detailed(lat, lon):
    if not WEATHER_API_KEY: return "", "", "", "", ""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=hu"
    data = get_json(url)
    if data:
        temp = f"{round(data['main']['temp'])}°C"
        desc = data['weather'][0]['description'].capitalize()
        icon = data['weather'][0]['icon']
        wind = f"{round(data['wind']['speed'] * 3.6)} km/h" # m/s átváltása km/h-ra
        humidity = f"{data['main']['humidity']}%"
        return temp, desc, icon, wind, humidity
    return "", "", "", "", ""

def format_date_range(start_date, end_date):
    months = ["JAN", "FEB", "MÁRC", "ÁPR", "MÁJ", "JÚN", "JÚL", "AUG", "SZEP", "OKT", "NOV", "DEC"]
    s_month = months[start_date.month - 1]
    e_month = months[end_date.month - 1]
    if s_month == e_month:
        return f"{s_month} {start_date.day} - {end_date.day}"
    return f"{s_month} {start_date.day} - {e_month} {end_date.day}"

def main():
    # Alapértelmezett üres adatszerkezet
    widget_data = {
        "status_title": "F1 WIDGET", 
        "location": "",
        "race_dates": "",
        "track_info": "",
        # Időjárás mezők (Race Mode-hoz)
        "w_temp": "", "w_desc": "", "w_icon": "", "w_wind": "", "w_hum": "",
        # Státusz és Módok
        "status_text": "",
        "is_weekend_mode": 0, # 0=Visszaszámláló, 1=Race Dashboard
        "is_live": 0,
        "progress": 33,
        # Tartalom
        "schedule": "",
        "track_map": "",
        "podium_title": "",
        # Pilóták (Kód, Pont)
        "d1_c": "", "d1_p": "", "d2_c": "", "d2_p": "", "d3_c": "", "d3_p": "",
        # Konstruktőrök (Kód, Pont)
        "c1_c": "", "c1_p": "", "c2_c": "", "c2_p": "", "c3_c": "", "c3_p": ""
    }

    # 1. KÖVETKEZŐ FUTAM ADATOK
    next_data = get_json("https://api.jolpi.ca/ergast/f1/current/next.json")
    if not next_data:
        with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(widget_data, f)
        return

    try:
        race = next_data['MRData']['RaceTable']['Races'][0]
        race_name = race['raceName'].replace("Grand Prix", "GP")
        circuit_id = race['Circuit']['circuitId']
        circuit_name = race['Circuit']['Location']['locality']
        
        # Kép és Specifikáció betöltése
        if circuit_id in TRACK_MAPS: widget_data['track_map'] = TRACK_MAPS[circuit_id]
        if circuit_id in TRACK_SPECS: widget_data['track_info'] = TRACK_SPECS[circuit_id]
        else: widget_data['track_info'] = "ADATOK HAMAROSAN..."

        now = datetime.now(timezone.utc)
        
        # --- MENETREND FELDOLGOZÁSA ---
        sessions = []
        def add_session(name, date_str, time_str, duration_min):
            start = parser.parse(f"{date_str} {time_str}")
            end = start + timedelta(minutes=duration_min)
            sessions.append({"name": name, "start": start, "end": end})

        add_session("Futam", race['date'], race['time'], 120)
        if 'Qualifying' in race: add_session("Időmérő", race['Qualifying']['date'], race['Qualifying']['time'], 60)
        if 'FirstPractice' in race: add_session("1. Edzés", race['FirstPractice']['date'], race['FirstPractice']['time'], 60)
        if 'SecondPractice' in race: add_session("2. Edzés", race['SecondPractice']['date'], race['SecondPractice']['time'], 60)
        if 'ThirdPractice' in race: add_session("3. Edzés", race['ThirdPractice']['date'], race['ThirdPractice']['time'], 60)
        if 'Sprint' in race: add_session("Sprint", race['Sprint']['date'], race['Sprint']['time'], 60)
        if 'SprintQualifying' in race: add_session("Sprint Q", race['SprintQualifying']['date'], race['SprintQualifying']['time'], 45)

        sessions.sort(key=lambda x: x["start"])
        first_session = sessions[0]["start"]
        last_session = sessions[-1]["end"]
        
        # Pontos hétvége dátumok (Péntek-Vasárnap) a Race Mode-hoz
        race_date = parser.parse(race['date']).date()
        friday_date = race_date - timedelta(days=2)
        today = now.date()

        # Adatok kitöltése
        widget_data['status_title'] = race_name.upper()
        widget_data['location'] = circuit_name.upper()
        widget_data['race_dates'] = format_date_range(first_session, last_session) + f", {first_session.year}"

        # --- WEEKEND MODE LOGIKA ---
        # Csak akkor aktív, ha a MAI nap Péntek, Szombat vagy Vasárnap ÉS ez a konkrét versenyhétvége
        if friday_date <= today <= race_date:
            widget_data['is_weekend_mode'] = 1
            # Részletes időjárás lekérése
            widget_data['w_temp'], widget_data['w_desc'], widget_data['w_icon'], widget_data['w_wind'], widget_data['w_hum'] = get_weather_detailed(race['Circuit']['Location']['lat'], race['Circuit']['Location']['long'])
        else:
            widget_data['is_weekend_mode'] = 0
            # Üres időjárás (hogy a KWGT helyit használjon)
            widget_data['w_temp'], widget_data['w_desc'], widget_data['w_icon'], _, _ = get_weather_detailed(race['Circuit']['Location']['lat'], race['Circuit']['Location']['long'])
            # Töröljük a részletes adatokat, ha nem weekend mode, hogy ne zavarjon be
            if widget_data['is_weekend_mode'] == 0:
                 widget_data['w_icon'] = "" 

        # --- VISSZASZÁMLÁLÓ & LIVE STATUS ---
        for s in sessions:
            if s["start"] <= now <= s["end"]:
                widget_data['is_live'] = 1
                widget_data['status_text'] = f"LIVE: {s['name'].upper()}"
                break

        if widget_data['is_live'] == 0:
            time_left = first_session - now
            days = time_left.days
            if days < 0: days = 0
            
            if days == 0: # Ma kezdődik (de még nincs live)
                hours, rem = divmod(time_left.seconds, 3600)
                mins, _ = divmod(rem, 60)
                widget_data['status_text'] = f"KEZDÉS: {hours}ó {mins}p"
            else:
                widget_data['status_text'] = f"{days} NAP VAN HÁTRA"

        # --- MENETREND GENERÁLÁS (SZÍNEZETT) ---
        schedule_text = ""
        for s in sessions:
            local_time = s["start"].astimezone()
            day_name = ["Hé", "Ke", "Sze", "Cs", "Pé", "Szo", "Va"][local_time.weekday()]
            time_str = local_time.strftime("%H:%M")
            
            if now > s["end"]: 
                # ELMÚLT: Halvány szürke
                schedule_text += f"[c=#70FFFFFF]{day_name} {time_str} | {s['name']}[/c]\n"
            elif s["start"] <= now <= s["end"]: 
                # ÉLŐ: Zöld és Félkövér
                schedule_text += f"[c=#00FF00][b]{day_name} {time_str} | {s['name']}[/b][/c]\n"
            else:
                # JÖVŐ: Fehér
                schedule_text += f"{day_name} {time_str} | {s['name']}\n"
        widget_data['schedule'] = schedule_text.strip()

        # --- BAJNOKSÁG ADATOK (FALLBACK-KEL) ---
        
        # 1. Konstruktőrök
        try:
            c_data = get_json("https://api.jolpi.ca/ergast/f1/current/constructorStandings.json")
            if not c_data or not c_data['MRData']['StandingsTable']['StandingsLists']:
                 c_data = get_json(f"https://api.jolpi.ca/ergast/f1/{now.year-1}/constructorStandings.json")
            
            if c_data and c_data['MRData']['StandingsTable']['StandingsLists']:
                c_res = c_data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
                # Top 3
                if len(c_res) > 0: widget_data['c1_c'], widget_data['c1_p'] = c_res[0]['Constructor']['name'][:3].upper(), c_res[0]['points']
                if len(c_res) > 1: widget_data['c2_c'], widget_data['c2_p'] = c_res[1]['Constructor']['name'][:3].upper(), c_res[1]['points']
                if len(c_res) > 2: widget_data['c3_c'], widget_data['c3_p'] = c_res[2]['Constructor']['name'][:3].upper(), c_res[2]['points']
        except Exception as e: print(f"Konstruktőr hiba: {e}")

        # 2. Pilóták
        try:
            d_data = get_json("https://api.jolpi.ca/ergast/f1/current/driverStandings.json")
            if not d_data or not d_data['MRData']['StandingsTable']['StandingsLists']:
                 d_data = get_json(f"https://api.jolpi.ca/ergast/f1/{now.year-1}/driverStandings.json")
            
            if d_data and d_data['MRData']['StandingsTable']['StandingsLists']:
                d_res = d_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
                # Top 3
                if len(d_res) > 0: widget_data['d1_c'], widget_data['d1_p'] = d_res[0]['Driver']['code'], d_res[0]['points']
                if len(d_res) > 1: widget_data['d2_c'], widget_data['d2_p'] = d_res[1]['Driver']['code'], d_res[1]['points']
                if len(d_res) > 2: widget_data['d3_c'], widget_data['d3_p'] = d_res[2]['Driver']['code'], d_res[2]['points']
        except Exception as e: print(f"Pilóta hiba: {e}")

        # --- PROGRESS BAR ---
        last_race_end = LAST_SEASON_END # Default
        # Próbáljuk megkeresni az előző futamot
        last_race_data = get_json("https://api.jolpi.ca/ergast/f1/current/last.json")
        if last_race_data:
            try:
                lr = last_race_data['MRData']['RaceTable']['Races'][0]
                last_race_end = parser.parse(f"{lr['date']} {lr['time']}")
            except: pass

        race_start = next((s["start"] for s in sessions if s["name"] == "Futam"), None)
        calc_progress = 0
        if race_start:
            total_duration = (race_start - last_race_end).total_seconds()
            elapsed = (now - last_race_end).total_seconds()
            if total_duration > 0:
                calc_progress = int(max(0, min(100, (elapsed / total_duration) * 100)))
        widget_data['progress'] = calc_progress

    except Exception as e:
        widget_data['status_text'] = f"Hiba: {e}"
        print(f"Végzetes hiba: {e}")

    # JSON MENTÉS
    with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(widget_data, f)
    print("F1 Adatok sikeresen frissítve!")

if __name__ == "__main__":
    main()
