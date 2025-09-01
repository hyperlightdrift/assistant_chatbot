import re
from datetime import timedelta, datetime
from . import datetime_utils
import dateparser
import parsedatetime
from zoneinfo import ZoneInfo
from dateutil import tz



_cal = parsedatetime.Calendar()
local_tz = tz.tzlocal()
DP_SETTINGS = {
    "TIMEZONE": "America/Denver",
    "RETURN_AS_TIMEZONE_AWARE": True,
    "PREFER_DATES_FROM": "current_period"
}


def extract_datetime(text):

    # try parsedatetime first (great for relative)
    dt, status = _cal.parseDT(text, tzinfo=local_tz)
    if status > 0:
        return dt
    # fallback to dateparser
    dt2 = dateparser.parse(text, settings=DP_SETTINGS)
    if dt2 and dt2.tzinfo is None:
        return dt2.replace(tzinfo=local_tz)
    return dt2


def parse_input(user_input):

    # when only given a date, it's parsing the wrong time

    intent_re = re.compile(
        r'\b(?P<intention>create|make|add|schedule|remove|delete|destroy|view|see|look)\b',
        re.IGNORECASE
    )

    intent_m = intent_re.search(user_input)
    if intent_m:
        intention = intent_m.group('intention')
    else:
        intention = input("What are you trying to do? ")

    object_re = re.compile(
        r'\b(?P<object>event|task|events|tasks)\b',
        re.IGNORECASE
    )

    object_m = object_re.search(user_input)
    if intent_m:
        obj = object_m.group('object')
    else:
        obj = input("Is this an event, appointment, or task? ")

    name_re = re.compile(
        r'\b(?:call(?:ed)?\s+it|called|named|name\s+it|titled|title\s+it|name\sof|title\sof)\b'  # trigger
        r'\s*'
        r'(?P<title>'
        r'"[^"]+"|'  # double‑quoted text
        r"\'[^\']+\'|"  # single‑quoted text
        r'\w+'  # or a single word
        r')',
        re.IGNORECASE
    )

    name_m = name_re.search(user_input)
    # title = None
    if name_m:
        raw = name_m.group('title')  # e.g.  "'test'"
        title = raw.strip('"\'')
    else:
        title = input("What is the title? ")

    split_re = re.compile(r'(.+?)\s+(on|at|from|between|in)\s+(.+)', re.IGNORECASE)
    m = split_re.match(user_input)
    if m:
        summary = m.group(1).strip()
        when_text = m.group(3).strip()
    else:
        summary = user_input.strip()
        when_text = None

    start_time = end_time = None
    if when_text:
        range_re = re.compile(
            r'from\s+(?P<s>[\d:\sapm]+)\s+(?:to|until|-)\s+(?P<e>[\d:\sapm]+)',
            re.IGNORECASE
        )
        r = range_re.search(when_text)
        if r:
            start_time = r.group("s").strip()
            end_time = r.group("e").strip()
            when_text = when_text[:r.start()].strip()

        else:
            at_re = re.compile(r'\bat\s+(?P<s>[\d:\sapm]+)', re.IGNORECASE)
            a = at_re.search(when_text)
            if a:
                start_time = a.group("s").strip()
                when_text = when_text[:a.start()].strip()


# the split off is here
    if title:
        summary = title

    # Parse the date
    dt_date = extract_datetime(when_text) if when_text else None  # possible problem here

    time_min = time_max = None
    if dt_date and start_time is None and end_time is None:
        time_min, time_max = datetime_utils.day_bounds(dt_date)



    # If date only but you have a start time, merge them
    if dt_date and start_time:
        t = extract_datetime(start_time)
        if t:
            dt_date = dt_date.replace(hour=t.hour, minute=t.minute)

    # Build start/end datetimes
    start_dt = dt_date
    if start_time and not when_text:
        # if no date part, maybe the entire phrase was a time
        start_dt = extract_datetime(start_time)

    if end_time:
        t2 = extract_datetime(end_time)
        # merge date if needed
        if dt_date and t2:
            end_dt = dt_date.replace(hour=t2.hour, minute=t2.minute)
        elif t2:
            end_dt = t2
        else:
            end_dt = start_dt + timedelta(hours=1)
    else:
        end_dt = (start_dt + timedelta(hours=1)) if start_dt else None

    # Prompt for any missing core fields
    if not summary:
        summary = input("What should this event be called? ")
    if not start_dt:
        raw = input("When should it start? ")
        start_dt = extract_datetime(raw)
    if not end_dt:
        raw = input("When should it end? ")
        end_dt = extract_datetime(raw)

    dt_date = extract_datetime(when_text) if when_text else None

    # print(f"{title}\n{intention}\n{obj}\n{start_time}\n{end_time}\n{dt_date}\n{summary}")
    if start_time is None and end_time is None:
        cal_info = {
            'intention': intention,
            'object': obj,
            'title': summary,
            'start': time_min,
            'end': time_max,
            'date': dt_date,
            'raw_text': user_input
        }
    else:
        cal_info = {
            'intention': intention,
            'object': obj,
            'title': summary,
            'start': start_dt,
            'end': end_dt,
            'date': dt_date,
            'raw_text': user_input
        }

    return cal_info

# summary, date_text, start_txt, end_txt, title = parse_input(user_input)
    #
    # # if explicit title given, override
    # if title:
    #     summary = title
    #
    # # Parse the date
    # dt_date = extract_datetime(date_text) if date_text else None
    #
    # # If date only but you have a start time, merge them
    # if dt_date and start_txt:
    #     t = extract_datetime(start_txt)
    #     if t:
    #         dt_date = dt_date.replace(hour=t.hour, minute=t.minute)
    #
    # # Build start/end datetimes
    # start_dt = dt_date
    # if start_txt and not date_text:
    #     # if no date part, maybe the entire phrase was a time
    #     start_dt = extract_datetime(start_txt)
    #
    # if end_txt:
    #     t2 = extract_datetime(end_txt)
    #     # merge date if needed
    #     if dt_date and t2:
    #         end_dt = dt_date.replace(hour=t2.hour, minute=t2.minute)
    #     elif t2:
    #         end_dt = t2
    #     else:
    #         end_dt = start_dt + timedelta(hours=1)
    # else:
    #     end_dt = (start_dt + timedelta(hours=1)) if start_dt else None
    #
    # # Prompt for any missing core fields
    # if not summary:
    #     summary = input("What should this event be called? ")
    # if not start_dt:
    #     raw = input("When should it start? ")
    #     start_dt = extract_datetime(raw)
    # if not end_dt:
    #     raw = input("When should it end? ")
    #     end_dt = extract_datetime(raw)
    #
    # # Now build your Google Calendar body as before
    # event_body = {
    #     'summary': summary,
    #     'start':  {'dateTime': start_dt.isoformat(), 'timeZone': 'America/Denver'},
    #     'end':    {'dateTime': end_dt.isoformat(),   'timeZone': 'America/Denver'},
    #     # location/description omitted for brevity…
    # }
    #
    # service = get_credentials()
    # created = service.events().insert(calendarId='primary', body=event_body).execute()
    # print(f"Event created: {created.get('htmlLink')}\n")
