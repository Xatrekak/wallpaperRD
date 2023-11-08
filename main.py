from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import starlette.status as status
import requests
import datetime
import logging
import pytz

logger = logging.getLogger("uvicorn")


# Set the NSFW level values 0 = disabled 1 = enabled.
# AUTO returns time based results
def calc_nsfw(timezone):
    def time_in_range(start, end, current):
        """Returns whether current is in the range [start, end]"""
        return start <= current <= end

    seven_am = datetime.time(7, 0, 0)
    five_pm = datetime.time(17, 0, 0)
    ten_pm = datetime.time(22, 0, 0)
    day = datetime.datetime.today().weekday()

    current = datetime.datetime.now(pytz.timezone(timezone)).time()

    if time_in_range(seven_am, five_pm, current):
        if day < 5:
            nsfw_level = "100"
        else:
            nsfw_level = "010"
    elif time_in_range(five_pm, ten_pm, current):
        nsfw_level = "010"
    else:
        nsfw_level = "001"

    return nsfw_level


def get_rnd_wallpaper(purity="100", apikey=""):
    try:
        response = requests.get(
            f'https://wallhaven.cc/api/v1/search?{"apikey=" + apikey + "&"}categories=010&{"purity=" + purity + "&"}atleast=1920x1080&ratios=16x9%2C16x10&sorting=random&order=desc&ai_art_filter=1&page=1'
        )
    
        wpurl = response.json()["data"][0]["path"]
        logger.info(purity)
        logger.info(wpurl)
    except Exception as error:
        response = requests.get(
            f'https://wallhaven.cc/api/v1/search?categories=010&purity=100&atleast=1920x1080&ratios=16x9%2C16x10&sorting=random&order=desc&ai_art_filter=1&page=1'
        )
    
        wpurl = response.json()["data"][0]["path"]
        logger.error(f"Fatal Error - Overwriting attributes:\n{error}")

    return wpurl


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
        url=get_rnd_wallpaper("100"),
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
        url=get_rnd_wallpaper("010"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/nsfw")
async def nsfw(apikey: str = ""):
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
    try:
        return RedirectResponse(
            url=get_rnd_wallpaper("001", apikey),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except IndexError:
        # Fallback to a Sketchy wallpaper if NSFW content cannot be retrieved.
        return RedirectResponse(
            url=get_rnd_wallpaper("010"),
            status_code=status.HTTP_303_SEE_OTHER,
        )


@app.get("/all")
async def all(apikey: str = ""):
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
    return RedirectResponse(
        url=get_rnd_wallpaper("111", apikey),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/auto")
async def auto(apikey: str = "", timezone: str = "America/New_York"):
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
            url=get_rnd_wallpaper(calc_nsfw(timezone), apikey),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except IndexError:
        # Fallback to a Sketchy wallpaper if NSFW content cannot be retrieved.
        return RedirectResponse(
            url=get_rnd_wallpaper("010", apikey),
            status_code=status.HTTP_303_SEE_OTHER,
        )
