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

def get_weather(lat, lon):
    if not WEATHER_API_KEY: return ""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=hu"
    data = get_json(url)
    if data:
        return f"{round(data['main']['temp'])}°C, {data['weather'][0]['description']}"
    return ""

def main():
    widget_data = {
        "status_title": "F1 Widget",
        "status_text": "",
        "weather": "",
        "bg_color": "#FF252525",
        "schedule": "",
        "track_map": "",
        "progress": 33,
        "is_live": 0,
        "live_session": "",
        "last_podium": ""
    }

    # 1. KÖVETKEZŐ FUTAM LEKÉRÉSE
    next_data = get_json("https://api.jolpi.ca/ergast/f1/current/next.json")
    
    if not next_data:
        with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(widget_data, f)
        return

    try:
        race = next_data['MRData']['RaceTable']['Races'][0]
        race_name = race['raceName']
        circuit_id = race['Circuit']['circuitId']
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

        # Live ellenőrzés
        is_weekend_live = False # Ez csak a live színekhez kell
        for s in sessions:
            if s["start"] <= now <= s["end"]:
                widget_data['is_live'] = 1
                widget_data['live_session'] = s["name"]
                widget_data['status_text'] = f"LIVE: {s['name'].upper()}"
                widget_data['bg_color'] = "#FF121212"
                is_weekend_live = True
                break
        
        # --- CÍMEK ÉS VISSZASZÁMLÁLÁS LOGIKA (Módosítva) ---
        if widget_data['is_live'] == 0:
            first_session_start = sessions[0]["start"] # Általában Péntek
            
            # Ellenőrizzük, hogy elértük-e már a hétvégét (Pénteket)
            # Ha a mai nap dátuma >= az első edzés napjával
            is_race_weekend_mode = now.date() >= first_session_start.date()

            if is_race_weekend_mode:
                # PÉNTEKTŐL VASÁRNAPIG (Hétvége mód)
                widget_data['status_title'] = race_name # Csak a név (Nincs "Következő")
                widget_data['status_text'] = "" # Üres visszaszámláló
                widget_data['bg_color'] = "#FF121212" # Sötétebb háttér
            else:
                # HÉTFŐTŐL CSÜTÖRTÖKIG (Várakozás mód)
                widget_data['status_title'] = f"Következő: {race_name}"
                widget_data['bg_color'] = "#FF2E2E2E"
                
                # Visszaszámláló számítása
                time_left = first_session_start - now
                days = time_left.days
                if days < 0: days = 0 # Biztonsági
                
                if days == 0:
                    # Ha már aznap van, de még nem kezdődött el (pl. Péntek reggel)
                    hours, rem = divmod(time_left.seconds, 3600)
                    mins, _ = divmod(rem, 60)
                    widget_data['status_text'] = f"Kezdés: {hours}ó {mins}p múlva"
                else:
                    widget_data['status_text'] = f"{days} nap van hátra"

            # Időjárás (mindig lekérjük, ha 4 napon belül van, de csak ha nincs Live)
            if (first_session_start - now).days < 4:
                w = get_weather(race['Circuit']['Location']['lat'], race['Circuit']['Location']['long'])
                widget_data['weather'] = f"{race['Circuit']['Location']['locality']}: {w}"

        # Menetrend szöveg
        schedule_text = ""
        for s in sessions:
            local_time = s["start"].astimezone()
            day_name = ["Hé", "Ke", "Sze", "Cs", "Pé", "Szo", "Va"][local_time.weekday()]
            time_str = local_time.strftime("%H:%M")
            schedule_text += f"{day_name} {time_str} | {s['name']}\n"
        widget_data['schedule'] = schedule_text.strip()

        # --- PROGRESS BAR ---
        last_data = get_json("https://api.jolpi.ca/ergast/f1/current/last.json")
        race_start = next((s["start"] for s in sessions if s["name"] == "Futam"), None)
        calculated_progress = None
        
        if last_data:
            try:
                # 1. DOBOGÓSOK (NEW - 60 órás szabály: V+H+K)
                last_race_results = last_data['MRData']['RaceTable']['Races'][0]
                results = last_race_results.get('Results', [])
                last_race_time = parser.parse(f"{last_race_results['date']} {last_race_results['time']}")

                # 60 óra = 2.5 nap (Vasárnap 16:00 -> Szerda 04:00)
                elapsed_since_race = (now - last_race_time).total_seconds()
                is_fresh_result = elapsed_since_race < (60 * 3600)

                if len(results) >= 3 and is_fresh_result:
                    p1 = results[0]['Driver']['code']
                    p2 = results[1]['Driver']['code']
                    p3 = results[2]['Driver']['code']
                    widget_data['last_podium'] = f"🥇{p1} 🥈{p2} 🥉{p3}"
                else:
                    widget_data['last_podium'] = ""

                # 2. PROGRESS
                if race_start:
                    total_duration = (race_start - last_race_time).total_seconds()
                    elapsed = (now - last_race_time).total_seconds()
                    if total_duration > 0:
                        calculated_progress = int(max(0, min(100, (elapsed / total_duration) * 100)))
            except Exception as e:
                print(f"Hiba last data: {e}")

        # Backup Progress
        if calculated_progress is None and race_start:
            total_duration = (race_start - LAST_SEASON_END).total_seconds()
            elapsed = (now - LAST_SEASON_END).total_seconds()
            if total_duration > 0:
                calculated_progress = int(max(0, min(100, (elapsed / total_duration) * 100)))
        
        widget_data['progress'] = calculated_progress if calculated_progress is not None else 50

    except Exception as e:
        widget_data['status_text'] = f"Hiba: {e}"
        print(f"Végzetes hiba: {e}")

    with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(widget_data, f)
    print(f"Widget adat frissítve! Progress: {widget_data['progress']}")

if __name__ == "__main__":
    main()
