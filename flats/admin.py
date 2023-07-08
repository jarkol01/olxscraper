from django.contrib import admin
from flats.models import Flat, Category, Search


class FlatAdmin(admin.ModelAdmin):
    fields = ["title", "price", "url"]
    list_display = fields


class CategoryAdmin(admin.ModelAdmin):
    fields = ["name", "price", "url", "search", "city", "distance"]
    list_display = fields


class FlatInline(admin.TabularInline):
    model = Flat
    readonly_fields = ["title", "url", "price", "category"]
    show_change_link = True


class SearchAdmin(admin.ModelAdmin):
    fields = ["category", "time", "found"]
    list_display = fields
    readonly_fields = fields
    inlines = [FlatInline]


admin.site.register(Flat, FlatAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Search, SearchAdmin)
