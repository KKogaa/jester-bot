import disnake
from disnake.ext import commands

import youtube_dl
import asyncio

youtube_dl.utils.bug_reports_message = lambda: ""

SAVE_PATH = "./youtube/music_files/youtube/"

ytdl_format_options = {
    "format": "bestaudio/best",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    'outtmpl':SAVE_PATH + '%(title)s.%(ext)s',
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #validate if url is an url
    #if url is a normal word search for url

    async def get_youtube_video(self, url: str):
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=True)
        )
        if "entries" in data:
            data = data["entries"][0]
        filename = ytdl.prepare_filename(data)
        title = data["title"]
        return filename, title 

    @commands.command(name="join")
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("Not connected to the voice channel")
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command(name="play", help="Plays a song")
    async def play(self, ctx, url: str):

        try:
            await self.join(ctx)
        except Exception as e:
            pass

        try:
            filename, title = await self.get_youtube_video(url)
            voice_channel = ctx.message.guild.voice_client
            voice_channel.play(
                disnake.FFmpegPCMAudio(source=filename)
            )
            await ctx.send(f'**Now playing:** {title}')
        except Exception as e:
            print(e)
            await ctx.send("The bot is not connected to a voice channel.")

    
    @commands.command(name="skip", help="Skips current song")
    async def skip(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")