from .player import MusicPlayer, Song

import disnake
import asyncio

# BROKEN library
import yt_dlp

# import youtube_dl
# import yt_dlp

# from yt-dlp import YoutubeDL
from urllib.parse import urlparse
from youtubesearchpython import VideosSearch

yt_dlp.utils.bug_reports_message = lambda: ""

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

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


class YoutubePlayer(MusicPlayer):
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
        return (
            parsed_url.netloc == "www.youtube.com"
            and parsed_url.path == "/watch"
        )

    async def _search_url(self, keyword: str) -> str:
        videos_search = VideosSearch(keyword, limit=5, region="US")
        return videos_search.result()["result"][0]["link"]

    async def obtain_audio_source(self, url):
        filename, title, meta = await self.get_youtube_video(
            url=url, stream=True
        )
        source = disnake.FFmpegPCMAudio(source=filename)
        return source, title, meta

    async def get_song_from_url(self, url: str):

        if self._is_youtube_url(url=url):
            url = await self._search_url(keyword=url)

        filename, title, meta = await self.get_youtube_video(
            url=url, stream=True
        )
        source = disnake.FFmpegPCMAudio(source=filename)

        return Song(
            filename=filename,
            title=title,
            meta=meta,
            source=source,
        )
