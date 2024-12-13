import asyncio
from typing import List, Tuple

import httpx
import pytest
from morecantile import tms

TILE_URLS = {
    "titiler-pgstac": "https://titiler-pgstac.maap-project.org/collections/icesat2-boreal/tiles/WebMercatorQuad/{z}/{x}/{y}",
    "mosaicjson": "https://titiler.maap-project.org/mosaics/cb39d9f9-4b7b-4812-a350-629f9f27fa3a/tiles/{z}/{x}/{y}.png",
}

LNG, LAT = -102, 57

TMS = tms.get("WebMercatorQuad")


def get_surrounding_tiles(
    x: int, y: int, zoom: int, width: int = 9, height: int = 7
) -> List[Tuple[int, int]]:
    """Get a list of surrounding tiles for a viewport"""
    tiles = []
    offset_x = width // 2
    offset_y = height // 2

    for y in range(y - offset_y, y + offset_y + 1):
        for x in range(x - offset_x, x + offset_x + 1):
            # Ensure x, y are valid for the zoom level
            max_tile = 2**zoom - 1
            x = max(0, min(x, max_tile))
            y = max(0, min(y, max_tile))
            tiles.append((x, y))

    return tiles


async def fetch_tile(
    client: httpx.AsyncClient, url: str, z: int, x: int, y: int, params: dict
):
    """Fetch a single tile"""
    formatted_url = url.format(z=z, x=x, y=y)
    return await client.get(formatted_url, params=params, timeout=None)


async def fetch_viewport_tiles(
    url: str, zoom: int, lng: float, lat: float, params: dict
):
    """Fetch all tiles for a viewport"""
    tile = TMS.tile(lng=lng, lat=lat, zoom=zoom)

    tiles = get_surrounding_tiles(tile.x, tile.y, zoom)

    async with httpx.AsyncClient() as client:
        tasks = [fetch_tile(client, url, zoom, x, y, params) for x, y in tiles]
        return await asyncio.gather(*tasks)


@pytest.mark.benchmark(
    group="icesat2-boreal",
    min_rounds=3,
    warmup=True,
    warmup_iterations=2,
)
@pytest.mark.parametrize("source", ("titiler-pgstac", "mosaicjson"))
@pytest.mark.parametrize("zoom", (6, 7, 8, 9, 10))
def test_tiles(benchmark, source: str, zoom: int):
    tile_url = TILE_URLS.get(source)

    params = {
        "bidx": 1,
        "rescale": [0, 400],
        "colormap_name": "gist_earth_r",
        "color_formula": "gamma r 1.06",
    }

    def tile_benchmark():
        assert tile_url
        result = asyncio.run(
            fetch_viewport_tiles(
                url=tile_url, zoom=zoom, lng=LNG, lat=LAT, params=params
            )
        )
        return result

    result = benchmark(tile_benchmark)
