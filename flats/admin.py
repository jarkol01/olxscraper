from django.contrib import admin
from flats.models import Flat, Category

# Register your models here.

class FlatAdmin(admin.ModelAdmin):
    fields = ["title", "price", "url"]
    list_display = fields


admin.site.register(Flat, FlatAdmin)
admin.site.register(Category)
