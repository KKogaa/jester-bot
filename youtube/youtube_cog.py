import os
import disnake
from disnake.ext import commands
from datetime import timedelta
import urllib
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from apiclient.discovery import build
from oauth2client import client  # Added
from oauth2client import tools  # Added
from oauth2client.file import Storage  # Added

import youtube_dl
import asyncio
from asyncio import coroutine, run

from youtubesearchpython import VideosSearch

###############################################
# YOUTUBE DL AND FFMPEG
###############################################

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
    "outtmpl": SAVE_PATH + "%(title)s.%(ext)s",
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

###############################################
# GOOGLE STUFF
###############################################
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


###############################################


class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.head = {}

    async def get_youtube_video(self, url: str, stream: bool = False):
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )
        if "entries" in data:
            data = data["entries"][0]
        filename = data["url"] if stream else ytdl.prepare_filename(data)
        title = data["title"]
        return filename, title, data

    def _is_youtube_url(self, url: str) -> bool:
        parsed_url = urlparse(url)
        return parsed_url.netloc == "www.youtube.com" and parsed_url.path == "/watch"

    async def _search_url(self, keyword: str) -> str:
        videos_search = VideosSearch(keyword, limit=20)
        videos_result = videos_search.result()

        print("!!!!!!!!!!!!!!!!11")
        for video in videos_result["result"]:
            print(video["title"])
        print("!!!!!!!!!!!!!!!!11")

        return videos_result["result"][0]["link"]

    @commands.command(name="join")
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("Not connected to the voice channel")
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    async def obtain_audio_source(self, url):
        filename, title, meta = await self.get_youtube_video(url=url, stream=True)
        source = disnake.FFmpegPCMAudio(source=filename)
        return source, title, meta

    @commands.command(name="play", help="Plays a song")
    async def play(self, ctx, url: str):

        try:
            await self.join(ctx)
        except Exception as e:
            pass

        voice_client = ctx.message.guild.voice_client

        try:
            if not self._is_youtube_url(url):
                url = await self._search_url(url)
            source, title, meta = await self.obtain_audio_source(url=url)
        except Exception as e:
            await ctx.send(f"Error obtaining video. {e}")
        guild_id = ctx.message.guild.id

        if not voice_client.is_playing():
            self.queues[guild_id] = []
            player = voice_client.play(
                source,
                after=lambda error: self.bot.loop.create_task(
                    self.play_next_in_queue(ctx=ctx, id=guild_id)
                ),
            )
            duration = timedelta(seconds=meta["duration"])
            self.head = {"title": title, "meta": meta}
            await ctx.send(
                f"**Now playing: ** {title} \n**Duration: ** {str(duration)}"
            )
        else:
            self.queues[guild_id].append((url, title, meta))
            await ctx.send(f"**Added to queue: ** {title}")

    async def play_next_in_queue(self, ctx, id):
        if self.queues[id] != []:
            voice = ctx.guild.voice_client
            voice.stop()
            while voice.is_playing():
                await asyncio.sleep(1)
            url, _, _ = self.queues[id].pop(0)
            source, title, meta = await self.obtain_audio_source(url=url)
            player = voice.play(source)
            duration = timedelta(seconds=meta["duration"])
            await ctx.send(
                f"**Now playing: ** {title} \n**Duration: ** {str(duration)}"
            )

    @commands.command(name="skip", help="Skips current song")
    async def skip(self, ctx):
        voice_client = ctx.message.guild.voice_client
        guild_id = ctx.message.guild.id
        if voice_client.is_playing():
            await self.play_next_in_queue(ctx=ctx, id=guild_id)
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name="stop", help="Stops the current song and empties queue")
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        guild_id = ctx.message.guild.id
        if voice_client.is_playing():
            self.queues[guild_id] = []
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name="list", help="Lists the current music queue")
    async def list(self, ctx):
        guild_id = ctx.message.guild.id
        if guild_id not in self.queues:
            await ctx.send("The music queue is empty at the moment.")

        titles = [title for url, title, meta in self.queues[guild_id]]

        head_title = self.head.get("title")
        message = f"**HEAD. **{head_title}"
        for pos, title in enumerate(titles):
            message += f"\n**{pos}. **{title}"

        message += f"\n**Number of songs in queue: **{len(titles)}"

        head_duration = self.head.get("meta", {}).get("duration", 0)
        durations = [meta["duration"] for _, _, meta in self.queues[guild_id]]
        durations.append(head_duration)
        total_duration = sum(durations)
        total_duration = timedelta(seconds=total_duration)
        message += f"\n**Estimated total duration: **{str(total_duration)}"

        await ctx.send(f"{message}")
