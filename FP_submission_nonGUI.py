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

def format_date_by_lang(dt, lang_code):

    """Formats a Python date object into a string based on the selected language.
    Each language uses its own conventional date order and punctuation:
      is: mánudagur 1. janúar
      es: lunes 1 de enero
      fr: lundi 1er janvier
      en: Monday January 1
    """

    lang = LANG_DATA[lang_code]
    day_name = lang["days"][dt.strftime("%A")]
    month_name = lang["months"][dt.month]

    if lang_code == "is":
        return f"{day_name} {dt.day}. {month_name}"

    elif lang_code == "es":
        return f"{day_name} {dt.day} de {month_name}"

    elif lang_code == "fr":
        ordinal = "er" if dt.day == 1 else ""
        return f"{day_name} {dt.day}{ordinal} {month_name}"

    elif lang_code == "en":
        return f"{day_name} {month_name} {dt.day}"

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


def collect_weights(assignments):

    """Asks the user if they want to add weights to any assignments.
    Loops through courses and assignments until the user is done.
    Returns a dict mapping assignment label -> weight string (or None)."""

    all_assignments = []
    for task_list in assignments.values():
        for task in task_list:
            if task not in all_assignments:
                all_assignments.append(task)

    found_courses = sorted(set(
        a.split(":")[0].strip() for a in all_assignments if ":" in a
    ))

    print("\n--- Assignment Weights ---")
    if found_courses:
        print("The following courses were found in your calendar:")
        for course in found_courses:
            print(f"  - {course}")
    else:
        print("No course-tagged assignments were found.")

    while True:
        add_weights = input("\nDo you want to add weights to any assignments? (yes/no): ").strip().lower()
        if add_weights in ["yes", "no", "y", "n"]:
            break
        print("Please enter yes or no.")

    if add_weights in ["no", "n"]:
        return {}

    weight_map = {}

    while True:
        course_name = input("\nEnter the course name to add weights for (or 'done' to finish): ").strip()

        if course_name.lower() == "done":
            break

        course_assignments = [a for a in all_assignments if a.lower().startswith(course_name.lower() + ":")]

        if not course_assignments:
            print(f"  No assignments found for course '{course_name}'. Check the spelling.")
            continue

        print(f"  Found {len(course_assignments)} assignment(s) for '{course_name}'.")
        print("  For each assignment, enter a weight (e.g. 0.2 or 20%) or 'n' to skip.\n")

        for assignment in course_assignments:
            while True:
                weight_input = input(f"  {assignment}\n  Weight (or n to skip): ").strip()

                if weight_input.lower() == "n":
                    break

                try:
                    cleaned = weight_input.replace("%", "").strip()
                    float(cleaned)
                    weight_map[assignment] = weight_input
                    break
                except ValueError:
                    print("  Invalid input. Enter a number (e.g. 0.2 or 20%) or 'n' to skip.")

        while True:
            another = input("\nAdd weights for another course? (yes/no): ").strip().lower()
            if another in ["yes", "no", "y", "n"]:
                break
            print("Please enter yes or no.")

        if another in ["no", "n"]:
            break

    return weight_map


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
    print("\n--- Export Format Options ---")
    while True:
        format_choice = input("Export format? (csv/txt): ").lower()
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

    # Collect up to 5 ICS URLs from the user
    print("\n--- Calendar Sources ---")
    print("Enter up to 5 .ics calendar URLs. Press Enter with no input when you are done.")
    urls = []
    for i in range(1, 6):
        url_input = input(f"  ICS URL {i} (or press Enter to finish): ").strip()
        if not url_input:
            break
        urls.append(url_input)

    if not urls:
        print("No URLs entered. Exiting.")
        return

    # Fetch each URL and merge all events into one combined assignments dict
    print(f"\nFetching calendar data from {len(urls)} source(s)...")
    assignments = {}
    for i, url in enumerate(urls, 1):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                raw_text = response.read().decode('utf-8')
            print(f"  [{i}/{len(urls)}] OK — {url[:60]}{'...' if len(url) > 60 else ''}")
        except Exception as e:
            # If one URL fails, warn and skip it rather than aborting everything
            print(f"  [{i}/{len(urls)}] Failed to fetch: {e}. Skipping.")
            continue

        # Merge this calendar's events into the combined dict
        # get_grouped_assignments is called once per URL and results are merged by date
        partial = get_grouped_assignments(raw_text)
        for day, tasks in partial.items():
            if day not in assignments:
                assignments[day] = []
            for task in tasks:
                if task not in assignments[day]:  # avoid duplicates if same event appears in two feeds
                    assignments[day].append(task)

    if not assignments:
        print("No assignments found in any of the provided calendars.")
        return

    # Call weight collection after data is fetched
    weight_map = collect_weights(assignments)

    filename = f"planner_{lang_choice}.{format_choice}"

    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar="\\") if format_choice == "csv" else None
        current_day = start_date
        while current_day <= end_date:
            date_str = format_date_by_lang(current_day, lang_choice)
            tasks = assignments.get(current_day, [])

            if format_choice == "csv":
                if layout_choice == "1":
                    if not tasks: writer.writerow([date_str, ""])
                    for task in tasks:
                        weight = weight_map.get(task, "")  # look up weight for this task
                        task_str = f"{task} [{weight}]" if weight else task  # weight now formatted in bracket inside task cell
                        writer.writerow([date_str, task_str])
                else:
                    writer.writerow([date_str])
                    for task in tasks:
                        weight = weight_map.get(task, "")  # look up weight for this task
                        task_str = f"{task} [{weight}]" if weight else task  # Cweight now formatted in bracket inside task cell
                        writer.writerow([task_str])
                    writer.writerow([])
            else:
                if layout_choice == "1":
                    # build task strings that include weight if available, then join
                    task_parts = []
                    for task in tasks:
                        weight = weight_map.get(task, "")
                        task_parts.append(f"{task} [{weight}]" if weight else task)
                    tasks_text = "\t".join(task_parts) if task_parts else ""
                    f.write(f"{date_str}\t{tasks_text}\n")
                else:
                    f.write(f"{date_str}\n")
                    for t in tasks:
                        weight = weight_map.get(t, "")
                        weight_str = f" [{weight}]" if weight else ""
                        f.write(f"  {t}{weight_str}\n")
                    f.write("\n")
            current_day += timedelta(days=1)

    print(f"Success! Planner saved to {filename}")

if __name__ == "__main__":
    main()
