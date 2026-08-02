import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")


async def get_uploads_playlist():
    url = (
        f"https://www.googleapis.com/youtube/v3/channels"
        f"?part=contentDetails"
        f"&id={CHANNEL_ID}"
        f"&key={API_KEY}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

            if response.status != 200:
                print("Channel API Error:", data)
                return None

            if not data.get("items"):
                print("No channel found.")
                return None

            return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


async def get_latest_video():
    playlist = await get_uploads_playlist()

    if playlist is None:
        return None

    url = (
        f"https://www.googleapis.com/youtube/v3/playlistItems"
        f"?part=snippet"
        f"&playlistId={playlist}"
        f"&maxResults=1"
        f"&key={API_KEY}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            data = await response.json()

            print("Playlist API:", data)

            if response.status != 200:
                return None

            if not data.get("items"):
                return None

            item = data["items"][0]["snippet"]

            return {
                "title": item["title"],
                "video_id": item["resourceId"]["videoId"],
                "thumbnail": item["thumbnails"]["high"]["url"],
            }


async def check_live():
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet"
        f"&channelId={CHANNEL_ID}"
        f"&eventType=live"
        f"&type=video"
        f"&key={API_KEY}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            if response.status != 200:
                return None

            data = await response.json()

            if not data.get("items"):
                return None

            item = data["items"][0]

            return {
                "title": item["snippet"]["title"],
                "video_id": item["id"]["videoId"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
            }