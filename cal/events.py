# # events.py
#
from datetime import datetime

from auth.authentication import get_credentials  # your existing auth helper
from . import datetime_utils, parser


def create_event(title, start, end):
    event_body = {
            'summary': title,
            'start': {'date': start},
            'end': {'date': end},
        }

    service = get_credentials()
    created = service.events().insert(calendarId='primary', body=event_body).execute()
    print(f"Event created: {created.get('htmlLink')}\n")


# TODO: see if title is involved, if not, use date to look at events.


def view_events(service, parsed: dict, calendar_id: str = 'primary'):

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
    # return events




def delete_events():
    pass