from datetime import datetime, date, timedelta
from . import datetime_utils, parser


def is_date_only(value: str) -> bool:
    return "T" not in value


def create_event(service, title, start, end):

    if is_date_only(start) and is_date_only(end):
        event_body = {
                'summary': title,
                'start': {'date': start},
                'end': {'date': end},
            }
    else:
        event_body = {
            'summary': title,
            'start': {'dateTime': start},
            'end': {'dateTime': end},
        }

    created = service.events().insert(calendarId='primary', body=event_body).execute()
    print(f"Event created: {created.get('htmlLink')}\n")


def view_events(service, parsed: dict, calendar_id: str = 'primary'):

    title = parsed.get('title') or None
    start = parsed.get('start')
    end = parsed.get('end')
    date_dt = parsed.get('date')

    
    time_min = time_max = None
    
    # Handle different cases for time bounds
    if start and end:
        # If start/end are datetime objects, convert to ISO strings
        if isinstance(start, datetime) and isinstance(end, datetime):
            time_min, time_max = datetime_utils.iso_with_offset(start), datetime_utils.iso_with_offset(end)
        # If start/end are already strings (from day_bounds), use them directly
        elif isinstance(start, str) and isinstance(end, str):
            time_min, time_max = start, end
    elif date_dt:
        # If only a date is provided, get day bounds
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


    response = service.events().list(**params).execute()

    events = response.get("items", [])

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


def delete_events(service, title, start, end, scoped, forced, calendar_id: str = 'primary',
                  confirm_bulk_threshold: int = 10, default_window_days: int = 365):
    """
    title: str | None
    start/end: can be RFC3339 strings (from day_bounds) OR tz-aware datetime objects OR None
    scoped: "all" if the user said all/everything, else None
    forced: bool (user said "force/anyway/i'm sure/yes delete")
    """

    # ---- normalize timeMin/timeMax into RFC3339 strings ----
    def _to_rfc3339(v):
        if v is None:
            return None
        if isinstance(v, str):
            # assume already RFC3339 from datetime_utils.day_bounds or similar
            return v
        if isinstance(v, datetime):
            # ensure tz-aware; Google accepts offsets (you don't HAVE to convert to Z)
            if v.tzinfo is None:
                v = v.replace(tzinfo=datetime.now().astimezone().tzinfo)
            return v.isoformat()
        raise TypeError(f"Unsupported type for time bound: {type(v)}")

    timeMin = _to_rfc3339(start)
    timeMax = _to_rfc3339(end)

    # If neither bound provided, use a safe default window (now .. now+365d)
    if timeMin is None and timeMax is None:
        now = datetime.now(datetime.now().astimezone().tzinfo)
        timeMin = now.isoformat()
        timeMax = (now + timedelta(days=default_window_days)).isoformat()

    # If only max is given, provide a reasonable min (Google prefers timeMin with orderBy=startTime)
    if timeMin is None and timeMax is not None:
        now = datetime.now(datetime.now().astimezone().tzinfo)
        timeMin = now.isoformat()

    # Sanity: ensure the window isn't inverted
    try:
        # parse back to compare only if both have 'T' (dateTime strings)
        if timeMin and timeMax and "T" in timeMin and "T" in timeMax:
            tmin = datetime.fromisoformat(timeMin.replace("Z", "+00:00"))
            tmax = datetime.fromisoformat(timeMax.replace("Z", "+00:00"))
            if tmin >= tmax:
                # widen by +1 day as a safe fallback
                tmax = tmin + timedelta(days=1)
                timeMax = tmax.isoformat()
    except Exception:
        pass  # if parsing fails, let API validate

    # ---- list candidate events ----
    params = {
        "calendarId": calendar_id,
        "singleEvents": True,                 # expand recurring series
        "orderBy": "startTime",
        "maxResults": 2500,
        "fields": "items(id,summary,start,end,recurringEventId),nextPageToken",
        "timeMin": timeMin
    }
    if timeMax: params["timeMax"] = timeMax
    if title:   params["q"] = title

    items, token = [], None
    while True:
        if token:
            params["pageToken"] = token
        resp = service.events().list(**params).execute()
        items.extend(resp.get("items", []))
        token = resp.get("nextPageToken")
        if not token:
            break

    if not items:
        print("No matching events found.")
        return {"status": "none", "deleted_count": 0}

    # ---- choose targets ----
    targets = items

    # If the user did NOT say "all", and provided a title, try to narrow to exact title matches
    if scoped != "all" and title:
        exact = [e for e in items if (e.get("summary") or "").strip().lower() == title.strip().lower()]
        if exact:
            targets = exact

    # If there is no title (or no exacts) and this looks like a bulk delete, apply guardrail unless forced
    if scoped != "all" and not forced and len(targets) >= confirm_bulk_threshold:
        sample = [(e.get("summary"), e.get("id")) for e in targets[:5]]
        print(f"Found {len(targets)} events in the window. Example ids: {sample}\n"
              f"Re-run with 'force' wording (e.g., 'delete anyway') or say 'all' to proceed.")
        return {"status": "too_many_matches", "count": len(targets)}

    # ---- delete ----
    deleted = 0
    for ev in targets:
        service.events().delete(calendarId=calendar_id, eventId=ev["id"]).execute()
        deleted += 1

    print(f"Deleted {deleted} event(s).")
    return {"status": "deleted", "deleted_count": deleted}