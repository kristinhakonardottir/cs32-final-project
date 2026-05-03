# cs32-final-project: Semester Assignment Planner

## Motivation

Each semester I manually write in my notes app the date of each day of the whole semester and add assignments as a to-do list under the date they are due. I like having my semester planned and to have to-do lists in my notes app (instead of an excel sheet which I know can do this pretty easily), but I want to make this process more efficient. Also, I like to have the months and the day in Icelandic which excel's date function can't do - it's only in english.

## Project Description

This project is a Python-based tool that connects a iCalendar feed, parses academic assignments, and exports them into a personalized planner. The tool allows users to:
- **Choose the language** of their planner from English, Icelandic, Spanish, or French.
- **Choose the layout** as either a horizontal "spreadsheet" style or a vertical "list" style.
- **Choose the file export format** as either `.csv` (for Excel/Google Sheets) or `.txt` files.
- **Get a continuous timeline** by generating a row for every single calendar day, providing space for manual entries on days without assignments.


## Instructions for Running
1. **Prerequisites**: No external libraries are required (uses standard libraries `urllib`, `csv`, and `datetime`).
2. **Setup**:
   - Save the script as `planner.py`.
   - Paste the iCalendar feed into the URL variable
3. **Execution**:
   - Open your terminal or IDE (like VS Code).
   - Run the command: `python planner.py`
4. **Configuration**: Follow the on-screen prompts to select your language, layout, and file format.
5. **Output**: The script will generate a file named `planner_[lang].csv` or `planner_[lang].txt` in the same directory.

### Generative AI Disclosure
I used Gemini to assist me while I developed this project. It helped me with:
- The format_date_by_lang function
- The get_grouped_assignments function
- The collect_weights function
- How the .ics file looks like, finding the keywords that signal the assignment name and date
- How to use the urllib library
- How to format the "spreadsheet" style and the "list" style
- How to use the datetime library
- Adding support for up to 5 URLs

I wrote the indexing of assignments and dates, the print statements, and the user inputs myself. For the "if/else" statements, functions and the main function, I wrote the logic myself, then I prompted Gemini asking how to translate it into an efficient python code.

The code blocks Gemini wrote for me and I copied are:
- The LANG_DATA dictionary as it is more efficient for GAI to write such dictionary of dictionary with languages I don't speak (french and spanish)
- The "getting data" from Canvas using the "urllib" library
- The date code in the format_date_by_lang function
- 

