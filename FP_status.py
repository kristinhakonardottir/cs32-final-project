import urllib.request
import csv
from datetime import date, timedelta

# Dictionaries (different languages is/es/fr) of dictionaries (the translations of the months and days)
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

# Change to the iCalendar feed you want to fetch assignments from
# URL = "https://canvas.harvard.edu/feeds/calendars/user_NOQogScFrdtBPeSdI1gIbpScSjCBFTuHYcdNf8W1.ics"
URL = "https://calendar.google.com/calendar/ical/kristinhakonardottir%40college.harvard.edu/public/basic.ics"

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

                if "[" in summary_line:
                    parts = summary_line.rsplit("[", 1)
                    assignment = parts[0].strip()
                    course = parts[1].replace("]", "").strip()
                    flipped_summary = f"{course}: {assignment}"
                else:
                    flipped_summary = summary_line

                if py_date not in grouped_data:
                    grouped_data[py_date] = []
                grouped_data[py_date].append(flipped_summary)
            except:
                continue
    return grouped_data

def main():
    # 1. User preferences
    print("--- Configuration ---")
    lang_choice = input("Select language (is/es/fr): ").lower()

    print("\n--- Layout Options ---")
    print("1: Standard (Date and Task on same row)")
    print("2: Grouped (Date row, Task row below, extra spacing)")
    layout_choice = input("Select layout (1 or 2): ")
    format_choice = input("\nExport format? (csv/txt): ").lower()

    # 2. Getting data
    print(f"\nFetching Canvas data...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_text = response.read().decode('utf-8')

    assignments = get_grouped_assignments(raw_text, lang_choice)

    # 3. Timeline Bounds (Jan 26 to last assignment, can change depending on when you want it to start)
    start_date = date(2026, 1, 26)
    end_date = max(assignments.keys()) if assignments else date(2026, 5, 31)

    filename = f"planner_{lang_choice}.{format_choice}"

    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f) if format_choice == "csv" else None

        current_day = start_date
        while current_day <= end_date:
            date_str = format_date_by_lang(current_day, lang_choice)
            tasks = assignments.get(current_day, [])

            if format_choice == "csv":
                if layout_choice == "1":
                    if not tasks:
                        writer.writerow([date_str, ""])
                    for task in tasks:
                        writer.writerow([date_str, task])
                else:
                    writer.writerow([date_str])
                    for task in tasks:
                        writer.writerow([task])
                    writer.writerow([])

            else: # TXT format
                if layout_choice == "1":
                    tasks_text = "\t".join(tasks) if tasks else ""
                    f.write(f"{date_str}\t{tasks_text}\n")
                else:
                    # Vertical list (unchanged)
                    f.write(f"{date_str}\n")
                    for t in tasks:
                        f.write(f"  {t}\n")
                    f.write("\n")

            current_day += timedelta(days=1)

    print(f"Success! Planner saved to {filename}")

if __name__ == "__main__":
    main()
