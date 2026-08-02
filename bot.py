import os
import discord
import aiohttp
import asyncio
from dotenv import load_dotenv
from storage import (
    load_last_video,
    save_last_video,
    load_last_live,
    save_last_live
)
from youtube import (
    check_live,
    get_latest_video,
    get_uploads_playlist
)
from notifier import send_video_notification

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")
print("DISCORD_CHANNEL_ID from env:", repr(os.getenv("DISCORD_CHANNEL_ID")))

DISCORD_CHANNEL = os.getenv("DISCORD_CHANNEL_ID")

if DISCORD_CHANNEL is None:
    raise RuntimeError("DISCORD_CHANNEL_ID environment variable is missing!")

DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

tree = discord.app_commands.CommandTree(client)

last_video = load_last_video()
last_live = load_last_live()

async def check_youtube():

    global last_video

    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?key={API_KEY}"
        f"&channelId={CHANNEL_ID}"
        f"&part=snippet,id"
        f"&order=date"
        f"&maxResults=1"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            if response.status != 200:
                return

            data = await response.json()

            if not data["items"]:
                return

            item = data["items"][0]

            if item["id"]["kind"] != "youtube#video":
                return

            video_id = item["id"]["videoId"]

            if video_id == last_video:
                return

            last_video = video_id
            save_last_video(video_id)

            title = item["snippet"]["title"]

            channel = client.get_channel(DISCORD_CHANNEL_ID)

            if channel:
                thumbnail = item["snippet"]["thumbnails"]["high"]["url"]

                await send_video_notification(
                    channel,
                    title,
                    video_id,
                    thumbnail
                )

async def check_live_notification():
    global last_live

    stream = await check_live()

    if stream is None:
        return

    if stream["video_id"] == last_live:
        return

    last_live = stream["video_id"]
    save_last_live(last_live)

    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if channel:
        await send_video_notification(
            channel,
            stream["title"],
            stream["video_id"],
            stream["thumbnail"],
            live=True
        )

        

@client.event
async def on_ready():

    print(f"Logged in as {client.user}")

    guild = discord.Object(id=1487198854150361272)

    tree.copy_global_to(guild=guild)
    await tree.sync(guild=guild)

    print("Slash commands synced!")

async def background_tasks():
    try:
        playlist = await get_uploads_playlist()
        print("Uploads Playlist:", playlist)
    except Exception as e:
        print("ERROR in get_uploads_playlist():", repr(e))
        print("No live stream information available.")

    while True:
        try:
            await check_youtube()
            await check_live_notification()
        except Exception as e:
            print(e)

        await asyncio.sleep(60)

@tree.command(name="ping", description="Checks if Nimbot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Nimbot is online.")

@tree.command(name="latest", description="Shows the latest YouTube upload.")
async def latest(interaction: discord.Interaction):

    video = await get_latest_video()

    if video is None:
        await interaction.response.send_message("❌ Couldn't find any videos.")
        return

    title = video["title"]
    video_id = video["video_id"]

    embed = discord.Embed(
        title="🎬 Latest Upload",
        description=title,
        color=discord.Color.red()
    )

    embed.add_field(
        name="Watch here",
        value=f"https://youtu.be/{video_id}",
        inline=False
    )

    embed.set_thumbnail(url=video["thumbnail"])

    await interaction.response.send_message(embed=embed)

@tree.command(name="live", description="Check if Nemby WR is live.")
async def live(interaction: discord.Interaction):

    stream = await check_live()

    if stream is None:
        await interaction.response.send_message(
            "⚫ Nemby WR is currently offline."
        )
        return

    embed = discord.Embed(
        title="🔴 Nemby WR is LIVE!",
        description=stream["title"],
        color=discord.Color.red()
    )

    embed.set_image(url=stream["thumbnail"])

    embed.add_field(
        name="Watch Live",
        value=f"https://youtube.com/watch?v={stream['video_id']}",
        inline=False
    )

    await interaction.response.send_message(embed=embed)

print("Token loaded:", TOKEN is not None)
print("Token length:", len(TOKEN) if TOKEN else 0)

client.run(TOKEN)