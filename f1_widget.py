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

def get_json(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"HIBA ({url}): {e}")
        return None

# ÚJ: Külön adjuk vissza a szöveget és az ikont
def get_weather_data(lat, lon):
    if not WEATHER_API_KEY: return None, None
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=hu"
    data = get_json(url)
    if data:
        temp = round(data['main']['temp'])
        desc = data['weather'][0]['description']
        icon = data['weather'][0]['icon'] # Pl. "10d"
        return f"{temp}°C, {desc.capitalize()}", icon
    return "", ""

def format_date_range(start_date, end_date):
    months = ["JAN", "FEB", "MÁRC", "ÁPR", "MÁJ", "JÚN", "JÚL", "AUG", "SZEP", "OKT", "NOV", "DEC"]
    s_month = months[start_date.month - 1]
    e_month = months[end_date.month - 1]
    if s_month == e_month:
        return f"{s_month} {start_date.day} - {end_date.day}"
    return f"{s_month} {start_date.day} - {e_month} {end_date.day}"

def main():
    widget_data = {
        "status_title": "F1 WIDGET", 
        "location": "",
        "race_dates": "",
        "weather_text": "",
        "weather_icon": "", # ÚJ MEZŐ AZ IKONNAK
        "status_text": "",
        "bg_color": "#FF252525",
        "schedule": "",
        "track_map": "",
        "progress": 33,
        "is_live": 0,
        "live_session": "",
        "podium_title": "",
        "podium_data": ""
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
        round_num = race['round']
        
        if circuit_id in TRACK_MAPS: widget_data['track_map'] = TRACK_MAPS[circuit_id]
        
        now = datetime.now(timezone.utc)
        
        # --- MENETREND ---
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
        quali_end = next((s["end"] for s in sessions if "Időmérő" in s["name"]), first_session)

        # --- MEZŐK KITÖLTÉSE ---
        widget_data['status_title'] = race_name.upper()
        widget_data['location'] = circuit_name.upper()
        widget_data['race_dates'] = format_date_range(first_session, last_session) + f", {first_session.year}"

        # --- IDŐJÁRÁS LOGIKA (HIBRID + IKON) ---
        is_race_weekend_weather = first_session.date() <= now.date() <= last_session.date()
        if is_race_weekend_weather:
            txt, ico = get_weather_data(race['Circuit']['Location']['lat'], race['Circuit']['Location']['long'])
            widget_data['weather_text'] = txt
            widget_data['weather_icon'] = ico
        else:
            widget_data['weather_text'] = ""
            widget_data['weather_icon'] = ""

        # --- LIVE ÉS VISSZASZÁMLÁLÓ ---
        is_weekend_mode = now.date() >= first_session.date()
        for s in sessions:
            if s["start"] <= now <= s["end"]:
                widget_data['is_live'] = 1
                widget_data['live_session'] = s["name"]
                widget_data['status_text'] = f"LIVE: {s['name'].upper()}"
                widget_data['bg_color'] = "#FF121212"
                is_weekend_mode = True 
                break

        if widget_data['is_live'] == 0:
            if is_weekend_mode:
                widget_data['status_text'] = "" 
                widget_data['bg_color'] = "#FF121212"
            else:
                time_left = first_session - now
                days = time_left.days
                if days == 0:
                    hours, rem = divmod(time_left.seconds, 3600)
                    mins, _ = divmod(rem, 60)
                    widget_data['status_text'] = f"KEZDÉS: {hours}ó {mins}p"
                else:
                    widget_data['status_text'] = f"{days} NAP VAN HÁTRA"

        # --- MENETREND ---
        schedule_text = ""
        for s in sessions:
            local_time = s["start"].astimezone()
            schedule_text += f"{['Hé','Ke','Sze','Cs','Pé','Szo','Va'][local_time.weekday()]} {local_time.strftime('%H:%M')} | {s['name']}\n"
        widget_data['schedule'] = schedule_text.strip()

        # --- DOBOGÓ LOGIKA (FALLBACK-KEL) ---
        last_race_data = get_json("https://api.jolpi.ca/ergast/f1/current/last.json")
        display_mode = "CHAMPIONSHIP"
        last_race_end_time = LAST_SEASON_END
        
        if last_race_data:
            try:
                lr = last_race_data['MRData']['RaceTable']['Races'][0]
                last_race_end_time = parser.parse(f"{lr['date']} {lr['time']}")
            except: pass

        hours_since_last = (now - last_race_end_time).total_seconds() / 3600
        hours_since_quali = (now - quali_end).total_seconds() / 3600

        if 0 < hours_since_last < 60: display_mode = "LAST_RACE"
        elif hours_since_quali > 0 and (first_session <= now <= last_session): display_mode = "QUALIFYING"
        else: display_mode = "CHAMPIONSHIP"

        p1, p2, p3 = "", "", ""
        if display_mode == "LAST_RACE":
            try:
                res = last_race_data['MRData']['RaceTable']['Races'][0]['Results']
                p1, p2, p3 = res[0]['Driver']['code'], res[1]['Driver']['code'], res[2]['Driver']['code']
                widget_data['podium_title'] = "ELŐZŐ DOBOGÓ"
            except: pass
        elif display_mode == "QUALIFYING":
            widget_data['podium_title'] = f"{circuit_name} POLE".upper()
            try:
                q_data = get_json(f"https://api.jolpi.ca/ergast/f1/current/{round_num}/qualifying.json")
                res = q_data['MRData']['RaceTable']['Races'][0]['QualifyingResults']
                p1, p2, p3 = res[0]['Driver']['code'], res[1]['Driver']['code'], res[2]['Driver']['code']
            except: display_mode = "CHAMPIONSHIP"
        if display_mode == "CHAMPIONSHIP":
            widget_data['podium_title'] = "VILÁGBAJNOKSÁG"
            standings_data = get_json("https://api.jolpi.ca/ergast/f1/current/driverStandings.json")
            found = False
            try:
                res = standings_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
                p1, p2, p3 = res[0]['Driver']['code'], res[1]['Driver']['code'], res[2]['Driver']['code']
                found = True
            except: pass
            if not found: # Fallback tavalyi évre
                last_year = now.year - 1
                standings_data = get_json(f"https://api.jolpi.ca/ergast/f1/{last_year}/driverStandings.json")
                try:
                    res = standings_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
                    p1, p2, p3 = res[0]['Driver']['code'], res[1]['Driver']['code'], res[2]['Driver']['code']
                except: pass

        if p1: widget_data['podium_data'] = f"🥇{p1} 🥈{p2} 🥉{p3}"
        else: widget_data['podium_data'] = ""

        # --- PROGRESS ---
        race_start = next((s["start"] for s in sessions if s["name"] == "Futam"), None)
        calc_progress = 50
        if race_start:
            total_duration = (race_start - last_race_end_time).total_seconds()
            elapsed = (now - last_race_end_time).total_seconds()
            if total_duration > 0: calc_progress = int(max(0, min(100, (elapsed / total_duration) * 100)))
        widget_data['progress'] = calc_progress

    except Exception as e: print(f"Hiba: {e}")

    with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(widget_data, f)
    print(f"Ikon mód kész. Ikon: {widget_data['weather_icon']}")

if __name__ == "__main__":
    main()
