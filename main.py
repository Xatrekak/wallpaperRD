from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import starlette.status as status
import requests


def get_rnd_wallpaper():
    response = requests.get(
        "https://wallhaven.cc/api/v1/search?q=anime&categories=110&purity=010&atleast=1920x1080&sorting=random&order=desc&ai_art_filter=1&page=1"
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
