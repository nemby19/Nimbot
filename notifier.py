import discord
from discord.ui import View, Button

async def send_video_notification(channel, title, video_id, thumbnail, live=False):

    if live:
        embed = discord.Embed(
            title="🔴 NEMBY WR IS LIVE!",
            description=f"**{title}**\n\n🔥 Come hang out in the stream!",
            color=discord.Color.red()
        )

        button_label = "🔴 Watch Live"

    else:
        embed = discord.Embed(
            title="🎥 NEW VIDEO FROM NEMBY WR!",
            description=f"**{title}**",
            color=discord.Color.red()
        )

        button_label = "▶️ Watch Now"

    embed.set_image(url=thumbnail)

    embed.set_footer(text="Powered by Nimbot 🤖")

    view = View()

    view.add_item(
        Button(
            label=button_label,
            url=f"https://youtu.be/{video_id}"
        )
    )

    await channel.send(
        "@everyone",
        embed=embed,
        view=view
    )