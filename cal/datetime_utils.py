from datetime import datetime, timedelta

# naive datetime means that it doesn't have a timezone attached
# tz stands for timezone
# RFC3339 (ISO-8601) is the timestamp format Google Calendar expects when you send it dateTime values.


def iso_with_offset(dt: datetime) -> str:
    """Return RFC3339 (ISO-8601) string with UTC offset. Treat naive datetimes as local."""
    if dt.tzinfo is None:
        dt = dt.astimezone()  # attach the machine's local timezone
    return dt.isoformat()

# def day_bounds(date_like: datetime) -> tuple[str, str]:
def day_bounds(date_like) -> tuple[str, str]:
    if date_like.tzinfo is None:
        date_like = date_like.astimezone()
    start = date_like.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end

