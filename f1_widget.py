import requests
import json
import traceback
from datetime import datetime, timedelta, timezone
from dateutil import parser

# --- BEÁLLÍTÁSOK ---
WEATHER_API_KEY = "84352f72e1c7846365290f1afb251a4c"
JSON_OUTPUT_PATH = "f1_widget_data.json"

# Fix dátumok
LAST_SEASON_END = datetime(2025, 12, 8, 14, 0, 0, tzinfo=timezone.utc)
SEASON_START_2026 = datetime(2026, 3, 6, 4, 0, 0, tzinfo=timezone.utc)

# ÚJ: BIZTOS KÉP LINKEK (Ezeket könnyebben betölti a KWGT)
IMG_HARD = "https://i.imgur.com/7Z7Z1Zt.png"   # Fehér
IMG_MED = "https://i.imgur.com/3Z7Z1Zt.png"    # Sárga
IMG_SOFT = "https://i.imgur.com/e4J6a2S.png"    # Piros

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
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except: return None

def format_date_range(start, end):
    months = ["JAN", "FEB", "MÁRC", "ÁPR", "MÁJ", "JÚN", "JÚL", "AUG", "SZEP", "OKT", "NOV", "DEC"]
    if start.month == end.month: return f"{months[start.month-1]} {start.day} - {end.day}"
    return f"{months[start.month-1]} {start.day} - {months[end.month-1]} {end.day}"

def main():
    # ALAP ADATOK
    data = {
        "status_title": "F1 WIDGET", "location": "", "race_dates": "", "track_info": "",
        "w_temp": "", "w_desc": "", "w_icon": "", "w_wind": "", "w_hum": "",
        "status_text": "ADATOK...", "is_weekend_mode": 0, "is_live": 0, "progress": 0,
        "schedule": "", "track_map": "", "podium_title": "",
        "tyre_h": "C1", "tyre_m": "C2", "tyre_s": "C3",
        "tyre_img_h": IMG_HARD, 
        "tyre_img_m": IMG_MED, 
        "tyre_img_s": IMG_SOFT,
        "d1_c": "VER", "d1_p": "0", "d2_c": "NOR", "d2_p": "0", "d3_c": "HAM", "d3_p": "0",
        "c1_c": "MCL", "c1_p": "0", "c2_c": "RBR", "c2_p": "0", "c3_c": "FER", "c3_p": "0"
    }

    try:
        print("Adatok letöltése...")
        next_data = get_json("https://api.jolpi.ca/ergast/f1/current/next.json")
        
        if next_data:
            race = next_data['MRData']['RaceTable']['Races'][0]
            c_id = race['Circuit']['circuitId']
            
            # Pálya adatok
            data['status_title'] = race['raceName'].replace("Grand Prix", "GP").upper()
            data['location'] = race['Circuit']['Location']['locality'].upper()
            if c_id in TRACK_MAPS: data['track_map'] = TRACK_MAPS[c_id]
            if c_id in TRACK_SPECS: data['track_info'] = TRACK_SPECS[c_id]
            
            # Gumi adatok
            if c_id in TYRE_ALLOCATIONS:
                alloc = TYRE_ALLOCATIONS[c_id]
                data['tyre_h'], data['tyre_m'], data['tyre_s'] = alloc[0], alloc[1], alloc[2]

            # Időpontok
            now = datetime.now(timezone.utc)
            sessions = []
            
            def add_s(name, d_str, t_str, dur):
                clean_t = t_str.replace("Z", "")
                start = parser.parse(f"{d_str} {clean_t}").replace(tzinfo=timezone.utc)
                sessions.append({"name": name, "start": start, "end": start + timedelta(minutes=dur)})

            add_s("Futam", race['date'], race['time'], 120)
            if 'Qualifying' in race: add_s("Időmérő", race['Qualifying']['date'], race['Qualifying']['time'], 60)
            if 'FirstPractice' in race: add_s("1. Edzés", race['FirstPractice']['date'], race['FirstPractice']['time'], 60)
            if 'SecondPractice' in race: add_s("2. Edzés", race['SecondPractice']['date'], race['SecondPractice']['time'], 60)
            if 'ThirdPractice' in race: add_s("3. Edzés", race['ThirdPractice']['date'], race['ThirdPractice']['time'], 60)
            if 'Sprint' in race: add_s("Sprint", race['Sprint']['date'], race['Sprint']['time'], 60)
            if 'SprintQualifying' in race: add_s("Sprint Q", race['SprintQualifying']['date'], race['SprintQualifying']['time'], 45)

            sessions.sort(key=lambda x: x["start"])
            first, last = sessions[0]["start"], sessions[-1]["end"]
            data['race_dates'] = format_date_range(first, last) + f", {first.year}"

            # Menetrend
            sch_txt = ""
            for s in sessions:
                loc_t = s["start"].astimezone()
                day = ["Hé", "Ke", "Sze", "Cs", "Pé", "Szo", "Va"][loc_t.weekday()]
                t_str = loc_t.strftime("%H:%M")
                if now > s["end"]: sch_txt += f"[c=#70FFFFFF]✔ {day} {t_str} | {s['name']}[/c]\n"
                elif s["start"] <= now <= s["end"]: sch_txt += f"[c=#00FF00][b]🔴 {day} {t_str} | {s['name']}[/b][/c]\n"
                else: sch_txt += f"{day} {t_str} | {s['name']}\n"
            data['schedule'] = sch_txt.strip()

            # Progress Bar
            season_start = first
            if now < season_start:
                start_d, end_d = LAST_SEASON_END, season_start
                total = (end_d - start_d).total_seconds()
                elapsed = (now - start_d).total_seconds()
                prog = int((elapsed / total) * 100) if total > 0 else 0
                data['status_text'] = f"{(season_start - now).days} NAP VAN HÁTRA"
            else:
                prog = 50
                data['status_text'] = "VERSENYHÉTVÉGE"
            data['progress'] = max(0, min(100, prog))

            # Weekend Mode
            race_d = parser.parse(race['date']).date()
            if (race_d - timedelta(days=2)) <= now.date() <= race_d:
                data['is_weekend_mode'] = 1
                w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={race['Circuit']['Location']['lat']}&lon={race['Circuit']['Location']['long']}&appid={WEATHER_API_KEY}&units=metric&lang=hu"
                w_res = get_json(w_url)
                if w_res:
                    data['w_temp'] = f"{round(w_res['main']['temp'])}°C"
                    data['w_wind'] = f"{round(w_res['wind']['speed'] * 3.6)} km/h"
                    data['w_hum'] = f"{w_res['main']['humidity']}%"

        # Bajnokság
        try:
            d_stand = get_json("https://api.jolpi.ca/ergast/f1/current/driverStandings.json")
            if d_stand and d_stand['MRData']['StandingsTable']['StandingsLists']:
                lst = d_stand['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
                for i in range(min(3, len(lst))):
                    data[f'd{i+1}_c'] = lst[i]['Driver']['code']
                    data[f'd{i+1}_p'] = lst[i]['points']
        except: pass

        try:
            c_stand = get_json("https://api.jolpi.ca/ergast/f1/current/constructorStandings.json")
            if c_stand and c_stand['MRData']['StandingsTable']['StandingsLists']:
                lst = c_stand['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
                for i in range(min(3, len(lst))):
                    data[f'c{i+1}_c'] = lst[i]['Constructor']['name'][:3].upper()
                    data[f'c{i+1}_p'] = lst[i]['points']
        except: pass

    except Exception as e:
        print("HIBA:", e)
        traceback.print_exc()

    with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(data, f)
    print("Mentés kész.")

if __name__ == "__main__":
    main()
