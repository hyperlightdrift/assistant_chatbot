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
    if object_m:
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
    title = None
    if name_m:
        raw = name_m.group('title')  # e.g.  "'test'"
        title = raw.strip('"\'')
    # else:
    #     title = input("What is the title? ")

    # TODO: have group 3 catch the word "week"
    split_re = re.compile(r'(.+?)\s+(?:(on|at|from|between|in)\s+|(?=\ba\s+week\b))(.+)', re.IGNORECASE)  # group 3 isn't catching "week"
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

    if title:
        summary = title

    # Parse the date
    dt_date = extract_datetime(when_text) if when_text else None

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

    scope = "all" if re.search(r'\b(all|everything|every)\b', user_input, re.IGNORECASE) else None
    force = bool(re.search(r'\b(force|anyway|i[’\']?m sure|yes,? delete)\b', user_input, re.IGNORECASE))

    is_create = intention.lower() in ("create", "make", "add", "schedule")
    if is_create:
        if not summary:
            summary = input("What should this event be called? ")
        if not start_dt:
            raw = input("When should it start? ")
            start_dt = extract_datetime(raw)
        if not end_dt:
            raw = input("When should it end? ")
            end_dt = extract_datetime(raw)

    dt_date = extract_datetime(when_text) if when_text else None

    if start_time is None and end_time is None:
        cal_info = {
            'intention': intention,
            'object': obj,
            'title': summary,
            'start': time_min,
            'end': time_max,
            'date': dt_date,
            'scope': scope,
            'force': force,
            'raw_text': user_input
        }
    else:
        cal_info = {
            'intention': intention,
            'object': obj,
            'title': summary,
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'date': dt_date,
            'scope': scope,
            'force': force,
            'raw_text': user_input
        }

    return cal_info
