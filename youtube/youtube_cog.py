import disnake
from disnake.ext import commands
from datetime import timedelta

import asyncio

from .youtube_player import YoutubePlayer


class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player = YoutubePlayer()

    @commands.slash_command(name="go", help="Plays a song")
    async def play_song(self, inter: disnake.ApplicationCommandInteraction, url: str):

        if not inter.author.voice:
            await inter.send("Not connected to the voice channel")
        else:
            channel = inter.author.voice.channel
            voice_client = inter.guild.voice_client
            if voice_client is None or not voice_client.is_playing():
                await channel.connect()

        song = await self.player.add_to_queue(guild_id=inter.guild_id, url=url)

        voice_client = inter.guild.voice_client

        if not voice_client.is_playing():
            song = self.player.pop_from_queue(guild_id=inter.guild_id)
            voice_client.play(
                song.source,
                after=lambda error: self.bot.loop.create_task(
                    self.play_next(inter=inter)
                ),
            )
            duration = timedelta(seconds=song.meta["duration"])
            await inter.response.send_message(
                f"**Now playing: ** {song.title} \n**Duration: ** {str(duration)}"
            )
        else:
            await inter.response.send_message(f"**Added to queue: ** {song.title}")

    @commands.slash_command(name="skip", help="Skips current song")
    async def skip(self, inter: disnake.ApplicationCommandInteraction):
        voice_client = inter.guild.voice_client
        if voice_client.is_playing():
            # stop triggers play_next, where song is popped from queue and then played
            voice_client.stop()
            await inter.send("Skipped current song.")
        else:
            await inter.send("The bot is not playing anything at the moment.")

    @commands.slash_command(name="end", help="Stops the current song and empties queue")
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        voice_client = inter.guild.voice_client
        guild_id = inter.guild_id
        if voice_client.is_playing():
            self.player.clear_queue(guild_id=guild_id)
            voice_client.stop()
        else:
            await inter.send("The bot is not playing anything at the moment.")

    @commands.slash_command(
        name="list", help="Lists the current music queue", auto_sync=True
    )
    async def list(self, inter: disnake.ApplicationCommandInteraction):
        await inter.send(self.player.print_queue(guild_id=inter.guild_id))

    async def play_next(self, inter: disnake.ApplicationCommandInteraction):
        voice_client = inter.guild.voice_client
        voice_client.stop()
        while voice_client.is_playing():
            await asyncio.sleep(1)

        song = self.player.pop_from_queue(guild_id=inter.guild_id)

        voice_client.play(song.source)
        duration = timedelta(seconds=song.meta["duration"])
        await inter.send(
            f"**Now playing: ** {song.title} \n**Duration: ** {str(duration)}"
        )
