import requests
import json
from datetime import datetime, timedelta, timezone
from dateutil import parser

# --- BEÁLLÍTÁSOK ---
WEATHER_API_KEY = "84352f72e1c7846365290f1afb251a4c"
JSON_OUTPUT_PATH = "f1_widget_data.json"

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
        "status_text": "Betöltés...",
        "weather": "",
        "bg_color": "#FF252525", # Alapból "világosabb" sötétszürke (Hétköznap)
        "schedule": "",
        "track_map": "",
        "progress": 0,
        "is_live": 0, # 0 = Nem live, 1 = LIVE
        "live_session": "" # Melyik esemény zajlik épp
    }

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
        
        # --- MENETREND ÉS LIVE ÉRZÉKELÉS ---
        sessions = []
        # Segédfüggvény az események hozzáadására (név, idő, hossz_percben)
        def add_session(name, date_str, time_str, duration_min):
            start = parser.parse(f"{date_str} {time_str}")
            end = start + timedelta(minutes=duration_min)
            sessions.append({"name": name, "start": start, "end": end})

        # Adatok betöltése (időtartamokkal!)
        add_session("Futam", race['date'], race['time'], 120) # Futam kb 2 óra
        if 'Qualifying' in race: add_session("Időmérő", race['Qualifying']['date'], race['Qualifying']['time'], 60)
        if 'FirstPractice' in race: add_session("1. Edzés", race['FirstPractice']['date'], race['FirstPractice']['time'], 60)
        if 'SecondPractice' in race: add_session("2. Edzés", race['SecondPractice']['date'], race['SecondPractice']['time'], 60)
        if 'ThirdPractice' in race: add_session("3. Edzés", race['ThirdPractice']['date'], race['ThirdPractice']['time'], 60)
        if 'Sprint' in race: add_session("Sprint", race['Sprint']['date'], race['Sprint']['time'], 60)
        if 'SprintQualifying' in race: add_session("Sprint Q", race['SprintQualifying']['date'], race['SprintQualifying']['time'], 45)

        # Sorbarendezés
        sessions.sort(key=lambda x: x["start"])

        # Live ellenőrzés
        is_weekend = False # Versenyhétvége van-e (4 napon belül)
        
        for s in sessions:
            # Ha most zajlik bármelyik
            if s["start"] <= now <= s["end"]:
                widget_data['is_live'] = 1
                widget_data['live_session'] = s["name"]
                widget_data['status_text'] = f"LIVE: {s['name'].upper()}"
                widget_data['bg_color'] = "#FF121212" # Hétvégi sötét háttér (hogy látszódjon a piros keret)
                is_weekend = True
                break
            
            # Ha még a jövőben van, de közel (hétvége mód)
            if s["start"] > now:
                time_diff = s["start"] - now
                if time_diff.days < 4:
                    is_weekend = True

        # Háttérszín logika
        if widget_data['is_live'] == 0:
            if is_weekend:
                widget_data['bg_color'] = "#FF121212" # Hétvége (sötét/fekete)
            else:
                widget_data['bg_color'] = "#FF2E2E2E" # Hétköznap/szünet (világosabb szürke)

        # Menetrend szöveg generálás
        schedule_text = ""
        for s in sessions:
            local_time = s["start"].astimezone()
            day_name = ["Hé", "Ke", "Sze", "Cs", "Pé", "Szo", "Va"][local_time.weekday()]
            time_str = local_time.strftime("%H:%M")
            schedule_text += f"{day_name} {time_str} | {s['name']}\n"
        widget_data['schedule'] = schedule_text.strip()

        # Progress bar Számítás
        last_data = get_json("https://api.jolpi.ca/ergast/f1/current/last.json")
        if last_data:
            last_race = last_data['MRData']['RaceTable']['Races'][0]
            last_race_time = parser.parse(f"{last_race['date']} {last_race['time']}")
            # Futam start ideje a sessions listából (az első "Futam" nevű)
            race_start = next((s["start"] for s in sessions if s["name"] == "Futam"), None)
            
            if race_start:
                total_duration = (race_start - last_race_time).total_seconds()
                elapsed = (now - last_race_time).total_seconds()
                if total_duration > 0:
                    percent = int(max(0, min(100, (elapsed / total_duration) * 100)))
                    widget_data['progress'] = percent

        # Címkék ha nem live
        if widget_data['is_live'] == 0:
            next_sess = next((s for s in sessions if s["start"] > now), None)
            if next_sess:
                time_left = next_sess["start"] - now
                days = time_left.days
                if days < 4: # Közelgő esemény
                    hours, rem = divmod(time_left.seconds, 3600)
                    mins, _ = divmod(rem, 60)
                    widget_data['status_title'] = f"Következő: {next_sess['name']}"
                    widget_data['status_text'] = f"Kezdés: {hours}ó {mins}p múlva"
                    # Időjárás
                    w = get_weather(race['Circuit']['Location']['lat'], race['Circuit']['Location']['long'])
                    widget_data['weather'] = f"{race['Circuit']['Location']['locality']}: {w}"
                else: # Távoli futam
                    widget_data['status_title'] = f"Következő: {race_name}"
                    widget_data['status_text'] = f"{days} nap van hátra"

    except Exception as e:
        widget_data['status_text'] = f"Hiba: {e}"

    with open(JSON_OUTPUT_PATH, 'w') as f: json.dump(widget_data, f)
    print("Widget frissítve! Live:", widget_data['is_live'], "Bg:", widget_data['bg_color'])

if __name__ == "__main__":
    main()