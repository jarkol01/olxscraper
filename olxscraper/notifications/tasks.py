from webpush import send_group_notification
from celery import shared_task
from django.templatetags.static import static


@shared_task
def send_notification(head: str, body: str, url: str):
    send_group_notification(
        group_name="all",
        payload={
            "head": head,
            "body": body,
            "icon": static("images/logo.png"),
            "url": url,
        },
        ttl=1000,
    )
