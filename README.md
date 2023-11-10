# ntbg.app – Dynamic Anime Wallpapers from wallhaven.cc

I'm thrilled to introduce ntbg.app, a new free service that provides random anime wallpapers from wallhaven.cc, tailored to your preference for use with nightTab. Whether you're after something Safe for Work and kid friendly, a Sketchy piece that's is a little more interesting, or you're in the mood for something risqué, ntbg.app has got you covered!
How to use:

Just add the URL to the background field in nightTab! That's it no registration needed.
r/nighttab - Introducing ntbg.app – Dynamic Anime Wallpapers from wallhaven.cc for nightTab
Options:

    / (default): Pull a random wallpaper from wallhaven.cc that has been tagged as Safe for Work:


https://ntbg.app/


    /pg13: For content that's slightly NSFW, hit up the /pg13 endpoint to pull a wallpaper tagged as sketchy. NOTE: Pictures are tagged by wallhaven users so the results can vary and I can NOT guarantee this will be suitable for work or children:


https://ntbg.app/pg13


    /nsfw: For those who dare, this endpoint is strictly NSFW. NOTE: If your wallhaven API key isn't provided or is incorrect, you'll get a PG-13 wallpaper as a fallback:


https://ntbg.app/nsfw?apikey=YOUR_API_KEY


    /all: Want to leave it completely to chance? The /all endpoint fetches a random wallpaper from all categories. Note that if you want to include NSFW results, you'll need to provide your API key. Otherwise you will only get pictures from the SFW and pg13 endpoints:


https://ntbg.app/all?apikey=YOUR_API_KEY


/auto: This endpoint serves you a wallpaper that automatically adjusts its NSFW level based on the time of day in your timezone. It's perfect for those who want a SFW wallpaper during work hours and something a bit more adventurous afterward. Use it like this:

https://ntbg.app/auto?apikey=YOUR_API_KEY&timezone=America/New_York

    Replace YOUR_API_KEY with your API key (required only if you want NSFW content after 10pm) Go to https://wallhaven.cc/settings/account to generate an API key

    (Optional) Replace America/New_York with your actual timezone. If not used New_York timezone is the fallback timezone. List of time zones.

# Why:

I built this for myself! The infrastructure and bandwidth costs are near zero so I decided to share it with anyone interested.

# Security Concerns:

If you use this service I Could potentially see you IP address and wallhaven.cc API key. I don't keep any of these logs and I think the consequences of this is fairly low. But if it is a concern do not use this service.

Instead feel free to deploy your own instance. I included a systemd service showing how to automatically launch the python script as a Linux daemon.
