# cs32-final-project

## Semester Assignment Planner

**Motivation**

Each semester I manually write in my notes app the date of each day of the whole semester and add assignments as a to-do list under the date they are due. I like having my semester planned and to have to-do lists in my notes app (instead of an excel sheet which I know can do this pretty easily), but I want to make this process more efficient. Also, I like to have the months and the day in Icelandic which excel's date function can't do - it's only in english.

**Project Description**

This project is a Python-based tool that connects a iCalendar feed, parses academic assignments, and exports them into a personalized planner. The tool allows users to:
- Localize their planner into Icelandic, Spanish, or French.
- Choose the layout as either a horizontal "spreadsheet" style or a vertical "list" style.
- Choose the file export format as either `.csv` (for Excel/Google Sheets) or `.txt` files.
- Get a continuous timeline by generating a row for every single calendar day, providing space for manual entries on days without assignments.
