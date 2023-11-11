from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from datetime import datetime, time
from random import choice
from logging import getLogger
from os import getenv
import starlette.status as status
import requests
import pytz

logger = getLogger("uvicorn")


API_KEY = getenv('API_KEY')

SFW_WP_LIST = []
PG13_WP_LIST = []
NSFW_WP_LIST = []


# Set the NSFW level values 0 = disabled 1 = enabled.
# AUTO returns time based results
def calc_nsfw(timezone):
    def time_in_range(start, end, current):
        """Returns whether current is in the range [start, end]"""
        return start <= current <= end

    seven_am = time(7, 0, 0)
    five_pm = time(17, 0, 0)
    nine_pm = time(22, 0, 0)
    day = datetime.today().weekday()

    try:
        current = datetime.now(pytz.timezone(timezone)).time()
    except Exception as error:
        logger.error(f"Fatal Error - Overwriting attributes: {error.message}")
        current = datetime.now(pytz.timezone("America/New_York")).time()

    if time_in_range(seven_am, five_pm, current):
        if day < 5:
            nsfw_level = "sfw"
        else:
            nsfw_level = "pg13"
    elif time_in_range(five_pm, nine_pm, current):
        nsfw_level = "pg13"
    else:
        nsfw_level = "nsfw"

    return nsfw_level

def fetch_wp_list(nsfw_lvl):
    match nsfw_lvl:
        case "sfw":
            purity = "100"
            wp_list = SFW_WP_LIST

        case "pg13":
            purity = "010"
            wp_list = PG13_WP_LIST

        case "nsfw":
            purity = "001"
            wp_list = NSFW_WP_LIST
    
    response = requests.get(
            f'https://wallhaven.cc/api/v1/search?{"apikey=" + API_KEY + "&"}categories=010&{"purity=" + purity + "&"}atleast=1920x1080&ratios=16x9%2C16x10&sorting=random&order=desc&ai_art_filter=1&page=1'
        )
    for wp in response.json()["data"]:
        wp_list.append(wp["path"])


def get_rnd_wallpaper(nsfw_lvl):

    match nsfw_lvl:
        case "sfw":
            wp_list = SFW_WP_LIST

        case "pg13":
            wp_list = PG13_WP_LIST

        case "nsfw":
            wp_list = NSFW_WP_LIST

    wpurl = wp_list.pop()
    if len(wp_list) == 0:
        fetch_wp_list(nsfw_lvl)

    logger.info(nsfw_lvl)
    logger.info(wpurl)
    logger.info(len(wp_list))

    return wpurl

def populate_wp():
    fetch_wp_list("sfw")
    fetch_wp_list("pg13")
    fetch_wp_list("nsfw")



populate_wp()
app = FastAPI()


@app.get("/")
async def default():
    """
    Default endpoint to retrieve a random SFW (Safe For Work) wallpaper from wallhaven.cc.
    This endpoint is accessible without an API key and will only return wallpapers
    that are suitable for all audiences. It redirects to the URL of the selected SFW wallpaper.

    Returns:
        RedirectResponse: A FastAPI response object that redirects the client to the
                          URL of the random SFW wallpaper.
    """
    return RedirectResponse(
        url=get_rnd_wallpaper("sfw"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/pg13")
async def pg13():
    """
    Endpoint to retrieve a random Sketchy (PG-13) wallpaper from wallhaven.cc.
    This endpoint does not require an API key and will only return wallpapers
    that are flagged as slightly NSFW or PG-13, excluding SFW and fully NSFW content.
    It redirects to the URL of the selected wallpaper.

    Returns:
        RedirectResponse: A FastAPI response object that redirects the client to the
                          URL of the random PG-13 wallpaper.
    """
    return RedirectResponse(
        url=get_rnd_wallpaper("pg13"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/nsfw")
async def nsfw():
    """
    Endpoint to retrieve a random NSFW wallpaper from wallhaven.cc. Requires a
    valid API key to access NSFW content. If the API key is not provided or is invalid,
    the function will return a Sketchy (PG-13) wallpaper instead. It redirects to the
    URL of the selected wallpaper.

    Args:
        apikey (str, optional): The API key for accessing NSFW content. Without this
                                key, the endpoint will default to returning Sketchy content.

    Returns:
        RedirectResponse: A FastAPI response object that redirects the client to the
                          URL of the random NSFW wallpaper. If an IndexError occurs,
                          it defaults to a Sketchy (PG-13) wallpaper.

    Raises:
        IndexError: If the NSFW wallpaper retrieval fails, indicating no wallpapers were
                    found with the '001' NSFW flag, it then attempts to retrieve a
                    wallpaper with the '010' Sketchy flag.
    """
    return RedirectResponse(
        url=get_rnd_wallpaper("nsfw"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/all")
async def all():
    """
    Endpoint to retrieve a random wallpaper from all categories on wallhaven.cc,
    including SFW, Sketchy, and NSFW, depending on the provided API key. If the API
    key is not provided, the function will only return SFW or Sketchy content. It
    redirects to the URL of the selected wallpaper.

    NSFW bits are as follows:
    - '100': Fully SFW content only.
    - '010': Slightly NSFW/PG-13 content.
    - '001': Fully NSFW content.
    These bits can be combined to access multiple categories.

    Args:
        apikey (str, optional): The API key for accessing NSFW content. If omitted,
                                access is restricted to SFW and Sketchy content.

    Returns:
        RedirectResponse: A FastAPI response object that redirects the client to the
                          URL of the random wallpaper selected across all categories.
    """
    nsfw_lvl = choice(["sfw", "pg13", "nsfw"])
    return RedirectResponse(
        url=get_rnd_wallpaper(nsfw_lvl),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/auto")
async def auto(timezone: str = "America/New_York"):
    """
    Endpoint to retrieve a random wallpaper from wallhaven.cc. If a valid API key
    is provided and the current time falls within NSFW time range in the specified timezone,
    NSFW results may be included. Redirects to the wallpaper URL.

    Args:
        apikey (str, optional): The API key for accessing NSFW content. If omitted,
                                NSFW content will not be included in the results.
        timezone (str, optional): The timezone string to determine the NSFW time range.
                                  Defaults to "America/New_York".

    Returns:
        RedirectResponse: A FastAPI response object that redirects the client to the
                          URL of the random wallpaper.

    Raises:
        IndexError: If the wallpaper retrieval fails and defaults to a safe wallpaper
                    with a specific code.
    """
    try:
        return RedirectResponse(
            url=get_rnd_wallpaper(calc_nsfw(timezone)),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        logger.error(e)
        logger.error("Fatal error - Invalid timezome - Overwriting user attribute.")
        return RedirectResponse(
            url=get_rnd_wallpaper(calc_nsfw("America/New_York")),
            status_code=status.HTTP_303_SEE_OTHER,
        )
