from django.utils.html import format_html
from django.contrib import admin
from olxscraper.flats.models import Flat, Category, Search


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    fields = ["title", "price", "url"]
    list_display = fields


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ["name", "price", "url", "search", "city", "distance"]
    list_display = fields


class FlatInline(admin.TabularInline):
    model = Flat
    fields = ["title", "price", "show_url"]
    readonly_fields = fields
    show_change_link = True
    can_delete = False

    def show_url(self, obj):
        return format_html("<a href='{url}'>{url}</a>", url=obj.url)


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    fields = ["category", "time", "found", "finished"]
    list_display = fields
    readonly_fields = fields
    inlines = [FlatInline]
