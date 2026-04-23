import urllib.request
import csv
from datetime import date, timedelta
import os

# --- Configuration & Data ---
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

# Testing with a verified public calendar URL
URL = "https://canvas.harvard.edu/feeds/calendars/user_NOQogScFrdtBPeSdI1gIbpScSjCBFTuHYcdNf8W1.ics"

def format_date_by_lang(dt, lang_code):
    lang = LANG_DATA[lang_code]
    day_name = lang["days"][dt.strftime("%A")]
    month_name = lang["months"][dt.month]
    return f"{day_name} {dt.day}. {month_name}"

def get_grouped_assignments(raw_text):
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

                # Format summary if it has brackets [Course]
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
    # 1. User Inputs
    print("--- 🛠️ Planner Configuration ---")
    lang_choice = input("Select language (is/es/fr): ").lower()

    date_input = input("Enter start date (YYYY-MM-DD): ")
    y, m, d = map(int, date_input.split("-"))
    start_date = date(y, m, d)

    print("\n--- 📂 Export Options ---")
    print("Formats: csv, txt, html, notes (Direct to Apple Notes)")
    format_choice = input("Select export format: ").lower()

    # 2. Fetch Data
    print(f"\n📡 Fetching calendar data...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            raw_text = response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    assignments = get_grouped_assignments(raw_text)
    end_date = max(assignments.keys()) if assignments else start_date + timedelta(days=14)

    # 3. Processing
    filename = f"planner_{lang_choice}.{format_choice}"
    note_body = f"<h1>Planner ({start_date} to {end_date})</h1>"

    # CSV setup if needed
    f = open(filename, 'w', encoding='utf-8-sig', newline='') if format_choice != "notes" else None
    writer = csv.writer(f) if format_choice == "csv" else None

    if format_choice == "html":
        f.write("<html><body style='font-family:sans-serif;'>\n")

    current_day = start_date
    while current_day <= end_date:
        date_str = format_date_by_lang(current_day, lang_choice)
        tasks = assignments.get(current_day, [])

        # Logic for Apple Notes or HTML
        day_html = f"<h3>{date_str}</h3><ul>"
        if not tasks:
            day_html += "<li>[ ] <i>Ekkert skráð</i></li>"
        for t in tasks:
            day_html += f"<li>[ ] {t}</li>"
        day_html += "</ul>"

        if format_choice in ["html", "notes"]:
            note_body += day_html
            if format_choice == "html":
                f.write(day_html + "<hr>\n")

        elif format_choice == "csv":
            writer.writerow([date_str])
            for t in tasks: writer.writerow([f"[ ] {t}"])
            writer.writerow([])

        elif format_choice == "txt":
            f.write(f"{date_str}\n")
            for t in tasks: f.write(f"  [ ] {t}\n")
            f.write("\n")

        current_day += timedelta(days=1)

    # 4. Finalizing
    if format_choice == "notes":
        print("🍎 Sending to Apple Notes...")
        clean_body = note_body.replace('"', '\\"').replace('\n', '')
        applescript = f'tell application "Notes" to make new note with properties {{body:"{clean_body}"}}'
        os.system(f"osascript -e '{applescript}'")
        print("✨ Check your Notes app!")
    else:
        if format_choice == "html": f.write("</body></html>")
        f.close()
        print(f"✅ Success! Saved to {filename}")

if __name__ == "__main__":
    main()
