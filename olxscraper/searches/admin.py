from django.contrib import admin
from django.utils.html import mark_safe
from django.utils.safestring import SafeString
from django.urls import reverse
from django.db.models import Count, Q


from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display



from olxscraper.searches.models import (
    Category,
    Address,
    Search,
    SearchResult,
    Item,
    ItemUpdate,
)
from olxscraper.searches.constants import WebsiteChoices


class AddressInline(TabularInline):
    model = Address
    extra = 0
    show_change_link = True
    fields = ("name", "website", "url")

    @display(description="Link", label=True)
    def show_link(self, obj):
        if obj and obj.url:
            return mark_safe(f'<a href="{obj.url}" target="_blank" class="btn btn-sm btn-outline-primary">View</a>')
        return "-"


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "search_frequency", "address_count", "recent_items_count")
    list_filter = ("search_frequency",)
    search_fields = ("name",)
    inlines = [AddressInline]
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('address_set')
        return queryset

    @display(description="Addresses")
    def address_count(self, obj):
        count = obj.address_set.count()
        if count > 0:
            url = reverse("admin:searches_address_changelist") + f"?category__id__exact={obj.id}"
            return mark_safe(f'<a href="{url}">{count}</a>')
        return count

    @display(description="Recent Items (7d)")
    def recent_items_count(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=2)
        count = Item.objects.filter(
            searchresult__search__address__category=obj,
            created__gte=week_ago
        ).distinct().count()
        
        if count > 0:
            url = reverse("admin:searches_item_changelist") + f"?searchresult__search__address__category__id__exact={obj.id}&created__gte={week_ago.strftime('%Y-%m-%d')}"
            return mark_safe(f'<a href="{url}" class="btn btn-sm btn-success">{count}</a>')
        return count


class SearchInline(TabularInline):
    model = Search
    extra = 0
    show_change_link = True
    readonly_fields = ("created", "is_finished", "items_found_count")
    fields = ("created", "is_finished", "items_found_count")


@admin.register(Address)
class AddressAdmin(ModelAdmin):
    list_display = ("name", "category", "website", "last_search", "items_found", "show_url")
    list_filter = (
        "category",
        "website",
    )
    search_fields = ("name", "category__name", "url")
    inlines = [SearchInline]
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('category').prefetch_related('search_set')
        return queryset

    @display(description="Last Search")
    def last_search(self, obj):
        last_search = obj.search_set.order_by('-created').first()
        if last_search:
            return last_search.created.strftime('%Y-%m-%d %H:%M')
        return "Never"

    @display(description="Items Found")
    def items_found(self, obj):
        total_items = obj.search_set.aggregate(
            total=Count('searchresult', filter=Q(searchresult__was_found=True))
        )['total'] or 0
        
        if total_items > 0:
            url = reverse("admin:searches_searchresult_changelist") + f"?search__address__id__exact={obj.id}&was_found__exact=1"
            return mark_safe(f'<a href="{url}">{total_items}</a>')
        return total_items

    @display(description="URL", label=True)
    def show_url(self, obj):
        if obj and obj.url:
            return mark_safe(f'<a href="{obj.url}" target="_blank" class="btn btn-sm btn-outline-primary">View</a>')
        return "-"


class SearchResultInline(TabularInline):
    model = SearchResult
    extra = 0
    show_change_link = True
    fields = ("item_link", "was_found", "created")
    readonly_fields = ("item_link", "created")

    def get_queryset(self, request):
        return super().get_queryset(request).filter(was_found=True).select_related('item')

    @display(description="Item", label=True)
    def item_link(self, obj):
        if obj and obj.item:
            return mark_safe(f'<a href="{obj.item.url}" target="_blank">{obj.item.title}</a>')
        return "-"


@admin.register(Search)
class SearchAdmin(ModelAdmin):
    list_display = ("address", "created", "is_finished", "items_found_count", "duration")
    list_filter = (
        "is_finished",
        "created",
        "address__category",
        "address__website",
    )
    search_fields = ("address__name", "address__category__name")
    inlines = [SearchResultInline]
    ordering = ("-created",)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('address', 'address__category')
        return queryset

    @display(description="Duration")
    def duration(self, obj):
        if obj.modified and obj.created:
            delta = obj.modified - obj.created
            minutes = int(delta.total_seconds() / 60)
            if minutes > 0:
                return f"{minutes}m"
            else:
                seconds = int(delta.total_seconds())
                return f"{seconds}s"
        return "-"


class ItemUpdateInline(TabularInline):
    model = ItemUpdate
    extra = 0
    show_change_link = True
    readonly_fields = ("created", "changes")
    fields = ("created", "changes")


@admin.register(Item)
class ItemAdmin(ModelAdmin):
    list_display = ("title", "price_display", "category_link", "created", "view_item", "found_in_searches")
    list_filter = (
        "created",
        "price",
        "currency",
        "searchresult__search__address__category",
        "searchresult__search__address__website",
    )
    search_fields = ("title", "url")
    inlines = [ItemUpdateInline]
    ordering = ("-created",)  # Latest items first - perfect for mobile users
    list_per_page = 50  # More items per page for better mobile browsing
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('searchresult_set__search__address__category')
        return queryset

    @display(description="Price", ordering="price")
    def price_display(self, obj):
        return f"{obj.price:.2f} {obj.currency}"

    @display(description="Category", label=True)
    def category_link(self, obj):
        # Get first category from search results
        search_result = obj.searchresult_set.first()
        if search_result and search_result.search.address.category:
            category = search_result.search.address.category
            url = reverse("admin:searches_category_change", args=[category.id])
            return mark_safe(f'<a href="{url}" class="btn btn-sm btn-info">{category.name}</a>')
        return "-"

    @display(description="View Item", label=True)
    def view_item(self, obj):
        if obj and obj.url:
            return mark_safe(f'<a href="{obj.url}" target="_blank" class="btn btn-sm btn-primary">View</a>')
        return "-"

    @display(description="Found In")
    def found_in_searches(self, obj):
        count = obj.searchresult_set.filter(was_found=True).count()
        if count > 0:
            url = reverse("admin:searches_searchresult_changelist") + f"?item__id__exact={obj.id}&was_found__exact=1"
            return mark_safe(f'<a href="{url}">{count} searches</a>')
        return f"{count} searches"


@admin.register(SearchResult)
class SearchResultAdmin(ModelAdmin):
    list_display = ("item_title", "search_info", "was_found", "created")
    list_filter = (
        "was_found",
        "created",
        "search__address__category",
        "search__address__website",
    )
    search_fields = ("item__title", "search__address__name", "search__address__category__name")
    ordering = ("-created",)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('item', 'search__address__category')
        return queryset

    @display(description="Item")
    def item_title(self, obj):
        if obj and obj.item:
            url = reverse("admin:searches_item_change", args=[obj.item.id])
            return mark_safe(f'<a href="{url}">{obj.item.title}</a>')
        return "-"

    @display(description="Search")
    def search_info(self, obj):
        if obj and obj.search:
            category = obj.search.address.category.name if obj.search.address.category else "N/A"
            return f"{category} - {obj.search.address.name}"
        return "-"


@admin.register(ItemUpdate)
class ItemUpdateAdmin(ModelAdmin):
    list_display = ("item_title", "created", "changes_preview")
    list_filter = (
        "created",
        "item__searchresult__search__address__category",
    )
    search_fields = ("item__title", "changes")
    ordering = ("-created",)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('item')
        return queryset

    @display(description="Item")
    def item_title(self, obj):
        if obj and obj.item:
            url = reverse("admin:searches_item_change", args=[obj.item.id])
            return mark_safe(f'<a href="{url}">{obj.item.title}</a>')
        return "-"

    @display(description="Changes")
    def changes_preview(self, obj):
        if obj.changes:
            preview = obj.changes[:100]
            if len(obj.changes) > 100:
                preview += "..."
            return preview
        return "-"
