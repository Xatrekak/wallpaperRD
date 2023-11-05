from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import starlette.status as status
import requests
import datetime

# Set the NSFW level values 0 = disabled 1 = enabled.
# AUTO overwrites the values and returns time based results
NSFW_FLAGS = {
    "SFW": "1",
    "PG_13": "1",
    "NSFW": "0",
    "auto": False
    }

# A wallhaven.cc API key is REQUIRED if and only if you want NSFW results
API_KEY = ""


def calc_nsfw():
    if not NSFW_FLAGS["auto"]:
        nsfw_level = NSFW_FLAGS["SFW"] + NSFW_FLAGS["PG_13"] + NSFW_FLAGS["NSFW"]
        return nsfw_level

    def time_in_range(start, end, current):
        """Returns whether current is in the range [start, end]"""
        return start <= current <= end

    nine_am = datetime.time(9, 0, 0)
    five_pm = datetime.time(17, 0, 0)
    ten_pm = datetime.time(22, 0, 0)
    day = datetime.datetime.today().weekday()

    current = datetime.datetime.now().time()

    if time_in_range(nine_am, five_pm, current):
        if day < 5:
            nsfw_level = "100"
        else:
            nsfw_level = "010"
    elif time_in_range(five_pm, ten_pm, current):
        nsfw_level = "010"
    else:
        if API_KEY:
            nsfw_level = "001"
        else:
            nsfw_level = "010"

    return nsfw_level


def get_rnd_wallpaper():
    nsfw_level = "purity=" + calc_nsfw() + "&"
    api_key = "apikey=" + API_KEY + "&"

    response = requests.get(
        f"https://wallhaven.cc/api/v1/search?{api_key}categories=010&{nsfw_level}atleast=1920x1080&ratios=16x9%2C16x10&sorting=random&order=desc&ai_art_filter=1&page=1"
    )

    wpurl = response.json()["data"][0]["path"]

    return wpurl

app = FastAPI()

@app.get("/")
async def main():
    # Redirect to /docs (relative URL)
    get_rnd_wallpaper()
    return RedirectResponse(
        url=get_rnd_wallpaper(),
        status_code=status.HTTP_303_SEE_OTHER,
    )
