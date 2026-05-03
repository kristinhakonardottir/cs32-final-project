import urllib.request
import csv
import threading
from datetime import date, timedelta
import customtkinter as ctk
from tkinter import messagebox

# ── appearance ────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── language data (unchanged) ─────────────────────────────────────────────────
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

# ── core logic (all unchanged from original) ──────────────────────────────────

def format_date_by_lang(dt, lang_code):
    lang = LANG_DATA[lang_code]
    day_name = lang["days"][dt.strftime("%A")]
    month_name = lang["months"][dt.month]
    if lang_code == "is":
        return f"{day_name} {dt.day}. {month_name}"
    elif lang_code == "es":
        return f"{day_name}, {dt.day} de {month_name}"
    elif lang_code == "fr":
        ordinal = "er" if dt.day == 1 else ""
        return f"{day_name} {dt.day}{ordinal} {month_name}"
    elif lang_code == "en":
        return f"{day_name}, {month_name} {dt.day}"

def get_grouped_assignments(raw_text):
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

def write_planner(filename, format_choice, layout_choice, lang_choice,
                  start_date, end_date, assignments, weight_map):
    """Unchanged file-writing logic from the original script."""
    current_day = start_date
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar="\\") if format_choice == "csv" else None
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
                    f.write(f"{date_str}\t{tasks_text}\n")
                else:
                    f.write(f"{date_str}\n")
                    for t in tasks:
                        weight = weight_map.get(t, "")
                        weight_str = f" [{weight}]" if weight else ""
                        f.write(f"  {t}{weight_str}\n")
                    f.write("\n")
            current_day += timedelta(days=1)

# ── Weight Window ─────────────────────────────────────────────────────────────

class WeightWindow(ctk.CTkToplevel):
    """Second window: shown after fetching, lets user enter weights per assignment."""

    def __init__(self, parent, assignments, on_done):
        super().__init__(parent)
        self.title("Assignment Weights")
        self.geometry("620x560")
        self.resizable(False, False)
        self.grab_set()  # make it modal

        self.on_done = on_done  # callback to call with the finished weight_map

        # Build flat unique assignment list and extract course names (same logic as original)
        self.all_assignments = []
        for task_list in assignments.values():
            for task in task_list:
                if task not in self.all_assignments:
                    self.all_assignments.append(task)

        self.found_courses = sorted(set(
            a.split(":")[0].strip() for a in self.all_assignments if ":" in a
        ))

        # weight_map stores { assignment_label: weight_string }
        self.weight_map = {}
        # entry widgets stored so we can read them on save: { assignment_label: CTkEntry }
        self.weight_entries = {}

        self._build_ui()

    def _build_ui(self):
        # Title
        ctk.CTkLabel(self, text="Assignment Weights",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self, text="Leave a field blank to skip that assignment.",
                     text_color="gray").pack(pady=(0, 10))

        if not self.found_courses:
            ctk.CTkLabel(self, text="No course-tagged assignments found.",
                         text_color="gray").pack(pady=20)
            ctk.CTkButton(self, text="Continue →", command=self._save).pack(pady=10)
            return

        # Scrollable area for all courses + their assignments
        scroll = ctk.CTkScrollableFrame(self, width=570, height=390)
        scroll.pack(padx=20, pady=(0, 10), fill="both", expand=True)

        for course in self.found_courses:
            # Course header label
            ctk.CTkLabel(scroll, text=course,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         anchor="w").pack(fill="x", padx=8, pady=(12, 2))

            course_assignments = [a for a in self.all_assignments
                                  if a.lower().startswith(course.lower() + ":")]

            for assignment in course_assignments:
                # Strip the "Course: " prefix for display to keep it short
                display = assignment.split(":", 1)[1].strip() if ":" in assignment else assignment

                row = ctk.CTkFrame(scroll, fg_color="transparent")
                row.pack(fill="x", padx=8, pady=2)

                ctk.CTkLabel(row, text=display, anchor="w",
                             wraplength=380).pack(side="left", fill="x", expand=True)

                entry = ctk.CTkEntry(row, width=100, placeholder_text="e.g. 20%")
                entry.pack(side="right", padx=(8, 0))
                self.weight_entries[assignment] = entry

        # Save button
        ctk.CTkButton(self, text="Save Weights & Generate →",
                      command=self._save, height=38).pack(pady=12)

    def _save(self):
        """Read all entry fields, validate, build weight_map, call on_done."""
        weight_map = {}
        errors = []

        for assignment, entry in self.weight_entries.items():
            val = entry.get().strip()
            if not val:
                continue  # blank = skip, same as typing "n" in the terminal version
            try:
                float(val.replace("%", "").strip())
                weight_map[assignment] = val
            except ValueError:
                errors.append(f'"{val}" is not a valid weight for: {assignment[:50]}')

        if errors:
            messagebox.showerror("Invalid weights", "\n".join(errors), parent=self)
            return

        self.weight_map = weight_map
        self.destroy()
        self.on_done(weight_map)

# ── Main Window ───────────────────────────────────────────────────────────────

class PlannerApp(ctk.CTk):
    """Main preference window — replaces all the input() prompts from the original."""

    def __init__(self):
        super().__init__()
        self.title("Semester Planner")
        self.geometry("560x700")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Semester Planner",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(22, 2))
        ctk.CTkLabel(self, text="Configure your planner and click Generate.",
                     text_color="gray").pack(pady=(0, 16))

        form = ctk.CTkFrame(self)
        form.pack(padx=28, fill="x")

        def section(text):
            ctk.CTkLabel(form, text=text,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#6ea8fe", anchor="w").pack(fill="x", padx=6, pady=(14, 2))

        def label(text):
            ctk.CTkLabel(form, text=text, anchor="w").pack(fill="x", padx=6, pady=(4, 0))

        # ── Language ──────────────────────────────────────────────────────────
        section("Language")
        self.lang_var = ctk.StringVar(value="en")
        lang_row = ctk.CTkFrame(form, fg_color="transparent")
        lang_row.pack(fill="x", padx=6, pady=4)
        for code, display in [("en", "English"), ("is", "Íslenska"),
                               ("es", "Español"), ("fr", "Français")]:
            ctk.CTkRadioButton(lang_row, text=display,
                               variable=self.lang_var, value=code).pack(side="left", padx=8)

        # ── Layout ────────────────────────────────────────────────────────────
        section("Layout")
        self.layout_var = ctk.StringVar(value="1")
        ctk.CTkRadioButton(form, text="Standard  —  date and task on the same row",
                           variable=self.layout_var, value="1").pack(anchor="w", padx=6, pady=2)
        ctk.CTkRadioButton(form, text="Grouped  —  date row, tasks below with spacing",
                           variable=self.layout_var, value="2").pack(anchor="w", padx=6, pady=2)

        # ── Export format ─────────────────────────────────────────────────────
        section("Export Format")
        self.format_var = ctk.StringVar(value="csv")
        fmt_row = ctk.CTkFrame(form, fg_color="transparent")
        fmt_row.pack(fill="x", padx=6, pady=4)
        ctk.CTkRadioButton(fmt_row, text=".csv  (Excel / Google Sheets)",
                           variable=self.format_var, value="csv").pack(side="left", padx=8)
        ctk.CTkRadioButton(fmt_row, text=".txt  (Notes app)",
                           variable=self.format_var, value="txt").pack(side="left", padx=8)

        # ── Date range ────────────────────────────────────────────────────────
        section("Date Range")
        date_row = ctk.CTkFrame(form, fg_color="transparent")
        date_row.pack(fill="x", padx=6, pady=4)

        ctk.CTkLabel(date_row, text="Start (YYYY-MM-DD)").pack(side="left")
        self.start_entry = ctk.CTkEntry(date_row, width=130, placeholder_text="2025-01-15")
        self.start_entry.pack(side="left", padx=(6, 20))

        ctk.CTkLabel(date_row, text="End (YYYY-MM-DD)").pack(side="left")
        self.end_entry = ctk.CTkEntry(date_row, width=130, placeholder_text="2025-05-15")
        self.end_entry.pack(side="left", padx=6)

        # ── Calendar URLs ─────────────────────────────────────────────────────
        section("Calendar URLs  (up to 5)")
        ctk.CTkLabel(form, text="Paste your .ics feed URL(s) below. Leave unused rows blank.",
                     text_color="gray", anchor="w", wraplength=480).pack(fill="x", padx=6)

        self.url_entries = []
        for i in range(5):
            e = ctk.CTkEntry(form, placeholder_text=f"URL {i+1}")
            e.pack(fill="x", padx=6, pady=3)
            self.url_entries.append(e)

        # ── Status / progress ─────────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=(14, 0))

        # ── Generate button ───────────────────────────────────────────────────
        self.generate_btn = ctk.CTkButton(
            self, text="Fetch Calendar & Continue →",
            height=42, font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_generate)
        self.generate_btn.pack(pady=14)

    # ── validation & fetch ────────────────────────────────────────────────────

    def _set_status(self, text, color="gray"):
        self.status_label.configure(text=text, text_color=color)
        self.update_idletasks()

    def _on_generate(self):
        """Validate inputs, then fetch calendars in a background thread."""

        # Validate dates
        try:
            sy, sm, sd = map(int, self.start_entry.get().strip().split("-"))
            start_date = date(sy, sm, sd)
        except:
            messagebox.showerror("Invalid date", "Start date must be YYYY-MM-DD.")
            return
        try:
            ey, em, ed = map(int, self.end_entry.get().strip().split("-"))
            end_date = date(ey, em, ed)
        except:
            messagebox.showerror("Invalid date", "End date must be YYYY-MM-DD.")
            return
        if end_date < start_date:
            messagebox.showerror("Invalid range", "End date cannot be before start date.")
            return

        # Collect URLs
        urls = [e.get().strip() for e in self.url_entries if e.get().strip()]
        if not urls:
            messagebox.showerror("No URLs", "Please enter at least one calendar URL.")
            return

        # Store validated preferences
        self._prefs = {
            "lang":   self.lang_var.get(),
            "layout": self.layout_var.get(),
            "format": self.format_var.get(),
            "start":  start_date,
            "end":    end_date,
            "urls":   urls,
        }

        self.generate_btn.configure(state="disabled")
        self._set_status("Fetching calendar data…")

        # Fetch in a thread so the window doesn't freeze
        threading.Thread(target=self._fetch_thread, daemon=True).start()

    def _fetch_thread(self):
        """Runs in background — fetches and merges all ICS feeds."""
        urls = self._prefs["urls"]
        assignments = {}
        errors = []

        for i, url in enumerate(urls, 1):
            self.after(0, self._set_status, f"Fetching source {i} of {len(urls)}…")
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
                errors.append(f"URL {i}: {e}")

        # Hand results back to the main thread
        self.after(0, self._fetch_done, assignments, errors)

    def _fetch_done(self, assignments, errors):
        """Called on main thread after fetch completes."""
        self.generate_btn.configure(state="normal")

        if errors:
            messagebox.showwarning("Some URLs failed",
                                   "Could not fetch:\n" + "\n".join(errors))

        if not assignments:
            self._set_status("No assignments found. Check your URLs.", color="#ff6b6b")
            return

        count = sum(len(v) for v in assignments.values())
        self._set_status(f"✓ Fetched {count} assignment(s). Opening weights window…", color="#6bcb77")

        self._assignments = assignments
        # Open the weights window; pass _generate as the callback
        WeightWindow(self, assignments, on_done=self._generate)

    # ── file generation ───────────────────────────────────────────────────────

    def _generate(self, weight_map):
        """Called after the weight window closes — writes the output file."""
        p = self._prefs
        filename = f"planner_{p['lang']}.{p['format']}"

        try:
            write_planner(
                filename=filename,
                format_choice=p["format"],
                layout_choice=p["layout"],
                lang_choice=p["lang"],
                start_date=p["start"],
                end_date=p["end"],
                assignments=self._assignments,
                weight_map=weight_map,
            )
            self._set_status(f"✓ Saved as {filename}", color="#6bcb77")
            messagebox.showinfo("Done!", f"Planner saved as:\n{filename}")
        except Exception as e:
            self._set_status("Error writing file.", color="#ff6b6b")
            messagebox.showerror("Error", str(e))

# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = PlannerApp()
    app.mainloop()
