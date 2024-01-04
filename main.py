from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from datetime import datetime, time
from random import choice
from logging import getLogger
from os import getenv
import requests
import pytz

# Tap into the gunicorn logger
logger = getLogger("gunicorn.error")

# Retrieve the API key from environment variables
API_KEY = getenv('API_KEY')

# Initialize lists to store wallpaper URLs for different categories
SFW_WP_LIST = []
PG13_WP_LIST = []
NSFW_WP_LIST = []


def calc_nsfw(timezone):
    """
    Calculate the appropriate NSFW level based on the current time and day in the given timezone.
    """
    def time_in_range(start, end, current) -> bool:
        """Check if the current time is within the start and end time."""
        return start <= current <= end

    # Define time thresholds
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
    """
    Fetch and populate the wallpaper list for the specified NSFW level.
    """
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
    """
    Get a random wallpaper URL from the list corresponding to the NSFW level.
    """
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

    logger.info("")
    logger.info(f"Nsfw_lvl: {nsfw_lvl} - Remaining length of wp_list: {len(wp_list)}")
    logger.info(wpurl)

    return wpurl

def populate_wp():
    """
    Populate wallpaper lists for all NSFW levels when the script starts.
    """
    fetch_wp_list("sfw")
    fetch_wp_list("pg13")
    fetch_wp_list("nsfw")



populate_wp()
app = FastAPI()


@app.get("/")
async def default():
    """
    Default endpoint to retrieve a random SFW (Safe For Work) wallpaper. 
    This endpoint automatically selects and redirects to a SFW wallpaper URL from wallhaven.cc.

    Returns:
        RedirectResponse: Redirects to a random SFW wallpaper URL with a 302 HTTP status code.
    """
    return RedirectResponse(
        url=get_rnd_wallpaper("sfw"),
        status_code=302,
    )


@app.get("/pg13")
async def pg13():
    """
    Endpoint to retrieve a random PG-13 (slightly NSFW) wallpaper. 
    Redirects to a PG-13 wallpaper URL from wallhaven.cc.

    Returns:
        RedirectResponse: Redirects to a random PG-13 wallpaper URL with a 302 HTTP status code.
    """
    return RedirectResponse(
        url=get_rnd_wallpaper("pg13"),
        status_code=302,
    )


@app.get("/nsfw")
async def nsfw():
    """
    Endpoint to retrieve a random NSFW (Not Safe For Work) wallpaper. 
    Redirects to an NSFW wallpaper URL from wallhaven.cc.

    Returns:
        RedirectResponse: Redirects to a random NSFW wallpaper URL with a 302 HTTP status code.
    """
    return RedirectResponse(
        url=get_rnd_wallpaper("nsfw"),
        status_code=302,
    )


@app.get("/all")
async def all():
    """
    Endpoint to retrieve a random wallpaper from any category (SFW, PG-13, NSFW). 
    The category is randomly selected and the user is redirected to the corresponding wallpaper URL from wallhaven.cc.

    Returns:
        RedirectResponse: Redirects to a randomly selected wallpaper URL with a 302 HTTP status code.
    """
    nsfw_lvl = choice(["sfw", "pg13", "nsfw"])
    return RedirectResponse(
        url=get_rnd_wallpaper(nsfw_lvl),
        status_code=302,
    )


@app.get("/auto")
async def auto(timezone: str = "America/New_York"):
    """
    Endpoint to retrieve a wallpaper based on the current time and the provided timezone. 
    Adjusts the NSFW level of the wallpaper according to the time. In case of an invalid timezone, 
    defaults to 'America/New_York'.

    Args:
        timezone (str, optional): The timezone to determine the NSFW time range. 
                                  Defaults to 'America/New_York'.

    Returns:
        RedirectResponse: Redirects to a wallpaper URL as per calculated NSFW level 
                          with a 302 HTTP status code.

    Raises:
        Exception: Logs and handles exceptions related to invalid timezone input.
    """
    try:
        return RedirectResponse(
            url=get_rnd_wallpaper(calc_nsfw(timezone)),
            status_code=302,
        )
    except Exception as e:
        logger.info("")
        logger.warning(e)
        logger.warning("Fatal error - Invalid timezome - Overwriting user attribute.")
        return RedirectResponse(
            url=get_rnd_wallpaper(calc_nsfw("America/New_York")),
            status_code=302,
        )

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """
    Exception handler for 404 Not Found errors. Redirects to a random SFW wallpaper 
    when an invalid path is requested.

    Args:
        request (Request): The request object.
        exc (HTTPException): The exception object.

    Returns:
        RedirectResponse: Redirects to a random SFW wallpaper URL with a 302 HTTP status code.
    """
    logger.info("")
    logger.error("Fatal error - Invalid path requested - Returning SFW picture.")
    return RedirectResponse(
        url=get_rnd_wallpaper("sfw"),
        status_code=302,
    )

@app.get("/test")
async def test():
    wallpaper_url = get_rnd_wallpaper("sfw")
    response = RedirectResponse(
        url=wallpaper_url,
        status_code=303,
    )
    # Add a custom header with the wallpaper URL
    response.headers['X-Wallpaper-URL'] = wallpaper_url
    return response
