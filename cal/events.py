# # events.py
#
from datetime import datetime

from auth.authentication import get_credentials  # your existing auth helper
from . import datetime_utils, parser


# _cal = parsedatetime.Calendar()
# DP_SETTINGS = {
#     "TIMEZONE": "America/Denver",
#     "RETURN_AS_TIMEZONE_AWARE": True,
#     "PREFER_DATES_FROM": "future"
# }
#
#
# def extract_datetime(text):
#     # try parsedatetime first (great for relative)
#     dt, status = _cal.parseDT(text, tzinfo=ZoneInfo("America/Denver"))
#     if status > 0:
#         return dt
#     # fallback to dateparser
#     dt2 = dateparser.parse(text, settings=DP_SETTINGS)
#     if dt2 and dt2.tzinfo is None:
#         return dt2.replace(tzinfo=ZoneInfo("America/Denver"))
#     return dt2
#
#
# def parse_input(text: str):
#     # 1) Extract “and call it X” / “called X” / “named X”
#     name_re = re.compile(
#         r'\b(?:call(?:ed)?\s+it|called|named|name\s+it|titled|title\s+it)\b'  # trigger
#         r'\s*'
#         r'(?P<title>'
#         r'"[^"]+"|'  # double‑quoted text
#         r"\'[^\']+\'|"  # single‑quoted text
#         r'\w+'  # or a single word
#         r')',
#         re.IGNORECASE
#     )
#     name_m = name_re.search(text)
#     title = None
#     if name_m:
#         raw = name_m.group('title')  # e.g.  "'test'"
#         title = raw.strip('"\'')  # => "test"
#         text = text[:name_m.start()] + text[name_m.end():]
#
#     # 2) Split off the first date/time keyword (on|at|from|between)
#     split_re = re.compile(r'(.+?)\s+(on|at|from|between|in|event)\s+(.+)', re.IGNORECASE)
#     m = split_re.match(text)
#     if m:
#         summary = m.group(1).strip()
#         when_text = m.group(3).strip()
#     else:
#         summary = text.strip()
#         when_text = None
#
#     # 3) Within when_text, pull out a time‐range if present
#     start_time = end_time = None
#     if when_text:
#         range_re = re.compile(
#             r'from\s+(?P<s>[\d:\sapm]+)\s+(?:to|until|-)\s+(?P<e>[\d:\sapm]+)',
#             re.IGNORECASE
#         )
#         r = range_re.search(when_text)
#         if r:
#             start_time = r.group("s").strip()
#             end_time = r.group("e").strip()
#             when_text = when_text[:r.start()].strip()
#
#         else:
#             at_re = re.compile(r'\bat\s+(?P<s>[\d:\sapm]+)', re.IGNORECASE)
#             a = at_re.search(when_text)
#             if a:
#                 start_time = a.group("s").strip()
#                 when_text = when_text[:a.start()].strip()
#
#     return summary, when_text, start_time, end_time, title


def create_event(title, start, end):
    event_body = {
        'summary': title,
        'start': {'dateTime': start.isoformat()},
        'end': {'dateTime': end.isoformat()},
    }

    service = get_credentials()
    created = service.events().insert(calendarId='primary', body=event_body).execute()
    print(f"Event created: {created.get('htmlLink')}\n")


def view_events(service, parsed: dict, calendar_id: str = 'primary') -> list[dict]:
    title = parsed.get('title') or None
    start = parsed.get('start')
    end = parsed.get('end')
    date_dt = parsed.get('date')

    time_min = time_max = None
    if start and end:
        time_min, time_max = datetime_utils.iso_with_offset(start), datetime_utils.iso_with_offset(end)
    elif date_dt:
        time_min, time_max = datetime_utils.day_bounds(date_dt)

    params = {
        "calendarId": calendar_id,
        "singleEvents": True,      # expand recurring series
        "orderBy": "startTime",
        "maxResults": 50,
    }

    if time_min:
        params["timeMin"] = time_min
    if time_max:
        params["timeMax"] = time_max
    if title:
        params["q"] = title

    params = {
        "calendarId": "primary",
        "singleEvents": True,
        "orderBy": "startTime",
        "timeMin": time_min,
        "timeMax": time_max,
        "maxResults": 100,
    }

    response = service.events().list(**params).execute()

    events = response.get("items", [])
    print(events)

    for event in events:
        start_str = event["start"].get("dateTime")
        end_str = event["end"].get("dateTime")

        if start_str and end_str:
            start_dt = datetime.fromisoformat(start_str)
            end_dt = datetime.fromisoformat(end_str)

            start_fmt = start_dt.strftime("%-I %p")
            end_fmt = end_dt.strftime("%-I %p")

            print(f'{event["summary"]}: {start_fmt} to {end_fmt}')
    print("\n")
    # return events




def delete_events():
    pass