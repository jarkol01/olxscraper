from django.contrib import admin
from olxscraper.searches.models import (
    Category,
    Address,
    Search,
    SearchResult,
    Item,
    ItemUpdate,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "search_frequency")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "url")


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ("address", "is_finished")


@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ("search", "item")


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("url", "title", "price", "currency")


@admin.register(ItemUpdate)
class ItemUpdateAdmin(admin.ModelAdmin):
    list_display = ("item", "changes")
