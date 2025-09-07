from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from olxscraper.searches.constants import WebsiteChoices
from olxscraper.utils.datetime import pretty_datetime


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

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        PeriodicTask.objects.update_or_create(
            task="olxscraper.searches.tasks.search_category",
            args=[self.id],
            defaults={
                "name": f"Search {self.name}",
                "interval": self.search_frequency,
            },
        )


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
    website = models.CharField(
        max_length=255,
        choices=WebsiteChoices.choices,
        help_text=_("Which website you want to search"),
    )
    url = models.URLField(
        max_length=2048,
        help_text=_(
            "The URL of the category with all the filters applied, e.g. 'https://www.olx.pl/elektronika/telefony-i-smartfony/'"
        ),
    )

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    def __str__(self):
        return self.name


class Search(TimeStampedModel):
    address = models.ForeignKey(
        "Address",
        on_delete=models.CASCADE,
    )
    is_finished = models.BooleanField(
        default=False,
        help_text=_("Whether the search was finished successfully"),
    )

    class Meta:
        verbose_name = _("Search")
        verbose_name_plural = _("Searches")

    def __str__(self):
        return pretty_datetime(self.created)

    @property
    def items_found_count(self):
        return self.searchresult_set.filter(was_found=True).count()


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
    was_found = models.BooleanField(
        default=False,
        help_text=_("Whether the item was found in this search"),
    )

    class Meta:
        verbose_name = _("Search Result")
        verbose_name_plural = _("Search Results")

    def __str__(self):
        return pretty_datetime(self.created)


class Item(TimeStampedModel):
    url = models.URLField(
        max_length=2048,
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

    class Meta:
        verbose_name = _("Item")
        verbose_name_plural = _("Items")

    def __str__(self):
        return f"{self.title} - {self.price} {self.currency}"


class ItemUpdate(TimeStampedModel):
    item = models.ForeignKey(
        "Item",
        on_delete=models.CASCADE,
    )
    changes = models.TextField(
        help_text=_("The changes that were made to the item"),
    )

    class Meta:
        verbose_name = _("Item Update")
        verbose_name_plural = _("Item Updates")

    def __str__(self):
        return f"{self.item.title} - {pretty_datetime(self.created)}"
