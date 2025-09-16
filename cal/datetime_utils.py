from datetime import datetime, timedelta


def iso_with_offset(dt: datetime) -> str:
    """Return RFC3339 (ISO-8601) string with UTC offset. Treat naive datetimes as local."""
    if dt.tzinfo is None:
        dt = dt.astimezone()  # attach the machine's local timezone
    return dt.isoformat()


def day_bounds(date_like) -> tuple[dict, dict]:
    date_like = date_like.date()
    start = {
        'date': date_like,
        'timeZone': datetime.tzinfo
    }
    end = {
        'date': start['date'] + timedelta(days=1),
        'timeZone': datetime.tzinfo
    }
    return start['date'].isoformat(), end['date'].isoformat()

