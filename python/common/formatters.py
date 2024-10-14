from datetime import date, datetime, timedelta


def pretty_size(num, suffix="B"):
    """Returns a pretty string representation of size"""
    for unit in ("", "k", "M", "G", "T", "P", "E", "Z"):
        if abs(num) < 1000.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1000.0
    return f"{num:.1f}Y{suffix}"


WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def base_relative_date(dt: date) -> str | None:
    """Prints natural language descriptions of date close to today
    Returns None for dates more than a month away"""
    today = date.today()
    if dt == today:
        return "today"
    if dt < today:
        diff = today - dt
        if diff.days == 1:
            return "yesterday"
        elif diff.days < 7:
            return "last " + WEEKDAYS[dt.weekday()]
        elif diff.days < 31:
            return "{} days ago".format(diff.days)
    else:
        diff = dt - today
        if diff.days == 1:
            return "tomorrow"
        elif diff.days < 7:
            return "next " + WEEKDAYS[dt.weekday()]
        elif diff.days < 31:
            return "in {} days".format(diff.days)
    return None


def relative_day(date: date) -> str:
    """Print natural language descriptions of days for dates less than a month away
    Use YYYY-MM-DD format for other dates"""
    relative = base_relative_date(date)
    if relative is None:
        return str(date)
    return relative


def base_relative_time(time: datetime) -> str | None:
    """Prints natural language description of times less than a day away
    None otherwise"""
    now = datetime.now()
    if time <= now:
        diff = now - time
        if diff <= timedelta(seconds=60.0):
            return "just now"
        if diff <= timedelta(seconds=120.0):
            return "1 minute ago"
        if diff <= timedelta(minutes=60.0):
            return "{} minutes ago".format(int(diff.seconds / 60))
        if diff < timedelta(hours=2):
            return "1 hour ago"
        if diff < timedelta(days=1):
            return "{} hours ago".format(int(diff.seconds / 3600))
    else:
        diff = time - now
        if diff <= timedelta(seconds=60.0):
            return "in an instant"
        if diff <= timedelta(seconds=120.0):
            return "in 1 minute"
        if diff <= timedelta(minutes=60.0):
            return "in {} minutes".format(int(diff.seconds / 60))
        if diff < timedelta(hours=2):
            return "in 1 hour"
        if diff < timedelta(days=1):
            return "in {} hours".format(int(diff.seconds / 3600))
    return None


def relative_time(time: datetime, hours_on_relative_days: bool = True) -> str:
    """Print a natural language description of times less than a month away
    if hours_on_relative_days is False, don't print hour information for
    times more than a day away"""
    ft = base_relative_time(time)
    if ft is not None:
        return ft
    ft = relative_day(time.date())
    if hours_on_relative_days:
        return f"{ft} {time.hour:02}:{time.hour:02}"
    return ft
