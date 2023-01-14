import disnake
from disnake.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f"Welcome {member.mention}.")

    # TODO: TOXIC MODERATION
    # TODO: KICK, BAN, TIMEOUT
