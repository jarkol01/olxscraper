import requests
from bs4 import BeautifulSoup
from django.db import models
import re
from urllib.parse import urlparse
from urllib.parse import parse_qs

from olxscraper.notifications.tasks import send_notification


class Category(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(
        max_length=500,
        help_text="Enter an OLX url with parameters you want to search, price and distance parameters will be overriden if specified. Localization should be replaced with {}. Ex. https://www.olx.pl/elektronika/telefony/smartfony-telefony-komorkowe/{}/?search%5Bfilter_enum_phonemodel%5D%5B0%5D=iphone-14-pro-max&search%5Bfilter_enum_phonemodel%5D%5B1%5D=iphone-14-pro",
    )
    city = models.CharField(max_length=255, default="krakow")
    distance = models.PositiveSmallIntegerField(blank=True, null=True)
    price = models.PositiveSmallIntegerField(blank=True, null=True)
    search = models.BooleanField(default=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def get_url_params(self):
        params = parse_qs(urlparse(self.url).query)
        if self.distance:
            params["search[dist]"] = self.distance
        if self.price:
            params["search[filter_float_price:to]"] = self.price
        params["page"] = 1
        return params

    def get_url(self):
        return self.url.split("{}")[0] + self.city + "/"

    @classmethod
    def search_all(cls):
        output = {}
        for obj in cls.objects.filter(search=True):
            output[obj.name] = obj.make_search()

        if any(value != 0 for value in output.values()):
            payload = {
                "head": "Nowe wyniki wyszukiwania!",
                "body": "; ".join(
                    [f"{name}: {found}" for name, found in output.items()]
                ),
                "url": "https://c2d72cfa9843-10290998949685835791.ngrok-free.app/admin/flats/search/",
            }
            send_notification(payload)

    def make_search(self):
        url = self.get_url()
        params = self.get_url_params()

        self.new_search = Search.objects.create(category=self)
        self.search_next = True

        while self.search_next:
            print(f"Searching page {params['page']}")
            response = requests.get(url, params)
            self.search_page(response)
            params["page"] += 1
        self.new_search.finished = True
        self.new_search.save()
        return self.new_search.found

    def search_page(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        offers = soup.find_all("a", class_="css-rc5s2u")
        print(f"Found {len(offers)} offers")
        for offer in offers:
            try:
                price = int(
                    re.sub(r"\D", "", offer.find("p", class_="css-10b0gli").text)
                )
            except ValueError:
                print(
                    f"Error while parsing price {offer.find('p', class_='css-10b0gli').text}"
                )
                price = 0

            offer_data = {
                "title": offer.find("h6", class_="css-16v5mdi").text,
                "url": "https://www.olx.pl" + offer["href"]
                if offer["href"].startswith("/d/")
                else offer["href"],
                "price": price,
                "category": self,
                "search": self.new_search,
            }

            if not Flat.objects.filter(url=offer_data["url"]).exists():
                Flat.objects.create(**offer_data)

        if not soup.find(attrs={"data-cy": "pagination-forward"}):
            self.search_next = False


class Search(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="category_search"
    )
    time = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)

    class Meta:
        verbose_name = "search"
        verbose_name_plural = "searches"

    @property
    def found(self):
        return self.flat_set.count()


class Flat(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    search = models.ForeignKey(Search, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "flat"
        verbose_name_plural = "flats"

    @property
    def get_url(self):
        if self.url.startswith("/d/"):
            return "https://www.olx.pl" + self.url
        return self.url

    @property
    def time(self):
        return self.search.time
