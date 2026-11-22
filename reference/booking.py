from datetime import datetime, timedelta
def _d(x):
    try: return datetime.strptime(x, "%m-%d-%y").date() if len(x) == 8 else None
    except ValueError: return None
def _t(x):
    try:
        if len(x) != 8: return None
        t = datetime.strptime(x, "%H:%M:%S"); return t.hour * 60 + t.minute + t.second / 60
    except ValueError: return None
def book_shift(shifts, staff, date, start, end):
    d = _d(date)
    if d is None: return "INVALID_DATE"
    a, b = _t(start), _t(end)
    if a is None or b is None or b <= a: return "INVALID_TIME"
    mine = [x for x in shifts if x["staff"] == staff]
    for x in mine:
        if _d(x["date"]) == d and _t(x["start"]) < b and a < _t(x["end"]): return "OVERLAP"
    def worked(day):
        mins = sum(_t(x["end"]) - _t(x["start"]) for x in mine if _d(x["date"]) == day)
        if day == d: mins += b - a
        return max(0, mins - 30) / 60 if mins else 0
    if worked(d) > 12: return "TOO_LONG"
    mon = d - timedelta(days=d.weekday())
    week = sum(worked(mon + timedelta(days=i)) for i in range(7))
    if worked(d) > 8 or week > 40: return "NEEDS_APPROVAL"
    return "OK"
