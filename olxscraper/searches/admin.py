from django.contrib import admin
from olxscraper.searches.models import (
    Category,
    Address,
    Search,
    SearchResult,
    Item,
    ItemUpdate,
)

from django.utils.html import mark_safe


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    show_change_link = True
    readonly_fields = (
        "name",
        "show_link",
    )
    fields = ("name", "show_link")

    @admin.display(description="Link")
    def show_link(self, obj):
        return mark_safe(f"<a href='{obj.url}'>Link</a>")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "search_frequency")
    inlines = [AddressInline]


class SearchInline(admin.TabularInline):
    model = Search
    extra = 0
    show_change_link = True
    readonly_fields = ("is_finished", "items_found_count")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "url")
    inlines = [SearchInline]


class SearchResultInline(admin.TabularInline):
    model = SearchResult
    extra = 0
    show_change_link = True
    fields = ("item_link",)
    readonly_fields = ("item_link",)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(was_found=True)

    @admin.display(description="Item")
    def item_link(self, obj):
        return mark_safe(f"<a href='{obj.item.url}'>{obj.item}</a>")


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ("address", "is_finished")
    inlines = [SearchResultInline]


class ItemUpdateInline(admin.TabularInline):
    model = ItemUpdate
    extra = 0
    show_change_link = True


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("url", "title", "price", "currency")
    inlines = [ItemUpdateInline]
