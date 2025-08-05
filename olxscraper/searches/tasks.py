from celery import shared_task
from django.urls import reverse

from olxscraper.notifications.tasks import send_notification
from olxscraper.searches.models import Address, Search
from olxscraper.searches.services.searchers import OlxSearcher
from olxscraper.searches.services.updaters import ItemUpdater


def perform_search(address: Address, search: Search):
    items = OlxSearcher(address).run()

    for item in items:
        ItemUpdater(item, search).run()


@shared_task
def search_category(category_id: int):
    for address in Address.objects.filter(category_id=category_id):
        print(f"Starting search for {address.name}")

        search = Search.objects.create(address=address)
        perform_search(address, search)
        search.is_finished = True
        search.save()

        print(f"Search for {address.name} finished, sending notification")
        send_notification.delay(
            "New items found!",
            f"See new items for {address.name}",
            reverse(
                "admin:searches_category_change", kwargs={"object_id": category_id}
            ),
        )
