from celery import shared_task

from olxscraper.flats.models import Category


@shared_task
def test_task():
    print("Test task just finished!")


@shared_task
def search_all_categories():
    Category.search_all()
