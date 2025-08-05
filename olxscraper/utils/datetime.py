import datetime
from django.utils import timezone


def pretty_datetime(datetime_obj: datetime.datetime) -> str:
    local_datetime = timezone.localtime(datetime_obj)
    return local_datetime.strftime("%d.%m.%Y %H:%M:%S")
