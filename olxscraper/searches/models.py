from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django_celery_beat.models import IntervalSchedule


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        help_text=_("The name of the category, e.g. 'Mobile phones'"),
    )
    search_frequency = models.ForeignKey(
        IntervalSchedule,
        on_delete=models.PROTECT,
        help_text=_("How often the search should be performed"),
    )

    def __str__(self):
        return self.name


class Address(models.Model):
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=255,
        help_text=_(
            "Should describe the address of the category, e.g. 'Mobile phones up to $1000'"
        ),
    )
    url = models.URLField(
        help_text=_(
            "The URL of the category with all the filters applied, e.g. 'https://www.olx.pl/elektronika/telefony-i-smartfony/'"
        ),
    )


class Search(TimeStampedModel):
    address = models.ForeignKey(
        "Address",
        on_delete=models.CASCADE,
    )
    is_finished = models.BooleanField(
        default=False,
        help_text=_("Whether the search was finished successfully"),
    )


class SearchResult(TimeStampedModel):
    search = models.ForeignKey(
        "Search",
        on_delete=models.CASCADE,
    )
    item = models.ForeignKey(
        "Item",
        on_delete=models.PROTECT,
        help_text=_("The item that was found"),
    )


class Item(TimeStampedModel):
    url = models.URLField(
        help_text=_("The URL of the item"),
    )
    title = models.CharField(
        max_length=255,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    currency = models.CharField(
        max_length=3,
    )


class ItemUpdate(TimeStampedModel):
    item = models.ForeignKey(
        "Item",
        on_delete=models.CASCADE,
    )
    changes = models.TextField(
        help_text=_("The changes that were made to the item"),
    )
