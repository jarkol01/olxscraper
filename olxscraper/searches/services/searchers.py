from decimal import Decimal
import json
import math
import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from logging import getLogger
from olxscraper.searches.models import Address, Item

logger = getLogger(__name__)


class ResearchFirstSearcher:
    """
    A searcher that performs a research on the first page of the address, concluding how many pages should be searched.
    Next, it performs the rest of the research.
    """

    def __init__(self, address: Address):
        self.address = address

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        async with session.get(url, headers=headers) as response:
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
        return items

    def run(self) -> list[Item]:
        pages_count = asyncio.run(self._search_first_page())

        print(f"Found {pages_count} pages to search")

        items = asyncio.run(self._search_rest_of_pages(pages_count))
        return items


class OlxSearcher(ResearchFirstSearcher):
    """
    A searcher that searches for items on OLX.
    """

    def _get_page_urls(self, page_number: int) -> str:
        """
        Returns the URL of the page.
        """
        return f"{self.address.url}&page={page_number}"

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
            url=self._ensure_absolute_url(self._parse_item_url(item)),
            title=self._parse_item_title(item),
            price=self._parse_item_price(item),
            currency="PLN",
        )

    @staticmethod
    def _parse_item_url(item: BeautifulSoup) -> str:
        """
        Parses the item URL and returns the URL.
        """
        item_listing = item.find("div", attrs={"data-cy": "ad-card-title"})
        item_listing_link = item_listing.find("a")
        return item_listing_link["href"]

    @staticmethod
    def _parse_item_title(item: BeautifulSoup) -> str:
        """
        Parses the item title and returns the title.
        """
        item_listing = item.find("div", attrs={"data-cy": "ad-card-title"})
        item_listing_link = item_listing.find("a")
        item_listing_heading = item_listing_link.find("h4")
        return item_listing_heading.text.strip()

    @staticmethod
    def _parse_item_price(item: BeautifulSoup) -> Decimal:
        """
        Parses the item price and returns the price.
        """
        item_listing_price = item.find("p", attrs={"data-testid": "ad-price"})
        price_text = item_listing_price.text.strip()
        match = re.search(r"\d{1,3}(?:[ ]\d{3})*", price_text)
        return Decimal(match.group(0).replace(" ", "").strip())

    @staticmethod
    def _ensure_absolute_url(url: str) -> str:
        """
        Ensures the URL is absolute.
        """
        if url.startswith("/"):
            return f"https://www.olx.pl{url}"
        return url


class KleinanzeigenSearcher(ResearchFirstSearcher):
    """
    A searcher that searches for items on Kleinanzeigen.
    """

    def _get_page_urls(self, page_number: int) -> str:
        """
        Returns the URL of the page.
        """
        url_parts = self.address.url.split("/")
        url_parts.insert(-1, f"seite:{page_number}")
        return "/".join(url_parts)

    def _parse_pages_count(self, html: str) -> int:
        """
        Parses the HTML and returns the number of pages to search.
        """
        soup = BeautifulSoup(html, "html.parser")
        pagination_items = soup.find_all("span", attrs={"class": "pagination-page"})

        if not pagination_items:
            return 1

        last_item = pagination_items[-1]

        return int(last_item.text.strip())

    def _parse_items(self, html: str) -> list[Item]:
        """
        Parses the HTML and returns the items.
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("li", attrs={"class": "ad-listitem fully-clickable-card"})

        return [self._parse_item(item) for item in items]

    def _parse_item(self, item: BeautifulSoup) -> Item:
        """
        Parses the item and returns the item.
        """
        return Item(
            url=self._ensure_absolute_url(self._parse_item_url(item)),
            title=self._parse_item_title(item),
            price=self._parse_item_price(item),
            currency="EUR",
        )

    @staticmethod
    def _parse_item_url(item: BeautifulSoup) -> str:
        """
        Parses the item URL and returns the URL.
        """
        item_listing = item.find("article")

        return item_listing["data-href"]

    @staticmethod
    def _parse_item_title(item: BeautifulSoup) -> str:
        """
        Parses the item title and returns the title.
        """
        item_listing = item.find("h2", attrs={"class": "text-module-begin"})
        item_listing_link = item_listing.find("a") or item_listing.find("span")

        return item_listing_link.text.strip()

    @staticmethod
    def _parse_item_price(item: BeautifulSoup) -> Decimal:
        """
        Parses the item price and returns the price.
        """
        item_listing_price = item.find(
            "p", attrs={"class": "aditem-main--middle--price-shipping--price"}
        )
        price_text = item_listing_price.text.strip()
        match = re.search(r"\d{1,3}(?:[ .]\d{3})*", price_text)

        return Decimal(match.group(0).replace(".", "").strip())

    @staticmethod
    def _ensure_absolute_url(url: str) -> str:
        if url.startswith("/"):
            return f"https://www.kleinanzeigen.de{url}"
        return url


class OtomotoSearcher(ResearchFirstSearcher):
    """
    A searcher that searches for items on Otomoto.
    """

    def _get_page_urls(self, page_number: int) -> str:
        """
        Returns the URL of the page.
        """
        return f"{self.address.url}&page={page_number}"

    def _parse_pages_count(self, html: str) -> int:
        """
        Parses the HTML and returns the number of pages to search.
        """
        soup = BeautifulSoup(html, "html.parser")

        script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
        next_data = json.loads(script_tag.string)

        for urql_state in next_data["props"]["pageProps"]["urqlState"].values():
            data = json.loads(urql_state["data"])
            if "advertSearch" not in data:
                continue
            page_size = data["advertSearch"]["pageInfo"]["pageSize"]
            total_count = data["advertSearch"]["totalCount"]

            return math.ceil(total_count / page_size)

    def _parse_items(self, html: str) -> list[Item]:
        """
        Parses the HTML and returns the items.
        """
        soup = BeautifulSoup(html, "html.parser")

        script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
        next_data = json.loads(script_tag.string)

        for urql_state in next_data["props"]["pageProps"]["urqlState"].values():
            data = json.loads(urql_state["data"])
            if "advertSearch" not in data:
                continue
            items = data["advertSearch"]["edges"]
            return [self._parse_item(item) for item in items]

    def _parse_item(self, item: dict) -> Item:
        """
        Parses the item and returns the item.
        """
        node = item["node"]

        return Item(
            url=self._ensure_absolute_url(node.get("url")),
            title=node.get("title"),
            price=node.get("price", {}).get("amount", {}).get("value"),
            currency="PLN",
        )

    @staticmethod
    def _ensure_absolute_url(url: str) -> str:
        if url.startswith("/"):
            return f"https://www.otomoto.pl{url}"
        return url
