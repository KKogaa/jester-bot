#!/bin/python3
import os
from dotenv import load_dotenv
import disnake
from disnake.ext import commands
from admin import Admin
from youtube import Youtube

load_dotenv()

DISCORD_TOKEN = os.getenv("discord_token")


class BotBase(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=disnake.Intents.all(),
        )


if __name__ == "__main__":
    bot = BotBase()
    bot.add_cog(Admin(bot=bot))
    bot.add_cog(Youtube(bot=bot))

    @bot.event
    async def on_ready():
        print("The bot is ready!")


bot.run(DISCORD_TOKEN)
