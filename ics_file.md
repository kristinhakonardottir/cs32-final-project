code

import urllib.request

# 1. Connect to the file
response = urllib.request.urlopen("https://canvas.harvard.edu/feeds/calendars/user_NOQogScFrdtBPeSdI1gIbpScSjCBFTuHYcdNf8W1.ics")

# 2. Read it and turn it into text
raw_text = response.read().decode('utf-8')

# 3. SHOW ME WHAT'S INSIDE (The "Discovery" line)
print(raw_text[:800])

BEGIN:VCALENDAR
VERSION:2.0
PRODID:icalendar-ruby
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Kristin Hakonardottir Calendar (Canvas)
X-WR-CALDESC:Calendar events for the user\, Kristin Hakonardottir
BEGIN:VEVENT
DTSTAMP:20260309T191000Z
UID:event-assignment-997543
DTSTART;VALUE=DATE;VALUE=DATE:20260309
CLASS:PUBLIC
DESCRIPTION:Please complete this assignment on [Gradescope] (https://www.gr
 adescope.com/courses/1067838/assignments/6559558).
SEQUENCE:0
SUMMARY:Hw #9: Big-O understanding [COMPSCI 32]
URL;VALUE=URI:https://canvas.harvard.edu/calendar?include_contexts=course_1
 63449&month=03&year=2026#assignment_997543
X-ALT-DESC;FMTTYPE=text/html:<p>Please complete this assignment on <a class
 ="inline_disabled" href="https://www.gradescope.com/courses/1067838/assign

/workspaces/cs32-final-project/ $
