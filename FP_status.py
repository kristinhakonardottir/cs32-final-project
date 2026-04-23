import urllib.request
import csv
from datetime import date

# --- TRANSLATION MASTER DATABASE ---
LANG_DATA = {
    "is": { # Icelandic
        "months": {1: "janúar", 2: "febrúar", 3: "mars", 4: "apríl", 5: "maí", 6: "júní", 7: "júlí", 8: "ágúst", 9: "september", 10: "október", 11: "nóvember", 12: "desember"},
        "days": {"Monday": "mánudagur", "Tuesday": "þriðjudagur", "Wednesday": "miðvikudagur", "Thursday": "fimmtudagur", "Friday": "föstudagur", "Saturday": "laugardagur", "Sunday": "sunnudagur"},
        "headers": ["Dagsetning", "Áfangi", "Verkefni"]
    },
    "es": { # Spanish
        "months": {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio", 7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"},
        "days": {"Monday": "lunes", "Tuesday": "martes", "Wednesday": "miércoles", "Thursday": "jueves", "Friday": "viernes", "Saturday": "sábado", "Sunday": "domingo"},
        "headers": ["Fecha", "Curso", "Tarea"]
    },
    "fr": { # French
        "months": {1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin", 7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"},
        "days": {"Monday": "lundi", "Tuesday": "mardi", "Wednesday": "mercredi", "Thursday": "jeudi", "Friday": "vendredi", "Saturday": "samedi", "Sunday": "dimanche"},
        "headers": ["Date", "Cours", "Devoir"]
    },
    "zh": { # Mandarin (Simplified)
        "months": {1: "一月", 2: "二月", 3: "三月", 4: "四月", 5: "五月", 6: "六月", 7: "七月", 8: "八月", 9: "九月", 10: "十月", 11: "十一月", 12: "十二月"},
        "days": {"Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三", "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六", "Sunday": "星期日"},
        "headers": ["日期", "课程", "作业"]
    }
}

URL = "https://canvas.harvard.edu/feeds/calendars/user_NOQogScFrdtBPeSdI1gIbpScSjCBFTuHYcdNf8W1.ics"

def format_date_by_lang(dt, lang_code):
    """Formats date based on selected language."""
    lang = LANG_DATA[lang_code]
    day_name = lang["days"][dt.strftime("%A")]
    month_name = lang["months"][dt.month]

    if lang_code == "zh":
        return f"{dt.year}年{month_name}{dt.day}日 ({day_name})"
    return f"{day_name} {dt.day}. {month_name}"

def main():
    # 1. USER INPUTS
    print("--- 🌍 Language Options ---")
    print("is: Icelandic | es: Spanish | fr: French | zh: Mandarin")
    lang_choice = input("Select language code (is/es/fr/zh): ").lower()
    if lang_choice not in LANG_DATA: lang_choice = "is"

    format_choice = input("Export format? (csv/txt): ").lower()

    # 2. FETCH DATA
    print(f"\n🛰️ Connecting to Canvas...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_text = response.read().decode('utf-8')

    events = raw_text.split("BEGIN:VEVENT")
    parsed_data = []

    # 3. PARSE DATA
    for event in events:
        if "SUMMARY:" in event and "DTSTART" in event:
            summary_line = event.split("SUMMARY:")[1].split("\n")[0].strip()

            course = "General" if lang_choice != "is" else "Almennt"
            assignment = summary_line
            if "[" in summary_line:
                parts = summary_line.rsplit("[", 1)
                assignment = parts[0].strip()
                course = parts[1].replace("]", "").strip()

            date_raw = event.split("DTSTART")[1].split(":")[1][:8]
            try:
                y, m, d = int(date_raw[0:4]), int(date_raw[4:6]), int(date_raw[6:8])
                py_date = date(y, m, d)

                # Filter for 2026
                if y != 2026: continue

                translated_date = format_date_by_lang(py_date, lang_choice)
                parsed_data.append([translated_date, course, assignment])
            except:
                continue

    # 4. EXPORT DATA
    filename = f"assignments_{lang_choice}.{format_choice}"
    headers = LANG_DATA[lang_choice]["headers"]

    if format_choice == "csv":
        # 'utf-8-sig' ensures characters like ð, é, and 中文 show up in Excel
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(parsed_data)
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{' | '.join(headers)}\n")
            f.write("-" * 50 + "\n")
            for row in parsed_data:
                f.write(f"{row[0]} | {row[1]}: {row[2]}\n")

    print(f"✅ Success! Data exported to {filename}")

if __name__ == "__main__":
    main()
