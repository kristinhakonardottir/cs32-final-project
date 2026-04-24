import urllib.request
import csv
from datetime import date, timedelta

# Dictionaries (is/es/fr/en) of dictionaries (translations of months and days)
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
    },
    "en": {
        "months": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"},
        "days": {"Monday": "Monday", "Tuesday": "Tuesday", "Wednesday": "Wednesday", "Thursday": "Thursday", "Friday": "Friday", "Saturday": "Saturday", "Sunday": "Sunday"},
    }
}

# The .ics file of the calendar
# URL = "https://canvas.harvard.edu/feeds/calendars/user_NOQogScFrdtBPeSdI1gIbpScSjCBFTuHYcdNf8W1.ics"
URL = "https://calendar.google.com/calendar/ical/a4j4vao234ts6a37q16lctup0k%40group.calendar.google.com/public/basic.ics"


def format_date_by_lang(dt, lang_code):

    """Formats a Python date object into
    a string based on the selected language."""

    lang = LANG_DATA[lang_code]
    day_name = lang["days"][dt.strftime("%A")]
    month_name = lang["months"][dt.month]
    return f"{day_name} {dt.day}. {month_name}"

def get_grouped_assignments(raw_text):

    """Extracts events from the raw .ics
    text and groups them by date."""

    events = raw_text.split("BEGIN:VEVENT")
    grouped_data = {}
    for event in events:
        if "SUMMARY:" in event and "DTSTART" in event:
            summary_line = event.split("SUMMARY:")[1].split("\n")[0].strip()
            date_raw = event.split("DTSTART")[1].split(":")[1][:8]
            try:
                y, m, d = int(date_raw[0:4]), int(date_raw[4:6]), int(date_raw[6:8])
                py_date = date(y, m, d)
                if "[" in summary_line:
                    parts = summary_line.rsplit("[", 1)
                    flipped_summary = f"{parts[1].replace(']', '').strip()}: {parts[0].strip()}"
                else:
                    flipped_summary = summary_line
                if py_date not in grouped_data:
                    grouped_data[py_date] = []
                grouped_data[py_date].append(flipped_summary)
            except:
                continue
    return grouped_data

def main():
    print("--- Configuration Preferences of the Planner---")

    # Language preference
    while True:
        lang_choice = input("Select language (is/es/fr/en): ").lower()
        if lang_choice in LANG_DATA:
            break
        print("Invalid language. Please choose from is, es, fr, or en.")

    # Layout preference
    print("\n--- Layout Options ---")
    print("1: Standard (Date and Task on same row)")
    print("2: Grouped (Date row, Task row below, extra spacing)")
    while True:
        layout_choice = input("Select layout (1 or 2): ")
        if layout_choice in ["1", "2"]:
            break
        print("Invalid layout. Please choose 1 or 2.")

    # File format preference
    while True:
        format_choice = input("\nExport format? (csv/txt): ").lower()
        if format_choice in ["csv", "txt"]:
            break
        print("Invalid format. Please enter 'csv' or 'txt'.")

    # Start date preference
    print("\n--- Date Range ---")
    while True:
        try:
            start_input = input("Enter start date (YYYY-MM-DD): ")
            sy, sm, sd = map(int, start_input.split("-"))
            start_date = date(sy, sm, sd)
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    # End date preference
    while True:
        try:
            end_input = input("Enter end date (YYYY-MM-DD): ")
            ey, em, ed = map(int, end_input.split("-"))
            end_date = date(ey, em, ed)
            if end_date < start_date:
                print("End date cannot be before start date.")
                continue
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    # Get data from URL
    print(f"\nFetching calendar data...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            raw_text = response.read().decode('utf-8')
    except Exception as e:
        print(f"xyz: Error fetching URL: {e}")
        return

    assignments = get_grouped_assignments(raw_text)
    filename = f"planner_{lang_choice}.{format_choice}"

    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f) if format_choice == "csv" else None
        current_day = start_date
        while current_day <= end_date:
            date_str = format_date_by_lang(current_day, lang_choice)
            tasks = assignments.get(current_day, [])

            if format_choice == "csv":
                if layout_choice == "1":
                    if not tasks: writer.writerow([date_str, ""])
                    for task in tasks: writer.writerow([date_str, task])
                else:
                    writer.writerow([date_str])
                    for task in tasks: writer.writerow([task])
                    writer.writerow([])
            else:
                if layout_choice == "1":
                    tasks_text = "\t".join(tasks) if tasks else ""
                    f.write(f"{date_str}\t{tasks_text}\n")
                else:
                    f.write(f"{date_str}\n")
                    for t in tasks: f.write(f"  {t}\n")
                    f.write("\n")
            current_day += timedelta(days=1)

    print(f"Success! Planner saved to {filename}")

if __name__ == "__main__":
    main()
