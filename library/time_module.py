from datetime import datetime
import pytz

tz = pytz.timezone("Europe/Athens")


def get_timestamp():
    return datetime.now(tz).replace(microsecond=0)


def schedule_time(hour: int, minute: int):
    athens_time = tz.localize(
        datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    )

    utc_time = athens_time.astimezone(pytz.UTC)

    return utc_time.time()


def calc_time_difference(from_time: datetime, to_time: datetime) -> int:
    diff = (to_time - from_time).total_seconds()
    diff = round(diff, 0)
    return int(diff)
