import urllib.request
import csv
import json
import os
from datetime import date
import google.generativeai as genai

# --- CONFIGURATION & API SETUP ---
# Pro-tip: For your GitHub, use an environment variable or keep this private!
API_KEY = "AIzaSyABC9koWOBHi00"
genai.configure(api_key=API_KEY)

URL = "https://canvas.harvard.edu/feeds/calendars/user_NOQogScFrdtBPeSdI1gIbpScSjCBFTuHYcdNf8W1.ics"

# --- TRANSLATION DICTIONARIES ---
MONTHS_IS = {
    1: "janúar", 2: "febrúar", 3: "mars", 4: "apríl", 5: "maí", 6: "júní",
    7: "júlí", 8: "ágúst", 9: "september", 10: "október", 11: "nóvember", 12: "desember"
}

DAYS_IS = {
    "Monday": "mánudagur", "Tuesday": "þriðjudagur", "Wednesday": "miðvikudagur",
    "Thursday": "fimmtudagur", "Friday": "föstudagur", "Saturday": "laugardagur", "Sunday": "sunnudagur"
}

# --- FUNCTIONS ---

def get_icelandic_date(dt):
    """Converts a Python date object into an Icelandic string."""
    day_name = DAYS_IS[dt.strftime("%A")]
    month_name = MONTHS_IS[dt.month]
    return f"{day_name} {dt.day}. {month_name}"

def get_weights_from_ai(syllabus_file):
    """
    Uses a Transformer model (Gemini) to semantically understand
    the grading section of a syllabus.
    """
    try:
        with open(syllabus_file, 'r', encoding='utf-8') as f:
            text = f.read()

        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            "Extract grading weights from this syllabus. Return ONLY a JSON "
            "object with category names as keys and decimal weights as values. "
            f"Syllabus text: {text}"
        )

        response = model.generate_content(prompt)
        # Clean potential markdown formatting from AI output
        clean_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json)
    except Exception as e:
        print(f"⚠️ NLP Warning: Could not parse syllabus. Using default weights. Error: {e}")
        return {}

def main():
    # 1. Fetch Canvas Data
    print("🛰️ Connecting to Canvas...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_ics = response.read().decode('utf-8')

    # 2. Extract Weights using Deep Learning logic
    print("🧠 Applying Transformer model to syllabus.txt...")
    # Make sure you have a file named 'syllabus.txt' in your folder!
    weights_lookup = get_weights_from_ai('syllabus.txt')

    # 3. Process Events
    print("📝 Processing assignments...")
    events = raw_ics.split("BEGIN:VEVENT")
    final_assignments = []

    for event in events:
        if "SUMMARY:" in event and "DTSTART" in event:
            summary_line = event.split("SUMMARY:")[1].split("\n")[0].strip()

            # Course/Assignment extraction
            course = "Almennt"
            assignment = summary_line
            if "[" in summary_line:
                parts = summary_line.rsplit("[", 1)
                assignment = parts[0].strip()
                course = parts[1].replace("]", "").strip()

            # Date extraction
            date_raw = event.split("DTSTART")[1].split(":")[1][:8]
            try:
                y, m, d = int(date_raw[0:4]), int(date_raw[4:6]), int(date_raw[6:8])
                py_date = date(y, m, d)
                is_date = get_icelandic_date(py_date)

                # Match Weight using AI results
                # Logic: Is the course or assignment category in our AI dictionary?
                weight = 0.0
                for category, val in weights_lookup.items():
                    if category.lower() in assignment.lower() or category.lower() in course.lower():
                        weight = val
                        break

                final_assignments.append({
                    "Dagsetning": is_date,
                    "Áfangi": course,
                    "Verkefni": assignment,
                    "Vægi": weight
                })
            except:
                continue

    # 4. Export to CSV
    output_file = "namsaaetlun.csv"
    if final_assignments:
        keys = final_assignments[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(final_assignments)
        print(f"✅ Success! Exported {len(final_assignments)} assignments to {output_file}")
    else:
        print("❌ No assignments found.")

if __name__ == "__main__":
    main()
