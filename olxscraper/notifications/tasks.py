from webpush import send_group_notification
from celery import shared_task


@shared_task
def send_notification(payload):
    send_group_notification(group_name="all", payload=payload, ttl=1000)
