import requests
import json
import traceback
from datetime import datetime, timedelta, timezone
from dateutil import parser

# --- 1. BEÁLLÍTÁSOK ---
WEATHER_API_KEY = "84352f72e1c7846365290f1afb251a4c"
JSON_OUTPUT_PATH = "f1_widget_data.json"

# Szezon határok (Téli szünet számításhoz)
LAST_SEASON_END = datetime(2025, 12, 8, 14, 0, 0, tzinfo=timezone.utc)
SEASON_START_2026 = datetime(2026, 3, 6, 4, 0, 0, tzinfo=timezone.utc)

# --- 2. KÉPEK LINKEK (Stabil Imgur linkek a KWGT-nek) ---
# Ezeket a linkeket használjuk, mert a Wikipédia néha nem tölt be a widgetben
IMG_HARD = "https://i.imgur.com/7Z7Z1Zt.png"   # Fehér oldalfal
IMG_MED = "https://i.imgur.com/3Z7Z1Zt.png"    # Sárga oldalfal
IMG_SOFT = "https://i.imgur.com/e4J6a2S.png"    # Piros oldalfal

# --- 3. TELJES ADATBÁZISOK (Nincs rövidítés!) ---

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

# Pályarajzok (Url-ek)
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

# Gumikiosztás (Minden pálya!)
# Formátum: [Hard, Medium, Soft]
TYRE_ALLOCATIONS = {
    "bahrain": ["C1", "C2", "C3"],
    "jeddah": ["C2", "C3", "C4"],
    "albert_park": ["C3", "C4", "C5"],
    "suzuka": ["C1", "C2", "C3"],
    "shanghai": ["C2", "C3", "C4"],
    "miami": ["C2", "C3", "C4"],
    "imola": ["C3", "C4", "C5"],
    "monaco": ["C4", "C5", "C6"],
    "catalunya": ["C1", "C2", "C3"],
    "villeneuve": ["C3", "C4", "C5"], # Kanada
    "red_bull_ring": ["C3", "C4", "C5"], # Ausztria
    "silverstone": ["C1", "C2", "C3"],
    "hungaroring": ["C3", "C4", "C5"],
    "spa": ["C2", "C3", "C4"],
    "zandvoort": ["C1", "C2", "C3"],
    "monza": ["C3", "C4", "C5"],
    "baku": ["C3", "C4", "C5"],
    "marina_bay": ["C4", "C5", "C6"],
    "americas": ["C2", "C3", "C4"], # USA
    "rodriguez": ["C3", "C4", "C5"], # Mexikó
    "interlagos": ["C2", "C3", "C4"], # Brazília
    "vegas": ["C3", "C4", "C5"],
    "losail": ["C1", "C2", "C3"], # Katar
    "yas_marina": ["C3", "C4", "C5"] # Abu Dhabi
}

# --- 4. SEGÉDFÜGGVÉNYEK ---

def get_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Hiba ennél a linknél: {url} -> {e}")
        return None

def format_date_range(start_date, end_date):
    months = ["JAN", "FEB", "MÁRC", "ÁPR", "MÁJ", "JÚN", "JÚL", "AUG", "SZEP", "OKT", "NOV", "DEC"]
    if start_date.month == end_date.month:
        return f"{months[start_date.month-1]} {start_date.day} - {end_date.day}"
    return f"{months[start_date.month-1]} {start_date.day} - {months[end_date.month-1]} {end_date.day}"

# --- 5. FŐ FÜGGVÉNY ---

def main():
    print("Script indítása...")
    
    # Alapértelmezett adat (ha minden API lehalna, ez jelenik meg)
    data = {
        "last_updated": str(datetime.now()),
        "status_title": "F1 WIDGET", 
        "location": "LOADING...", 
        "race_dates": "", 
        "track_info": "",
        "track_map": "",
        # Időjárás
        "w_temp": "", "w_desc": "", "w_icon": "", "w_wind": "", "w_hum": "",
        # Státusz
        "status_text": "ADATOK...", 
        "is_weekend_mode": 0, 
        "is_live": 0, 
        "progress": 0,
        "schedule": "",
        # Gumik (Alapértelmezett)
        "tyre_h": "C1", "tyre_m": "C2", "tyre_s": "C3",
        "tyre_img_h": IMG_HARD, 
        "tyre_img_m": IMG_MED, 
        "tyre_img_s": IMG_SOFT,
        # Bajnokság (Placeholder)
        "d1_c": "VER", "d1_p": "0", "d2_c": "NOR", "d2_p": "0", "d3_c": "HAM", "d3_p": "0",
        "c1_c": "MCL", "c1_p": "0", "c2_c": "RBR", "c2_p": "0", "c3_c": "FER", "c3_p": "0"
    }

    try:
        # A) Következő verseny adatainak letöltése
        print("Következő futam keresése...")
        next_data = get_json("https://api.jolpi.ca/ergast/f1/current/next.json")
        
        if next_data:
            race = next_data['MRData']['RaceTable']['Races'][0]
            c_id = race['Circuit']['circuitId']
            
            # Alapadatok kitöltése
            data['status_title'] = race['raceName'].replace("Grand Prix", "GP").upper()
            data['location'] = race['Circuit']['Location']['locality'].upper()
            
            # Pálya infók és térkép betöltése
            if c_id in TRACK_MAPS: data['track_map'] = TRACK_MAPS[c_id]
            if c_id in TRACK_SPECS: data['track_info'] = TRACK_SPECS[c_id]
            
            # GUMIKIOSZTÁS BETÖLTÉSE
            if c_id in TYRE_ALLOCATIONS:
                alloc = TYRE_ALLOCATIONS[c_id]
                data['tyre_h'] = alloc[0]
                data['tyre_m'] = alloc[1]
                data['tyre_s'] = alloc[2]
            else:
                # Ha véletlen nincs benne a listában, fallback C1-C3
                print(f"HIÁNYZÓ GUMI ADAT: {c_id}")
                data['tyre_h'], data['tyre_m'], data['tyre_s'] = "C1", "C2", "C3"

            # B) Menetrend (Schedule) és Időzónák
            now = datetime.now(timezone.utc)
            sessions = []
            
            # Segédfüggvény az ülések hozzáadásához
            def add_session(name, date_str, time_str, duration_min):
                # A 'Z' eltávolítása és UTC kényszerítése
                clean_time = time_str.replace("Z", "")
                start = parser.parse(f"{date_str} {clean_time}").replace(tzinfo=timezone.utc)
                end = start + timedelta(minutes=duration_min)
                sessions.append({"name": name, "start": start, "end": end})

            # Minden esemény hozzáadása
            add_session("Futam", race['date'], race['time'], 120)
            if 'Qualifying' in race: add_session("Időmérő", race['Qualifying']['date'], race['Qualifying']['time'], 60)
            if 'FirstPractice' in race: add_session("1. Edzés", race['FirstPractice']['date'], race['FirstPractice']['time'], 60)
            if 'SecondPractice' in race: add_session("2. Edzés", race['SecondPractice']['date'], race['SecondPractice']['time'], 60)
            if 'ThirdPractice' in race: add_session("3. Edzés", race['ThirdPractice']['date'], race['ThirdPractice']['time'], 60)
            if 'Sprint' in race: add_session("Sprint", race['Sprint']['date'], race['Sprint']['time'], 60)
            if 'SprintQualifying' in race: add_session("Sprint Q", race['SprintQualifying']['date'], race['SprintQualifying']['time'], 45)

            # Rendezés időrendbe
            sessions.sort(key=lambda x: x["start"])
            first_session_start = sessions[0]["start"]
            last_session_end = sessions[-1]["end"]
            
            data['race_dates'] = format_date_range(first_session_start, last_session_end) + f", {first_session_start.year}"

            # Menetrend szöveg generálása
            schedule_text = ""
            for s in sessions:
                # Átváltás helyi időre (hogy a widgeten jó legyen)
                local_time = s["start"].astimezone()
                day_name = ["Hé", "Ke", "Sze", "Cs", "Pé", "Szo", "Va"][local_time.weekday()]
                time_str = local_time.strftime("%H:%M")
                
                if now > s["end"]: 
                    schedule_text += f"[c=#70FFFFFF]✔ {day_name} {time_str} | {s['name']}[/c]\n"
                elif s["start"] <= now <= s["end"]: 
                    schedule_text += f"[c=#00FF00][b]🔴 {day_name} {time_str} | {s['name']}[/b][/c]\n"
                else: 
                    schedule_text += f"{day_name} {time_str} | {s['name']}\n"
            data['schedule'] = schedule_text.strip()

            # C) Progress Bar (Téli szünet logika)
            season_start_point = first_session_start
            if now < season_start_point:
                # Téli szünet
                start_date = LAST_SEASON_END
                end_date = season_start_point
                total_seconds = (end_date - start_date).total_seconds()
                elapsed_seconds = (now - start_date).total_seconds()
                
                if total_seconds > 0:
                    prog = int((elapsed_seconds / total_seconds) * 100)
                else:
                    prog = 0
                
                data['status_text'] = f"{(season_start_point - now).days} NAP VAN HÁTRA"
            else:
                # Szezon közben
                prog = 50 
                data['status_text'] = "VERSENYHÉTVÉGE"
            
            data['progress'] = max(0, min(100, prog))

            # D) Időjárás (Weekend Mode)
            # Ha Péntek, Szombat vagy Vasárnap van a versenyhétvégén
            race_date = parser.parse(race['date']).date()
            friday_date = race_date - timedelta(days=2)
            
            # Most mindig lekérjük tesztelés miatt, de beállítjuk a flaget
            if friday_date <= now.date() <= race_date:
                data['is_weekend_mode'] = 1
            else:
                data['is_weekend_mode'] = 0

            # Időjárás lekérése
            lat = race['Circuit']['Location']['lat']
            lon = race['Circuit']['Location']['long']
            w_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=hu"
            w_res = get_json(w_url)
            
            if w_res:
                data['w_temp'] = f"{round(w_res['main']['temp'])}°C"
                data['w_wind'] = f"{round(w_res['wind']['speed'] * 3.6)} km/h"
                data['w_hum'] = f"{w_res['main']['humidity']}%"
                data['w_desc'] = w_res['weather'][0]['description'].capitalize()
                data['w_icon'] = w_res['weather'][0]['icon']

        # E) BAJNOKSÁG ÁLLÁS (Robusztus verzió)
        print("Bajnokság adatok lekérése...")
        
        # 1. Pilóták
        try:
            # Először próbáljuk az aktuális évet (current)
            d_stand = get_json("https://api.jolpi.ca/ergast/f1/current/driverStandings.json")
            
            # Ha üres (mert év eleje van), próbáljuk a tavalyit
            if not d_stand or not d_stand['MRData']['StandingsTable']['StandingsLists']:
                 print("Idei pilóta adat üres, tavalyi lekérése...")
                 d_stand = get_json(f"https://api.jolpi.ca/ergast/f1/{now.year-1}/driverStandings.json")
            
            if d_stand and d_stand['MRData']['StandingsTable']['StandingsLists']:
                lst = d_stand['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
                if len(lst) > 0: 
                    data['d1_c'] = lst[0]['Driver']['code']
                    data['d1_p'] = lst[0]['points']
                if len(lst) > 1: 
                    data['d2_c'] = lst[1]['Driver']['code']
                    data['d2_p'] = lst[1]['points']
                if len(lst) > 2: 
                    data['d3_c'] = lst[2]['Driver']['code']
                    data['d3_p'] = lst[2]['points']
        except Exception as e: 
            print(f"Pilóta hiba: {e}")

        # 2. Konstruktőrök
        try:
            # Először próbáljuk az aktuális évet
            c_stand = get_json("https://api.jolpi.ca/ergast/f1/current/constructorStandings.json")
            
            # Ha üres, próbáljuk a tavalyit
            if not c_stand or not c_stand['MRData']['StandingsTable']['StandingsLists']:
                 print("Idei konstruktőr adat üres, tavalyi lekérése...")
                 c_stand = get_json(f"https://api.jolpi.ca/ergast/f1/{now.year-1}/constructorStandings.json")
            
            if c_stand and c_stand['MRData']['StandingsTable']['StandingsLists']:
                lst = c_stand['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
                if len(lst) > 0: 
                    data['c1_c'] = lst[0]['Constructor']['name'][:3].upper()
                    data['c1_p'] = lst[0]['points']
                if len(lst) > 1: 
                    data['c2_c'] = lst[1]['Constructor']['name'][:3].upper()
                    data['c2_p'] = lst[1]['points']
                if len(lst) > 2: 
                    data['c3_c'] = lst[2]['Constructor']['name'][:3].upper()
                    data['c3_p'] = lst[2]['points']
        except Exception as e: 
            print(f"Konstruktőr hiba: {e}")

    except Exception as e:
        print("VÉGZETES HIBA:", e)
        traceback.print_exc()

    # MENTÉS
    with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(data, f)
    print("Mentés kész.")

if __name__ == "__main__":
    main()
