# cs32-final-project: Semester Assignment Planner

## Motivation

Each semester I manually write in my notes app the date of each day of the whole semester and add assignments as a to-do list under the date they are due. I like having my semester planned and to have to-do lists in my notes app (instead of an excel sheet which I know can do this pretty easily), but I want to make this process more efficient. Also, I like to have the months and the day in Icelandic which excel's date function can't do - it's only in english.

## Project Description

This project is a Python-based tool that connects a iCalendar feed, parses academic assignments, and exports them into a personalized planner. The tool allows users to:
- **Localize** their planner into Icelandic, Spanish, or French.
- **Choose the layout** as either a horizontal "spreadsheet" style or a vertical "list" style.
- **Choose the file export format** as either `.csv` (for Excel/Google Sheets) or `.txt` files.
- **Get a continuous timeline** by generating a row for every single calendar day, providing space for manual entries on days without assignments.


## Instructions for Running
1. **Prerequisites**: No external libraries are required (uses standard libraries `urllib`, `csv`, and `datetime`).
2. **Setup**:
   - Save the script as `planner.py`.
   - Paste the iCalendar feed into the URL variable
   - Ensure you are connected to the internet to fetch the live Canvas feed.
3. **Execution**:
   - Open your terminal or IDE (like VS Code).
   - Run the command: `python planner.py`
4. **Configuration**: Follow the on-screen prompts to select your language, layout, and file format.
5. **Output**: The script will generate a file named `planner_[lang].csv` or `planner_[lang].txt` in the same directory.
