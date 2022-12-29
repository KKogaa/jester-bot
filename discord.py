#!/bin/python3
import os
from dotenv import load_dotenv
import disnake
from disnake.ext import commands
from admin import Admin
from youtube import Youtube

load_dotenv()

DISCORD_TOKEN = os.getenv("discord_token")


command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True


class BotBase(commands.Bot):
    def __init__(self):

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            # command_prefix=commands.when_mentioned_or("/"),
            intents=disnake.Intents.all(),
            command_sync_flags=command_sync_flags,
        )


if __name__ == "__main__":
    bot = BotBase()
    bot.add_cog(Admin(bot=bot))
    bot.add_cog(Youtube(bot=bot))

    @bot.event
    async def on_ready():
        print("The bot is ready!")

    @bot.slash_command(name="heart")
    async def join(self, ctx):
        await ctx.send("I'm alive.")

    bot.run(DISCORD_TOKEN)
