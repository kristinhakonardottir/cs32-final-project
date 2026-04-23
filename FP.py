import urllib.request
import csv
from datetime import date

# --- TRANSLATION MASTER DATABASE ---
LANG_DATA = {
    "is": {
        "months": {1: "janúar", 2: "febrúar", 3: "mars", 4: "apríl", 5: "maí", 6: "júní", 7: "júlí", 8: "ágúst", 9: "september", 10: "október", 11: "nóvember", 12: "desember"},
        "days": {"Monday": "mánudagur", "Tuesday": "þriðjudagur", "Wednesday": "miðvikudagur", "Thursday": "fimmtudagur", "Friday": "föstudagur", "Saturday": "laugardagur", "Sunday": "sunnudagur"},
    },
    "es": {
        "months": {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio", 7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"},
        "days": {"Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles", "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"},
    },
    "fr": {
        "months": {1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin", 7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"},
        "days": {"Monday": "lundi", "Tuesday": "mardi", "Wednesday": "mercredi", "Thursday": "jeudi", "Friday": "vendredi", "Saturday": "samedi", "Sunday": "dimanche"},
    }
}

URL = "https://canvas.harvard.edu/feeds/calendars/user_NOQogScFrdtBPeSdI1gIbpScSjCBFTuHYcdNf8W1.ics"

def format_date_by_lang(dt, lang_code):
    """Translates and formats a date object into a human-readable string."""
    lang = LANG_DATA[lang_code]
    day_name = lang["days"][dt.strftime("%A")]
    month_name = lang["months"][dt.month]
    return f"{day_name} {dt.day}. {month_name}"

def get_grouped_assignments(raw_text, lang_choice):
    """Parses raw ICS, filters for 2026, and returns a dict keyed by date OBJECTS."""
    events = raw_text.split("BEGIN:VEVENT")
    grouped_data = {}

    for event in events:
        if "SUMMARY:" in event and "DTSTART" in event:
            summary_line = event.split("SUMMARY:")[1].split("\n")[0].strip()
            date_raw = event.split("DTSTART")[1].split(":")[1][:8]

            try:
                y, m, d = int(date_raw[0:4]), int(date_raw[4:6]), int(date_raw[6:8])
                if y != 2026: continue

                py_date = date(y, m, d)

                # String Flip Logic
                course = "Almennt" if lang_choice == "is" else "General"
                assignment = summary_line
                if "[" in summary_line:
                    parts = summary_line.rsplit("[", 1)
                    assignment = parts[0].strip()
                    course = parts[1].replace("]", "").strip()

                flipped_summary = f"{course}: {assignment}"

                if py_date not in grouped_data:
                    grouped_data[py_date] = []
                grouped_data[py_date].append(flipped_summary)
            except:
                continue
    return grouped_data

def main():
    # 1. User preferences
    print("--- 🌍 Configuration ---")
    lang_choice = input("Select language (is/es/fr): ").lower()
    if lang_choice not in LANG_DATA: lang_choice = "is"

    print("\n--- 📋 Layout Options ---")
    print("1: Standard (Date and Task on same row)")
    print("2: Grouped (Date row, Task row below, extra spacing)")
    layout_choice = input("Select layout (1 or 2): ")
    format_choice = input("\nExport format? (csv/txt): ").lower()

    # 2. Getting data
    print(f"\n🛰️ Fetching Canvas data...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_text = response.read().decode('utf-8')

    assignments_dict = get_grouped_assignments(raw_text, lang_choice)

    # 3. EXPORT LOGIC
    filename = f"planner_export.{format_choice}"

    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        # Sort the dates so the planner is chronological
        sorted_dates = sorted(assignments_dict.keys())

        if format_choice == "csv":
            writer = csv.writer(f)
            for py_date in sorted_dates:
                date_str = format_date_by_lang(py_date, lang_choice)
                tasks = assignments_dict[py_date]

                if layout_choice == "1":
                    for task in tasks:
                        writer.writerow([date_str, task])
                else:
                    writer.writerow([date_str]) # The date line
                    for task in tasks:
                        writer.writerow([task])     # The assignment line
                    writer.writerow([])             # The blank line

        else: # TXT format
            for py_date in sorted_dates:
                date_str = format_date_by_lang(py_date, lang_choice)
                tasks = assignments_dict[py_date]

                if layout_choice == "1":
                    for task in tasks:
                        f.write(f"{date_str} | {task}\n")
                else:
                    f.write(f"{date_str}\n")
                    for task in tasks:
                        f.write(f"{task}\n")
                    f.write("\n")

    print(f"✅ Success! Assignments-only planner saved to {filename}")

if __name__ == "__main__":
    main()
