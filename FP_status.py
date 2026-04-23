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
    print("--- 🌍 Configuration ---")
    lang_choice = input("Select language (is/es/fr): ").lower()
    if lang_choice not in LANG_DATA: lang_choice = "is"

    print("\n--- 📋 Layout Options ---")
    print("1: Standard (Each assignment is its own row)")
    print("2: Grouped (Date on top, assignments listed below it)")
    layout_choice = input("Select layout (1 or 2): ")

    format_choice = input("\nExport format? (csv/txt): ").lower()

    # 2. FETCH AND PARSE
    print(f"\n🛰️ Fetching Canvas data...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_text = response.read().decode('utf-8')

    events = raw_text.split("BEGIN:VEVENT")

    # We use a dictionary to group assignments by date string
    grouped_data = {}

    for event in events:
        if "SUMMARY:" in event and "DTSTART" in event:
            summary_line = event.split("SUMMARY:")[1].split("\n")[0].strip()
            date_raw = event.split("DTSTART")[1].split(":")[1][:8]

            try:
                y, m, d = int(date_raw[0:4]), int(date_raw[4:6]), int(date_raw[6:8])
                if y != 2026: continue

                formatted_date = format_date_by_lang(date(y, m, d), lang_choice)

                if formatted_date not in grouped_data:
                    grouped_data[formatted_date] = []
                grouped_data[formatted_date].append(summary_line)
            except:
                continue

    # 3. EXPORT LOGIC
    filename = f"planner_export.{format_choice}"
    headers = LANG_DATA[lang_choice]["headers"]

    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        if format_choice == "csv":
            writer = csv.writer(f)
            # We don't necessarily need headers for a vertical grouped layout,
            # but we can keep them or leave them out based on preference.

            for date_str, tasks in grouped_data.items():
                if layout_choice == "1":
                    # Standard: Date and Task on the same row
                    for task in tasks:
                        writer.writerow([date_str, task])
                else:
                    # Grouped: Date on Row 1, Task on Row 2
                    # Row 1: The Date
                    writer.writerow([date_str])

                    # Row 2+: The Assignments
                    for task in tasks:
                        writer.writerow([task])

                    # Row After: A blank row for spacing before the next date
                    writer.writerow([])

        else: # TXT format (Grouped)
            for date_str, tasks in grouped_data.items():
                if layout_choice == "1":
                    for task in tasks:
                        f.write(f"{date_str} | {task}\n")
                else:
                    f.write(f"\n{date_str}\n") # Date Row
                    for task in tasks:
                        f.write(f"{task}\n")    # Assignment Row
                    f.write("\n")               # Spacing Row


    print(f"✅ Success! Planner saved to {filename}")

if __name__ == "__main__":
    main()
