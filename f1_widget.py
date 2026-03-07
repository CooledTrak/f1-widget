import requests
import json
import traceback
import os
from datetime import datetime, timedelta, timezone
from dateutil import parser, tz

# --- BEÁLLÍTÁSOK ---
WEATHER_API_KEY = "84352f72e1c7846365290f1afb251a4c"
JSON_OUTPUT_PATH = "f1_widget_data.json"

# KEDVENC CSAPAT SZÍNE
MY_TEAM_COLOR = "#FF1801" 

# SZEZON HATÁROK (2026)
LAST_SEASON_END = datetime(2025, 12, 8, 14, 0, 0, tzinfo=timezone.utc)
SEASON_START_2026 = datetime(2026, 3, 6, 4, 0, 0, tzinfo=timezone.utc)

# SAJÁT KÉPEK
BASE_REPO_URL = "https://raw.githubusercontent.com/CooledTrak/f1-widget/main"
IMG_HARD = f"{BASE_REPO_URL}/pirellif1pzerohard2026.png"
IMG_MED = f"{BASE_REPO_URL}/pirellif1pzeromedium2026.png"
IMG_SOFT = f"{BASE_REPO_URL}/pirellif1pzerosoft2026.png"

# PÁLYA RAJZOK ÉS ADATOK (NE FELEJTSD EL A SAJÁTODDAL KIEGÉSZÍTENI HA RÖVIDÍTVE VAN!)
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

TYRE_ALLOCATIONS = {
    "bahrain": ["C1", "C2", "C3"], "jeddah": ["C2", "C3", "C4"], "albert_park": ["C3", "C4", "C5"],
    "suzuka": ["C1", "C2", "C3"], "shanghai": ["C2", "C3", "C4"], "miami": ["C2", "C3", "C4"],
    "imola": ["C3", "C4", "C5"], "monaco": ["C4", "C5", "C6"], "catalunya": ["C1", "C2", "C3"],
    "villeneuve": ["C3", "C4", "C5"], "red_bull_ring": ["C3", "C4", "C5"], "silverstone": ["C1", "C2", "C3"],
    "hungaroring": ["C3", "C4", "C5"], "spa": ["C2", "C3", "C4"], "zandvoort": ["C1", "C2", "C3"],
    "monza": ["C3", "C4", "C5"], "baku": ["C3", "C4", "C5"], "marina_bay": ["C4", "C5", "C6"],
    "americas": ["C2", "C3", "C4"], "rodriguez": ["C3", "C4", "C5"], "interlagos": ["C2", "C3", "C4"],
    "vegas": ["C3", "C4", "C5"], "losail": ["C1", "C2", "C3"], "yas_marina": ["C3", "C4", "C5"]
}

def get_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception: return None

def format_date_range(start_date, end_date):
    months = ["JAN", "FEB", "MÁRC", "ÁPR", "MÁJ", "JÚN", "JÚL", "AUG", "SZEP", "OKT", "NOV", "DEC"]
    if start_date.month == end_date.month: 
        return f"{months[start_date.month - 1]} {start_date.day} - {end_date.day}"
    return f"{months[start_date.month - 1]} {start_date.day} - {months[end_date.month - 1]} {end_date.day}"

def main():
    print("--- ADATGYŰJTÉS INDÍTÁSA ---")

    # MEGLÉVŐ ADATOK BEOLVASÁSA (MEMÓRIA)
    existing_data = {}
    if os.path.exists(JSON_OUTPUT_PATH):
        try:
            with open(JSON_OUTPUT_PATH, 'r') as f:
                existing_data = json.load(f)
        except Exception as e:
            print("Nem sikerült beolvasni a régi JSON-t:", e)

    widget_data = {
        "status_title": "F1 WIDGET", "location": "", "race_dates": "", "track_info": "",
        "w_temp": "", "w_desc": "", "w_icon": "", "w_wind": "", "w_hum": "",
        "status_text": "ADATOK...", "is_weekend_mode": 0, "is_live": 0, "progress": 0,
        "schedule": "", "track_map": "", "podium_title": "",
        "weekend_progress": 0.0,
        "bar_color": MY_TEAM_COLOR,
        "tyre_h": "C1", "tyre_m": "C2", "tyre_s": "C3",
        "tyre_img_h": IMG_HARD, "tyre_img_m": IMG_MED, "tyre_img_s": IMG_SOFT,
        "d1_c": "VER", "d1_p": "0", "d2_c": "NOR", "d2_p": "0", "d3_c": "HAM", "d3_p": "0",
        "c1_c": "MCL", "c1_p": "0", "c2_c": "RBR", "c2_p": "0", "c3_c": "FER", "c3_p": "0"
    }

    try:
        next_data = get_json("https://api.jolpi.ca/ergast/f1/current/next.json")
        if not next_data:
            if existing_data:
                with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(existing_data, f)
            return

        race = next_data['MRData']['RaceTable']['Races'][0]
        circuit_id = race['Circuit']['circuitId']
        
        widget_data['status_title'] = race['raceName'].replace("Grand Prix", "GP").upper()
        widget_data['location'] = race['Circuit']['Location']['locality'].upper()

        if circuit_id in TRACK_MAPS: widget_data['track_map'] = TRACK_MAPS[circuit_id]
        if circuit_id in TRACK_SPECS: widget_data['track_info'] = TRACK_SPECS[circuit_id]
        if circuit_id in TYRE_ALLOCATIONS:
            alloc = TYRE_ALLOCATIONS[circuit_id]
            widget_data['tyre_h'], widget_data['tyre_m'], widget_data['tyre_s'] = alloc[0], alloc[1], alloc[2]
        
        now = datetime.now(timezone.utc)
        sessions = []
        
        def add_session(name, date_str, time_str, duration_min):
            clean_time = time_str.replace("Z", "")
            start = parser.parse(f"{date_str} {clean_time}").replace(tzinfo=timezone.utc)
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
        
        widget_data['race_dates'] = format_date_range(first_session, last_session) + f", {first_session.year}"
        
        # WEEKEND PROGRESS
        weekend_duration = (last_session - first_session).total_seconds()
        time_since_start = (now - first_session).total_seconds()
        
        if now < first_session:
            widget_data['weekend_progress'] = 0.0
        elif now > last_session:
            widget_data['weekend_progress'] = 100.0
        else:
            if weekend_duration > 0:
                prog = (time_since_start / weekend_duration) * 100
                widget_data['weekend_progress'] = round(max(0.0, min(100.0, float(prog))), 2)

        # MENETREND SZÍNEZÉS (KÖZÉP-EURÓPAI IDŐZÓNA)
        schedule_text = ""
        budapest_tz = tz.gettz('Europe/Budapest')
        
        for s in sessions:
            local_time = s["start"].astimezone(budapest_tz)
            day_name = ["Hé", "Ke", "Sze", "Cs", "Pé", "Szo", "Va"][local_time.weekday()]
            time_str = local_time.strftime("%H:%M")
            
            if now > s["end"]: 
                schedule_text += f"[c=#70FFFFFF]{day_name} {time_str} | {s['name']}[/c]\n"
            elif s["start"] <= now <= s["end"]: 
                schedule_text += f"[c=#00FF00][b]{day_name} {time_str} | {s['name']}[/b][/c]\n"
            else: 
                schedule_text += f"{day_name} {time_str} | {s['name']}\n"
        
        widget_data['schedule'] = schedule_text.strip()
        
        # IDŐJÁRÁS (AGRESSZÍV MEMÓRIÁVAL)
        race_date = parser.parse(race['date']).date()
        friday_date = race_date - timedelta(days=2)
        today = now.date()

        def get_weather():
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={race['Circuit']['Location']['lat']}&lon={race['Circuit']['Location']['long']}&appid={WEATHER_API_KEY}&units=metric&lang=hu"
            data = get_json(url)
            
            # 1. Ha van sikeres friss adat
            if data and 'main' in data:
                return (
                    f"{round(data['main']['temp'])}°C",
                    data['weather'][0]['description'].capitalize(),
                    data['weather'][0]['icon'],
                    f"{round(data['wind']['speed'] * 3.6)} km/h",
                    f"{data['main']['humidity']}%"
                )
            
            # 2. Ha az API hibát dobott, de van régi adat a memóriában
            mem_temp = existing_data.get('w_temp', '')
            if mem_temp != "" and mem_temp != "--°C":
                return (
                    mem_temp,
                    existing_data.get('w_desc', ''),
                    existing_data.get('w_icon', ''),
                    existing_data.get('w_wind', ''),
                    existing_data.get('w_hum', '')
                )
            
            # 3. Ha semmi nem jött össze (hogy ne tűnjön el a widget szövege)
            return ("--°C", "Adatfrissítés...", "", "-- km/h", "--%")

        if friday_date <= today <= race_date:
            widget_data['is_weekend_mode'] = 1
            widget_data['w_temp'], widget_data['w_desc'], widget_data['w_icon'], widget_data['w_wind'], widget_data['w_hum'] = get_weather()
        else:
            widget_data['is_weekend_mode'] = 0
            widget_data['w_temp'], widget_data['w_desc'], widget_data['w_icon'], widget_data['w_wind'], widget_data['w_hum'] = get_weather()

        # SZEZON PROGRESS
        season_start_point = first_session
        if now < season_start_point:
            start_date = LAST_SEASON_END
            end_date = season_start_point
            total_seconds = (end_date - start_date).total_seconds()
            elapsed_seconds = (now - start_date).total_seconds()
            if total_seconds > 0:
                calc_progress = int((elapsed_seconds / total_seconds) * 100)
            else:
                calc_progress = 0
            
            days_left = (season_start_point - now).days
            widget_data['status_text'] = f"{days_left} NAP VAN HÁTRA"
        else:
            calc_progress = 50
            widget_data['status_text'] = "VERSENYHÉTVÉGE"
        
        widget_data['progress'] = max(0, min(100, calc_progress))
        
        # BAJNOKSÁG
        try:
            d_data = get_json("https://api.jolpi.ca/ergast/f1/current/driverStandings.json")
            if not d_data or not d_data['MRData']['StandingsTable']['StandingsLists']:
                 d_data = get_json(f"https://api.jolpi.ca/ergast/f1/{now.year-1}/driverStandings.json")
            if d_data and d_data['MRData']['StandingsTable']['StandingsLists']:
                d_res = d_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
                if len(d_res) > 0: widget_data['d1_c'], widget_data['d1_p'] = d_res[0]['Driver']['code'], d_res[0]['points']
                if len(d_res) > 1: widget_data['d2_c'], widget_data['d2_p'] = d_res[1]['Driver']['code'], d_res[1]['points']
                if len(d_res) > 2: widget_data['d3_c'], widget_data['d3_p'] = d_res[2]['Driver']['code'], d_res[2]['points']
        except Exception as e: pass

        try:
            c_data = get_json("https://api.jolpi.ca/ergast/f1/current/constructorStandings.json")
            if not c_data or not c_data['MRData']['StandingsTable']['StandingsLists']:
                 c_data = get_json(f"https://api.jolpi.ca/ergast/f1/{now.year-1}/constructorStandings.json")
            if c_data and c_data['MRData']['StandingsTable']['StandingsLists']:
                c_res = c_data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
                if len(c_res) > 0: widget_data['c1_c'], widget_data['c1_p'] = c_res[0]['Constructor']['name'][:3].upper(), c_res[0]['points']
                if len(c_res) > 1: widget_data['c2_c'], widget_data['c2_p'] = c_res[1]['Constructor']['name'][:3].upper(), c_res[1]['points']
                if len(c_res) > 2: widget_data['c3_c'], widget_data['c3_p'] = c_res[2]['Constructor']['name'][:3].upper(), c_res[2]['points']
        except Exception as e: pass

    except Exception as e:
        traceback.print_exc()

    with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(widget_data, f)
    print("Mentés kész.")

if __name__ == "__main__":
    main()
