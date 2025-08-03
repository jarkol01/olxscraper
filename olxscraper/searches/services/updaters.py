from olxscraper.searches.models import Item, ItemUpdate, Search, SearchResult


class ItemUpdater:
    """
    A class that updates an item.
    If the item is not found, it creates a new one.
    If the item is found, it updates the item.
    """

    def __init__(self, item: Item, search: Search):
        self.item = item
        self.search = search

    def _build_update_changes(self, old_item: Item, new_item: Item) -> str:
        """
        Builds the changes that were made to the item.
        """
        changes = []
        if old_item.title != new_item.title:
            changes.append(f"Title changed from {old_item.title} to {new_item.title}")
        if old_item.price != new_item.price or old_item.currency != new_item.currency:
            changes.append(
                f"Price changed from {old_item.price} {old_item.currency} to {new_item.price} {new_item.currency}"
            )
        return "\n".join(changes)

    def _create_update_entry(self, item: Item, changes: str) -> None:
        """
        Creates an update entry for the item.
        """
        ItemUpdate.objects.create(
            item=item,
            changes=changes,
        )

    def _overwrite_item(self, old_item: Item, new_item: Item) -> None:
        """
        Overwrites the old item with the new item data.
        """
        old_item.title = new_item.title
        old_item.price = new_item.price
        old_item.currency = new_item.currency
        old_item.save()

    def _update_item(self, old_item: Item, new_item: Item) -> Item:
        """
        Creates an update entry and overwrites the old item with the new item data.
        """
        changes = self._build_update_changes(old_item, new_item)
        self._create_update_entry(new_item, changes)
        self._overwrite_item(old_item, new_item)

        return old_item

    def _create_item(self, item: Item) -> Item:
        """
        Creates a new item.
        """
        item.save()
        return item

    def run(self) -> None:
        existing_item = Item.objects.filter(url=self.item.url).first()
        if existing_item:
            item = self._update_item(existing_item, self.item)
        else:
            item = self._create_item(self.item)

        SearchResult.objects.create(search=self.search, item=item)
