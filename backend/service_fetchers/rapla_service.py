import requests
from .helpers import is_valid_date

# Schedule (Rapla API)
#
# Parameters:
# - dates (list of str): List of dates (in "YYYY-MM-DD" format) for which to retrieve events
#
# Returns:
# - dict: Maps each event summary to a dictionary containing:
#     - "start" (str): Event start time in "HH:MM" format
#     - "end" (str): Event end time in "HH:MM" format
#     - "location" (str): Event location
def get_rapla_schedule(dates):
    url = (
        "http://rapla.satoqz.net/rapla/internal_calendar?"
        "key=6Q0QSbNtpyeYPKQhnGFTaEN6AggaPdGgCFyhd5ANmjydX8WyDjUfLBh4YjDgat2dJd8as6Az5GGmQilBwJydDTQpeHfV6bTghpX2dlRU6RU5QsAKr6ARjgRj_BxZmmhVA3Tk_bSK4acN3oO7a7PkNAHTfszb0OA4_JMp8zdoYDY"
        "&salt=648736798"
    )
    response = requests.get(url)
    ics_file = response.text

    current_event = {}
    events = {}
    
    # Iterates through all lines of the given ICS file
    for date in dates:
        date = is_valid_date(date)
        for line in ics_file.splitlines():
            line = line.strip()

            if line.startswith("BEGIN:VEVENT"):
                current_event = {}

            elif line.startswith("DTSTAMP:"):
                timestamp = line.replace("DTSTAMP:", "").strip().split("T")[0]
                current_event["timestamp"] = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:]}"

            elif line.startswith("SUMMARY:"):
                current_event["summary"] = line.replace("SUMMARY:", "").strip()

            elif line.startswith("DTSTART;TZID=Europe/Berlin:"):
                start_time = line.replace("DTSTART;TZID=Europe/Berlin:", "").strip().split("T")[1]
                current_event["start"] = f"{start_time[:2]}:{start_time[2:4]}"

            elif line.startswith("DTEND;TZID=Europe/Berlin:"):
                end_time = line.replace("DTEND;TZID=Europe/Berlin:", "").strip().split("T")[1]
                current_event["end"] = f"{end_time[:2]}:{end_time[2:4]}"

            elif line.startswith("LOCATION:"):
                current_event["location"] = line.replace("LOCATION:", "").strip()

            elif line.startswith("END:VEVENT"):
                if "summary" in current_event and current_event["timestamp"] == date:
                    events[current_event["summary"]] = {
                        "start": current_event.get("start"),
                        "end": current_event.get("end"),
                        "location": current_event.get("location"),
                    }

    return events