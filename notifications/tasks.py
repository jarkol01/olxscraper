from webpush import send_group_notification
from celery import shared_task

payload = {"head": "Welcome!", "body": "Hello World"}

@shared_task
def send_notification():
	send_group_notification(group_name="all", payload=payload, ttl=1000)
