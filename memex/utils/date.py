import os
from datetime import datetime
from logging import getLogger
from zoneinfo import ZoneInfo

from memex.utils import log_call

log = getLogger("memex")

@log_call()
def _choose_tz(tz_arg: str | None = None) -> datetime.tzinfo:
    """
    Selects the timezone to use, in this order:
    1. Explicit tz_arg provided by user
    2. MEMEX_TZ environment variable
    3. System default timezone

    Args:
        tz_arg (str | None): Explicit timezone name (e.g., 'Africa/Abidjan').

    Returns:
        tzinfo: The chosen timezone object.
    """
    if tz_arg:                      # explicit flag wins
        log.debug("[_choose_tz] Use explicit timezone: %s", tz_arg)
        return ZoneInfo(tz_arg)
    env = os.getenv("MEMEX_TZ")           # env var next
    if env:
        log.debug("[_choose_tz] Use environment timezone: %s", env)
        return ZoneInfo(env)
    # system zone - datetime grabs it automatically
    sys_tz = datetime.now().astimezone().tzinfo
    return sys_tz

@log_call()
def now(tz_arg: str | None = None) -> datetime:
    """Timezone-aware 'now' as datetime object."""
    tz = _choose_tz(tz_arg)
    return datetime.now(tz=tz)

@log_call()
def now_str(tz_arg: str | None = None) -> str:
    """Formatted 'now' as string 'YYYY-MM-DD HH:MM:SS +0000'."""
    return now(tz_arg).strftime("%Y-%m-%d %H:%M:%S %z")

@log_call()
def today_iso(tz_arg: str | None = None) -> str:
    """Return YYYY-MM-DD of *today* in chosen tz."""
    today = now(tz_arg).date().isoformat()
    return today

if __name__ == "__main__":
    print(_choose_tz()) # GMT
    print(now())        # 2025-08-30 15:32:16.551574+00:00
    print(now_str())    # 2025-08-30 15:32:16 +0000
    print(today_iso())  # 2025-08-30
    
    
    
    