import urllib.request
import csv
import io
from datetime import date, timedelta
import streamlit as st

# Page configuration
st.set_page_config(page_title="Semester Planner", page_icon="📅", layout="centered")

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

def build_planner_bytes(format_choice, layout_choice, lang_choice,
                        start_date, end_date, assignments, weight_map):

    """Same file-writing logic as earlier versions, but writes to a bytes buffer
    instead of a file so Streamlit can offer it as a download."""

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONE, escapechar="\\") if format_choice == "csv" else None

    current_day = start_date
    while current_day <= end_date:
        date_str = format_date_by_lang(current_day, lang_choice)
        tasks = assignments.get(current_day, [])

        if format_choice == "csv":
            if layout_choice == "1":
                if not tasks:
                    writer.writerow([date_str, ""])
                for task in tasks:
                    weight = weight_map.get(task, "")
                    task_str = f"{task} [{weight}]" if weight else task
                    writer.writerow([date_str, task_str])
            else:
                writer.writerow([date_str])
                for task in tasks:
                    weight = weight_map.get(task, "")
                    task_str = f"{task} [{weight}]" if weight else task
                    writer.writerow([task_str])
                writer.writerow([])
        else:
            if layout_choice == "1":
                task_parts = []
                for task in tasks:
                    weight = weight_map.get(task, "")
                    task_parts.append(f"{task} [{weight}]" if weight else task)
                tasks_text = "\t".join(task_parts) if task_parts else ""
                output.write(f"{date_str}\t{tasks_text}\n")
            else:
                output.write(f"{date_str}\n")
                for t in tasks:
                    weight = weight_map.get(t, "")
                    weight_str = f" [{weight}]" if weight else ""
                    output.write(f"{t}{weight_str}\n")
                output.write("\n")

        current_day += timedelta(days=1)

    return output.getvalue().encode("utf-8-sig")

# Streamlit UI

st.title("📅 Semester Planner")
st.caption("Connect your calendar, choose your preferences, and download your planner.")

# Streamlit reruns top to bottom on every interaction, so we use
# st.session_state to remember things across reruns (fetched assignments, etc.)
if "assignments" not in st.session_state:
    st.session_state.assignments = None
if "fetch_errors" not in st.session_state:
    st.session_state.fetch_errors = []

# Section 1: Preferences
st.subheader("1 · Preferences")

col1, col2, col3 = st.columns(3)

with col1:
    lang_choice = st.radio(
        "Language",
        options=["en", "is", "es", "fr"],
        format_func=lambda x: {"en": "English", "is": "Íslenska", "es": "Español", "fr": "Français"}[x],
    )

with col2:
    layout_choice = st.radio(
        "Layout",
        options=["1", "2"],
        format_func=lambda x: "Standard (same row)" if x == "1" else "Grouped (date then tasks)",
    )

with col3:
    format_choice = st.radio(
        "Export format",
        options=["csv", "txt"],
        format_func=lambda x: ".csv  (Excel / Sheets)" if x == "csv" else ".txt  (Notes app)",
    )

# Section 2: Date Range
st.subheader("2 · Date Range")

col_s, col_e = st.columns(2)
with col_s:
    start_date = st.date_input("Start date", value=date.today())
with col_e:
    end_date = st.date_input("End date", value=date(date.today().year, 12, 31))

if end_date < start_date:
    st.error("End date cannot be before start date.")
    st.stop()

# Section 3: Calendar URLs
st.subheader("3 · Calendar URLs")
st.caption("Paste up to 5 .ics feed URLs. Leave unused fields blank.")

url_entries = []
for i in range(5):
    url = st.text_input(f"URL {i+1}", key=f"url_{i}", placeholder="https://calendar.google.com/calendar/ical/...")
    if url.strip():
        url_entries.append(url.strip())

# Fetch button
st.divider()

if st.button("📥  Fetch Calendar Data", type="primary", use_container_width=True):
    if not url_entries:
        st.error("Please enter at least one calendar URL.")
    else:
        assignments = {}
        errors = []
        progress = st.progress(0, text="Starting…")

        for i, url in enumerate(url_entries):
            progress.progress((i) / len(url_entries), text=f"Fetching source {i+1} of {len(url_entries)}…")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urllib.request.urlopen(req) as resp:
                    raw_text = resp.read().decode("utf-8")
                partial = get_grouped_assignments(raw_text)
                for day, tasks in partial.items():
                    if day not in assignments:
                        assignments[day] = []
                    for task in tasks:
                        if task not in assignments[day]:
                            assignments[day].append(task)
            except Exception as e:
                errors.append(f"URL {i+1}: {e}")

        progress.progress(1.0, text="Done!")

        st.session_state.assignments = assignments
        st.session_state.fetch_errors = errors

        if errors:
            for err in errors:
                st.warning(f"Could not fetch — {err}")

        if assignments:
            total = sum(len(v) for v in assignments.values())
            st.success(f"✓ Fetched {total} assignment(s) across {len(assignments)} day(s).")
        else:
            st.error("No assignments found. Check your URLs.")

# Section 4: Weights (shown only after a successful fetch)
if st.session_state.assignments:
    assignments = st.session_state.assignments

    # Build flat unique assignment list and course names
    all_assignments = []
    for task_list in assignments.values():
        for task in task_list:
            if task not in all_assignments:
                all_assignments.append(task)

    found_courses = sorted(set(
        a.split(":")[0].strip() for a in all_assignments if ":" in a
    ))

    st.subheader("4 · Assignment Weights  *(optional)*")

    add_weights = st.toggle("Add weights to assignments")
    weight_map = {}

    if add_weights:
        if not found_courses:
            st.info("No course-tagged assignments found in your calendar.")
        else:
            st.caption("Enter a weight (e.g. 20% or 0.2) next to each assignment. Leave blank to skip.")

            for course in found_courses:
                with st.expander(f"📚 {course}", expanded=True):
                    course_assignments = [
                        a for a in all_assignments
                        if a.lower().startswith(course.lower() + ":")
                    ]
                    for assignment in course_assignments:
                        display = assignment.split(":", 1)[1].strip() if ":" in assignment else assignment
                        col_a, col_w = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"<small>{display}</small>", unsafe_allow_html=True)
                        with col_w:
                            val = st.text_input(
                                "Weight",
                                key=f"w_{assignment}",
                                placeholder="e.g. 20%",
                                label_visibility="collapsed",
                            )
                        if val.strip():
                            try:
                                float(val.strip().replace("%", ""))
                                weight_map[assignment] = val.strip()
                            except ValueError:
                                st.error(f'"{val}" is not a valid weight for: {display}')

    # Generate & Download
    st.divider()
    st.subheader("5 · Generate & Download")

    filename = f"planner_{lang_choice}.{format_choice}"
    mime = "text/csv" if format_choice == "csv" else "text/plain"

    try:
        file_bytes = build_planner_bytes(
            format_choice=format_choice,
            layout_choice=layout_choice,
            lang_choice=lang_choice,
            start_date=start_date,
            end_date=end_date,
            assignments=assignments,
            weight_map=weight_map,
        )

        st.download_button(
            label=f"⬇️  Download {filename}",
            data=file_bytes,
            file_name=filename,
            mime=mime,
            type="primary",
            use_container_width=True,
        )

    except Exception as e:
        st.error(f"Error generating file: {e}")
