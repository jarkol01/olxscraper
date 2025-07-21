import marimo

__generated_with = "0.14.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import aiohttp
    import time
    import asyncio
    import httpx

    return aiohttp, asyncio, httpx, time


@app.cell
def _():
    url = "https://www.olx.pl/motoryzacja/samochody/"
    return


@app.cell
def _(aiohttp, asyncio, time):
    async def fetch_async(url, number_of_pages):
        urls = [f"{url}?page={i}" for i in range(1, number_of_pages + 1)]

        aiohttp_client = aiohttp.ClientSession()

        try:
            start_time = time.perf_counter()
            tasks = [aiohttp_client.get(target) for target in urls]
            result = await asyncio.gather(*tasks)
            end_time = time.perf_counter()
            print(f"Async: {end_time - start_time:.2f} seconds")
            return result
        finally:
            await aiohttp_client.close()

    return (fetch_async,)


@app.cell
def _(httpx, time):
    async def fetch_sync(url, number_of_pages):
        urls = [f"{url}?page={i}" for i in range(1, number_of_pages + 1)]

        client = httpx.Client()

        try:
            start_time = time.perf_counter()
            result = [client.get(target) for target in urls]
            end_time = time.perf_counter()
            print(f"Sync: {end_time - start_time:.2f} seconds")
            return result
        finally:
            client.close()

    return (fetch_sync,)


@app.cell
async def _(fetch_async):
    await fetch_async("https://www.olx.pl/motoryzacja/samochody/", 25)
    return


@app.cell
async def _(fetch_sync):
    await fetch_sync("https://www.olx.pl/motoryzacja/samochody/", 25)
    return


if __name__ == "__main__":
    app.run()
