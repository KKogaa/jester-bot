import disnake
from disnake.ext import commands
from datetime import timedelta

import asyncio

from .player import YoutubePlayer


class Youtube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player = YoutubePlayer()

    @commands.slash_command(name="go", description="Plays a song")
    async def play_song(self, inter: disnake.ApplicationCommandInteraction, url: str):
        # Defer the response
        await inter.response.defer(with_message=True)

        if not inter.author.voice:
            await inter.send("Not connected to the voice channel")
            return

        channel = inter.author.voice.channel
        voice_client: disnake.VoiceClient = inter.guild.voice_client

        if not voice_client:
            await channel.connect()
            voice_client: disnake.VoiceClient = inter.guild.voice_client

        song, error = await self.player.add_to_queue(guild_id=inter.guild_id, url=url)

        if error is not None:
            await inter.followup.send(error)
            return

        if not voice_client.is_playing():
            song = self.player.pop_from_queue(guild_id=inter.guild_id)
            if song is not None and song.source is not None:
                voice_client.play(
                    song.source,
                    after=lambda error: self.bot.loop.create_task(
                        self.play_next(inter=inter)
                    ),
                )
                duration = timedelta(seconds=song.meta["duration"])

                await inter.followup.send(
                    f"**Now playing: ** {song.title} \n**Duration: ** {str(duration)}"
                )
                return

        await inter.followup.send(f"**Added to queue: ** {song.title}")

    @commands.slash_command(name="skip", help="Skips the current song")
    async def skip(self, inter: disnake.ApplicationCommandInteraction):
        voice_client: disnake.VoiceClient = inter.guild.voice_client
        if voice_client and voice_client.is_connected():
            # stop triggers play_next, where song is popped from queue and then played
            voice_client.stop()
            await inter.send("Skipped current song.")
            return

        await inter.send("The bot is not playing anything at the moment.")

    @commands.slash_command(
        name="kill", description="Kills music bot and empties queue"
    )
    async def kill(self, inter: disnake.ApplicationCommandInteraction):
        voice_client: disnake.VoiceClient = inter.guild.voice_client
        guild_id = inter.guild_id
        if voice_client and voice_client.is_connected():
            self.player.clear_queue(guild_id=guild_id)
            voice_client.disconnect()
            return

        await inter.send("The bot is not playing anything at the moment.")

    @commands.slash_command(
        name="list",
        description="Lists the current music queue",
        auto_sync=True,
    )
    async def list(self, inter: disnake.ApplicationCommandInteraction):
        await inter.send(self.player.print_queue(guild_id=inter.guild_id))

    async def play_next(self, inter: disnake.ApplicationCommandInteraction):
        voice_client: disnake.VoiceClient = inter.guild.voice_client
        song = self.player.pop_from_queue(guild_id=inter.guild_id)

        if song is None:
            self.player.clear_queue(guild_id=inter.guild_id)
            await voice_client.disconnect()
            return

        voice_client.play(song.source)
        duration = timedelta(seconds=song.meta["duration"])
        await inter.send(
            f"**Now playing: ** {song.title} \n**Duration: ** {str(duration)}"
        )
