import urllib.request
import csv
from datetime import date

# --- TRANSLATION MASTER DATABASE ---
LANG_DATA = {
    "is": {
        "months": {1: "janúar", 2: "febrúar", 3: "mars", 4: "apríl", 5: "maí", 6: "júní", 7: "júlí", 8: "ágúst", 9: "september", 10: "október", 11: "nóvember", 12: "desember"},
        "days": {"Monday": "mánudagur", "Tuesday": "þriðjudagur", "Wednesday": "miðvikudagur", "Thursday": "fimmtudagur", "Friday": "föstudagur", "Saturday": "laugardagur", "Sunday": "sunnudagur"},
        "headers": ["Dagsetning", "Verkefni"]
    },
    "es": {
        "months": {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio", 7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"},
        "days": {"Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles", "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"},
        "headers": ["Fecha", "Tareas"]
    },
    "fr": {
        "months": {1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin", 7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"},
        "days": {"Monday": "lundi", "Tuesday": "mardi", "Wednesday": "mercredi", "Thursday": "jeudi", "Friday": "vendredi", "Saturday": "samedi", "Sunday": "dimanche"},
        "headers": ["Date", "Devoirs"]
    }
}

URL = "https://canvas.harvard.edu/feeds/calendars/user_NOQogScFrdtBPeSdI1gIbpScSjCBFTuHYcdNf8W1.ics"

def format_date_by_lang(dt, lang_code):
    lang = LANG_DATA[lang_code]
    day_name = lang["days"][dt.strftime("%A")]
    month_name = lang["months"][dt.month]
    return f"{day_name} {dt.day}. {month_name}"

def main():
    # 1. USER PREFERENCES
    lang_choice = "is" # Defaulting to Icelandic based on your example
    format_choice = input("Export format? (csv/txt): ").lower()

    # 2. FETCH AND PARSE
    print(f"\n🛰️ Fetching Canvas data...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_text = response.read().decode('utf-8')

    events = raw_text.split("BEGIN:VEVENT")
    grouped_data = {}

    for event in events:
        if "SUMMARY:" in event and "DTSTART" in event:
            summary_line = event.split("SUMMARY:")[1].split("\n")[0].strip()
            date_raw = event.split("DTSTART")[1].split(":")[1][:8]

            try:
                y, m, d = int(date_raw[0:4]), int(date_raw[4:6]), int(date_raw[6:8])
                if y != 2026: continue # Only keep current year

                # --- THE "FLIP" LOGIC ---
                # Default values
                course = "Almennt"
                assignment = summary_line

                if "[" in summary_line:
                    # Logic: Split at the last '[' to separate course from assignment
                    parts = summary_line.rsplit("[", 1)
                    assignment = parts[0].strip()
                    course = parts[1].replace("]", "").strip()

                # Create the formatted string: "Course: Assignment"
                flipped_summary = f"{course}: {assignment}"

                formatted_date = format_date_by_lang(date(y, m, d), lang_choice)

                if formatted_date not in grouped_data:
                    grouped_data[formatted_date] = []
                grouped_data[formatted_date].append(flipped_summary)
            except:
                continue

    # 3. EXPORT LOGIC
    filename = f"namsaaetlun.{format_choice}"

    # Use utf-8-sig so Icelandic characters (ð, þ, á) show up in Excel
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        if format_choice == "csv":
            writer = csv.writer(f)
            for date_str, tasks in grouped_data.items():
                writer.writerow([date_str]) # Date Row
                for task in tasks:
                    writer.writerow([task]) # "Course: Assignment" Row
                writer.writerow([])         # Blank Row for spacing

        else: # TXT format
            for date_str, tasks in grouped_data.items():
                f.write(f"{date_str}\n")
                for task in tasks:
                    f.write(f"{task}\n")
                f.write("\n")

    print(f"✅ Success! Your planner is ready in {filename}")

if __name__ == "__main__":
    main()
