from __future__ import annotations
import datetime as dt
import locale
from dateutil.relativedelta import relativedelta

# Always format in Turkish for user-facing strings
try:
    locale.setlocale(locale.LC_TIME, 'tr_TR.UTF-8')
except Exception:
    pass  # container might not have the locale; we'll still work with ISO

TZ = dt.timezone(dt.timedelta(hours=3))  # Europe/Istanbul fixed offset


def today_ist() -> dt.date:
    return dt.datetime.now(TZ).date()


def tomorrow_ist() -> dt.date:
    return today_ist() + relativedelta(days=1)


def format_date_tr(d: dt.date) -> str:
    # e.g., '20 Ekim 2025 Pazartesi'
    try:
        return d.strftime('%-d %B %Y %A')
    except Exception:
        return d.isoformat()