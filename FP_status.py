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
    print("🛰️ Connecting to Canvas...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_text = response.read().decode('utf-8')

    events = raw_text.split("BEGIN:VEVENT")
    all_assignments = []

    # 1. First Pass: Extract data and find categories
    course_data = {} # Format: { 'CS 32': { 'Pset': [list of assignments], 'Quiz': [] } }

    for event in events:
        if "SUMMARY:" in event and "DTSTART" in event:
            summary_line = event.split("SUMMARY:")[1].split("\n")[0].strip()

            # Extract Course and Assignment Name
            course = "Almennt"
            assignment_name = summary_line
            if "[" in summary_line:
                parts = summary_line.rsplit("[", 1)
                assignment_name = parts[0].strip()
                course = parts[1].replace("]", "").strip()

            # Date Extraction
            date_raw = event.split("DTSTART")[1].split(":")[1][:8]
            try:
                y, m, d = int(date_raw[0:4]), int(date_raw[4:6]), int(date_raw[6:8])
                is_date = get_icelandic_date(date(y, m, d))

                # Group by Course and "Keyword"
                if course not in course_data:
                    course_data[course] = {}

                # Determine category (Pset, Hw, Quiz, etc.)
                category = "Other"
                for word in ["Pset", "Hw", "Homework", "Quiz", "Exam", "FP", "Final"]:
                    if word.lower() in assignment_name.lower():
                        category = word
                        break

                if category not in course_data[course]:
                    course_data[course][category] = []

                course_data[course][category].append({
                    "Date": is_date,
                    "Name": assignment_name
                })
            except:
                continue

    # 2. Second Pass: Interactive Weighting
    final_output = []
    print("\n--- ⚖️ WEIGHTING CONFIGURATION ---")

    for course, categories in course_data.items():
        print(f"\n📚 COURSE: {course}")
        for cat_name, items in categories.items():
            count = len(items)
            print(f"   Found {count} assignments for category: '{cat_name}'")

            # Prompt the user
            try:
                total_pct = float(input(f"   What is the TOTAL percentage grade for {cat_name}s? (e.g., 20 for 20%): "))
                individual_weight = (total_pct / 100) / count
            except ValueError:
                individual_weight = 0.0

            for item in items:
                final_output.append({
                    "Dagsetning": item["Date"],
                    "Áfangi": course,
                    "Verkefni": item["Name"],
                    "Vægi": round(individual_weight, 4)
                })

    # 3. Export to CSV
    with open('namsaaetlun.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["Dagsetning", "Áfangi", "Verkefni", "Vægi"])
        writer.writeheader()
        writer.writerows(final_output)

    print(f"\n✅ Success! CSV generated with {len(final_assignments)} weighted assignments.")

if __name__ == "__main__":
    main()
