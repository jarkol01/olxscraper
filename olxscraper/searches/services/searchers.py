from decimal import Decimal
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from logging import getLogger
from olxscraper.searches.models import Address, Item, Search
from olxscraper.searches.services.updaters import ItemUpdater

logger = getLogger(__name__)


class ResearchFirstSearcher:
    """
    A searcher that performs a research on the first page of the address, concluding how many pages should be searched.
    Next, it performs the rest of the research.
    """

    def __init__(self, address: Address):
        self.address = address
        self.search = None

    def _get_page_urls(self, page_number: int) -> str:
        """
        Returns the URL of the page.
        """
        return f"{self.address.url}&page={page_number}"

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> str:
        async with session.get(url) as response:
            return await response.text()

    def _parse_pages_count(self, html: str) -> int:
        """
        Parses the HTML and returns the number of pages to search.
        """
        raise NotImplementedError()

    def _parse_items(self, html: str) -> list[Item]:
        """
        Parses the HTML and returns the items.
        """
        raise NotImplementedError()

    async def _search_first_page(self) -> int:
        """
        Searches the first page of the address and returns the number of pages to search.
        """
        async with aiohttp.ClientSession() as session:
            html = await self._fetch(session, self.address.url)
            return self._parse_pages_count(html)

    async def _search_rest_of_pages(self, pages_count: int) -> None:
        """
        Searches the rest of the pages of the address, saving the items to the database.
        """
        urls = [self._get_page_urls(page) for page in range(1, pages_count + 1)]

        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch(session, url) for url in urls]
            htmls = await asyncio.gather(*tasks)

        items = []
        for html in htmls:
            items += [*self._parse_items(html)]

        for item in items:
            ItemUpdater(item, self.search).run()

    def run(self) -> None:
        print(f"Starting search for {self.address.name}")
        self.search = Search.objects.create(address=self.address)

        pages_count = asyncio.run(self._search_first_page())
        print(f"Found {pages_count} pages to search")

        asyncio.run(self._search_rest_of_pages(pages_count))

        print(f"Search for {self.address.name} finished")
        self.search.is_finished = True
        self.search.save()


class OlxSearcher(ResearchFirstSearcher):
    """
    A searcher that searches for items on OLX.
    """

    def _parse_pages_count(self, html: str) -> int:
        """
        Parses the HTML and returns the number of pages to search.
        """
        soup = BeautifulSoup(html, "html.parser")
        pagination_items = soup.find_all(
            "li", attrs={"data-testid": "pagination-list-item"}
        )

        if not pagination_items:
            return 1

        last_item = pagination_items[-1]
        last_item_link = last_item.find("a")
        return int(last_item_link.text.strip())

    def _parse_items(self, html: str) -> list[Item]:
        """
        Parses the HTML and returns the items.
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", attrs={"data-testid": "l-card"})
        return [self._parse_item(item) for item in items]

    def _parse_item(self, item: BeautifulSoup) -> Item:
        """
        Parses the item and returns the item.
        """
        return Item(
            url=self._parse_item_url(item),
            title=self._parse_item_title(item),
            price=self._parse_item_price(item),
            currency=self._parse_item_currency(item),
        )

    def _parse_item_url(self, item: BeautifulSoup) -> str:
        """
        Parses the item URL and returns the URL.
        """
        item_listing = item.find("div", attrs={"data-cy": "ad-card-title"})
        item_listing_link = item_listing.find("a")
        return item_listing_link["href"]

    def _parse_item_title(self, item: BeautifulSoup) -> str:
        """
        Parses the item title and returns the title.
        """
        item_listing = item.find("div", attrs={"data-cy": "ad-card-title"})
        item_listing_link = item_listing.find("a")
        item_listing_heading = item_listing_link.find("h4")
        return item_listing_heading.text.strip()

    def _parse_item_price(self, item: BeautifulSoup) -> Decimal:
        """
        Parses the item price and returns the price.
        """
        item_listing_price = item.find("p", attrs={"data-testid": "ad-price"})
        return Decimal(item_listing_price.text.strip().rsplit(" ", 1)[0])

    def _parse_item_currency(self, item: BeautifulSoup) -> str:
        """
        Parses the item currency and returns the currency.
        """
        item_listing_price = item.find("p", attrs={"data-testid": "ad-price"})
        return item_listing_price.text.strip().rsplit(" ", 1)[1]
