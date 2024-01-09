# ntbg.app – Dynamic Anime Wallpapers from wallhaven.cc

I'm thrilled to introduce ntbg.app, a new free service that provides random anime wallpapers from wallhaven.cc, tailored to your preference for use with nightTab. Whether you're after something Safe for Work and kid friendly, a Sketchy piece that's is a little more interesting, or you're in the mood for something risqué, ntbg.app has got you covered!

# Update
API Keys are no longer required for the endpoints!

# How to use:

Just add the URL to the background field in nightTab! That's it no registration needed.
r/nighttab - Introducing ntbg.app – Dynamic Anime Wallpapers from wallhaven.cc for nightTab
Options:

    / (default): Pull a random wallpaper from wallhaven.cc that has been tagged as Safe for Work:


https://ntbg.app/


    /pg13: For content that's slightly NSFW, hit up the /pg13 endpoint to pull a wallpaper tagged as sketchy. NOTE: Pictures are tagged by wallhaven users so the results can vary and I can NOT guarantee this will be suitable for work or children:


https://ntbg.app/pg13


    /nsfw: For those who dare, this endpoint is strictly NSFW.


https://ntbg.app/nsfw


    /all: Want to leave it completely to chance? The /all endpoint fetches a random wallpaper from all categories.


https://ntbg.app/all


    /auto: This endpoint serves you a wallpaper that automatically adjusts its NSFW level based on the time of day in your timezone. It's perfect for those who want a SFW wallpaper during work hours and something a bit more adventurous afterward. Use it like this:

https://ntbg.app/auto&timezone=America/New_York

    (Optional) Replace America/New_York with your actual timezone. If not used New_York timezone is the fallback timezone. List of time zones.

# Why:

I built this for myself! The infrastructure and bandwidth costs are near zero so I decided to share it with anyone interested.

# Security Concerns:

If you use this service I Could potentially see you IP address. I don't keep any of these logs and I think the consequences of this is fairly low. But if it is a concern do not use this service.

Instead feel free to deploy your own instance. I included a systemd service showing how to automatically launch the python script as a Linux daemon.
