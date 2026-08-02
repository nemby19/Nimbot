import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def get_uploads_playlist():
    url = (
        f"https://www.googleapis.com/youtube/v3/channels"
        f"?part=contentDetails"
        f"&id={CHANNEL_ID}"
        f"&key={API_KEY}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            if response.status != 200:
                print(await response.text())
                return None

            data = await response.json()

            print("Channel API:", data)

            if not data["items"]:
                return None

            return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")


async def get_latest_video():
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet,id"
        f"&channelId={CHANNEL_ID}"
        f"&order=date"
        f"&type=video"
        f"&maxResults=1"
        f"&key={API_KEY}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            print("Status:", response.status)

            data = await response.json()

            print("Response:", data)

            if response.status != 200:
                return None

            if not data.get("items"):
                return None

            return data["items"][0]


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

            print("YouTube API response:")
            print(data)

            if not data["items"]:
                return None

            item = data["items"][0]

            return {
                "title": item["snippet"]["title"],
                "video_id": item["id"]["videoId"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
            }