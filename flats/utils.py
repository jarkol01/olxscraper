from bs4 import BeautifulSoup
import requests

from flats.models import Flat

urls_to_search = {
    "https://www.olx.pl/nieruchomosci/stancje-pokoje/krakow/?search%5Bfilter_enum_roomsize%5D%5B0%5D=one&search%5Bfilter_float_price%3Ato%5D={}&page=": [1400, FlatTypes.POKOJ],
    "https://www.olx.pl/nieruchomosci/mieszkania/wynajem/krakow/?search%5Bfilter_float_price%3Ato%5D={}&page=": [3000, FlatTypes.MIESZKANIE],
}

def S():
    for template, info in urls_to_search.items():
        page_num = 1

        while True:
            print(f"Checking page {page_num}")
            url = template.format(page_num, info[0])
            page = requests.get(url)
            
            if page.status_code != 200:
                print(f"Brak połączenia. Code: {page.status_code}")
                break
            
            soup = BeautifulSoup(page.text, 'html.parser')

            offers = soup.find_all(class_="css-1sw7q4x")

            print(len(offers))
            print(url)

            for offer in offers:
                try:
                    offer_title = offer.find(class_="css-16v5mdi").string
                    offer_url = "https://www.olx.pl" + offer.find(class_="css-rc5s2u")["href"]
                    offer_price = offer.find(class_="css-10b0gli").string.strip("zł").replace(" ", "").replace(",", ".")

                    if Flat.objects.filter(url=offer_url).exists():
                        continue

                    Flat.objects.create(title=offer_title, url=offer_url, type=info[1], price=offer_price)
                    print("new object")
                except AttributeError:
                    pass

            if len(soup.find(class_="css-1vdlgt7").find_all(class_="css-pyu9k9")) == 1 and page_num != 1:
                print("Koniec ofert")
                break

            page_num += 1
    