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
                # We filter for 2026 to stay within the project scope
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

    # --- NEW: User Input for Start Date ---
    print("\n--- Date Range ---")
    while True:
        date_input = input("Enter start date (YYYY-MM-DD) or press Enter for 2026-01-26: ")
        if date_input == "":
            start_date = date(2026, 1, 26)
            break
        try:
            # Splits "2026-01-26" into [2026, 1, 26] and converts to ints
            y, m, d = map(int, date_input.split("-"))
            start_date = date(y, m, d)
            break
        except ValueError:
            print("❌ Invalid format. Please use YYYY-MM-DD (e.g., 2026-04-01)")

    # 2. Getting data
    print(f"\nFetching calendar data...")
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})

    # Adding a basic check for the 404 error we saw earlier
    try:
        with urllib.request.urlopen(req) as response:
            raw_text = response.read().decode('utf-8')
    except Exception as e:
        print(f"❌ Error fetching URL: {e}")
        return

    assignments = get_grouped_assignments(raw_text, lang_choice)

    # 3. Timeline Bounds
    # End date is either the last assignment in the file or May 31st
    end_date = max(assignments.keys()) if assignments else date(2026, 5, 31)

    # Safety check: if start_date is after end_date, adjust it
    if start_date > end_date:
        print("⚠️ Warning: Start date is after the last assignment. Setting end date to start date.")
        end_date = start_date

    filename = f"planner_{lang_choice}.{format_choice}"

    # ... (Rest of the file writing logic remains the same) ...
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
                    f.write(f"{date_str}\n")
                    for t in tasks:
                        f.write(f"  {t}\n")
                    f.write("\n")
            current_day += timedelta(days=1)

    print(f"Success! Planner saved to {filename}")

if __name__ == "__main__":
    main()


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
    print(f"\nFetching calendar data...")
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

