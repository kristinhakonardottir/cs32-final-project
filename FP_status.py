import urllib.request
import csv
from datetime import date

# Translation Dictionaries
MONTHS_IS = {
    1: "janúar", 2: "febrúar", 3: "mars", 4: "apríl", 5: "maí", 6: "júní",
    7: "júlí", 8: "ágúst", 9: "september", 10: "október", 11: "nóvember", 12: "desember"
}

DAYS_IS = {
    "Monday": "mánudagur", "Tuesday": "þriðjudagur", "Wednesday": "miðvikudagur",
    "Thursday": "fimmtudagur", "Friday": "föstudagur", "Saturday": "laugardagur", "Sunday": "sunnudagur"
}

URL = "https://canvas.harvard.edu/feeds/calendars/user_NOQogScFrdtBPeSdI1gIbpScSjCBFTuHYcdNf8W1.ics"

def get_icelandic_date(dt):
    day_name = DAYS_IS[dt.strftime("%A")]
    month_name = MONTHS_IS[dt.month]
    return f"{day_name} {dt.day}. {month_name}"

def main():
    # 1. FETCH DATA
    print("🛰️ Connecting to Canvas...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_text = response.read().decode('utf-8')

    events = raw_text.split("BEGIN:VEVENT")

    # We will organize assignments by course name in a dictionary
    # Structure: { "CS 32": [list of assignment dictionaries], ... }
    course_catalog = {}

    # 2. PARSE DATA
    for event in events:
        if "SUMMARY:" in event and "DTSTART" in event:
            summary_line = event.split("SUMMARY:")[1].split("\n")[0].strip()

            course = "Almennt"
            assignment = summary_line
            if "[" in summary_line:
                parts = summary_line.rsplit("[", 1)
                assignment = parts[0].strip()
                course = parts[1].replace("]", "").strip()

            date_raw = event.split("DTSTART")[1].split(":")[1][:8]
            try:
                y, m, d = int(date_raw[0:4]), int(date_raw[4:6]), int(date_raw[6:8])
                py_date = date(y, m, d)

                # Filtering to ensure we only see 2026 assignments
                if y != 2026:
                    continue

                if course not in course_catalog:
                    course_catalog[course] = []

                course_catalog[course].append({
                    "date_obj": py_date,
                    "is_date": get_icelandic_date(py_date),
                    "name": assignment
                })
            except:
                continue

    # 3. INTERACTIVE WEIGHTING
    final_data = []
    print("\n--- ⚖️ INTERACTIVE WEIGHTING ---")

    # Sort courses alphabetically for the user
    for course_name in sorted(course_catalog.keys()):
        assignments = course_catalog[course_name]
        # Sort assignments by date so it's easier for the user to read
        assignments.sort(key=lambda x: x["date_obj"])

        print(f"\n📚 COURSE: {course_name}")
        print(f"Found {len(assignments)} assignments:")

        for item in assignments:
            print(f"   - {item['is_date']}: {item['name']}")

        # Now ask for weights
        for item in assignments:
            prompt = f"   → Enter weight for '{item['name']}' (e.g. 0.05 for 5%): "
            weight_input = input(prompt)

            try:
                weight = float(weight_input)
            except ValueError:
                weight = 0.0 # Default if they just hit enter

            final_data.append({
                "Dagsetning": item["is_date"],
                "Áfangi": course_name,
                "Verkefni": item["name"],
                "Vægi": weight
            })

    # 4. EXPORT TO CSV
    output_file = "namsaaetlun.csv"
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["Dagsetning", "Áfangi", "Verkefni", "Vægi"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_data)

    print(f"\n✅ All set! Your weighted planner is saved to {output_file}")

if __name__ == "__main__":
    main()
