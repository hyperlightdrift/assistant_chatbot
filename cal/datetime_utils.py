from datetime import datetime, timedelta


def iso_with_offset(dt: datetime) -> str:
    """Return RFC3339 (ISO-8601) string with UTC offset. Treat naive datetimes as local."""
    if dt.tzinfo is None:
        dt = dt.astimezone()  # attach the machine's local timezone
    return dt.isoformat()


def day_bounds(date_like) -> tuple[str, str]:
    """Return RFC3339 datetime strings for start and end of day."""
    if hasattr(date_like, 'date'):
        date_like = date_like.date()
    
    # Get local timezone
    local_tz = datetime.now().astimezone().tzinfo
    
    # Start of day (00:00:00)
    start_dt = datetime.combine(date_like, datetime.min.time()).replace(tzinfo=local_tz)
    
    # End of day (23:59:59.999999) - or start of next day
    end_dt = datetime.combine(date_like + timedelta(days=1), datetime.min.time()).replace(tzinfo=local_tz)
    
    return start_dt.isoformat(), end_dt.isoformat()


