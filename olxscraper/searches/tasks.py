from celery import shared_task
from django.urls import reverse

from olxscraper.notifications.tasks import send_notification
from olxscraper.searches.models import Address, Category, Search
from olxscraper.searches.services.searchers import OlxSearcher
from olxscraper.searches.services.updaters import ItemUpdater


def perform_search(address: Address, search: Search):
    items = OlxSearcher(address).run()

    for item in items:
        ItemUpdater(item, search).run()


@shared_task
def search_category(category_id: int):
    category = Category.objects.get(id=category_id)

    items_found_count = 0
    for address in Address.objects.filter(category=category):
        print(f"Starting search for {address.name}")

        search = Search.objects.create(address=address)
        perform_search(address, search)
        search.is_finished = True
        search.save()

        items_found_count += search.items_found_count

        print(f"Search for {address.name} finished, sending notification")

    if items_found_count > 0:
        send_notification.delay(
            "New items found!",
            f"See {items_found_count} new items for {category.name}",
            reverse(
                "admin:searches_category_change", kwargs={"object_id": category_id}
            ),
        )
