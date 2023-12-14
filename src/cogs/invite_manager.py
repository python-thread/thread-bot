import discord
from discord.ext import commands
from typing import Optional

from src.utils import Embeds, Error
from src.config import Config


class Invite(commands.Cog):
  """hidden

  Handles welcoming new members
  """

  client: commands.Bot
  

  def __init__(self, client: commands.Bot) -> None:
    self.client = client


  @commands.Cog.listener()
  async def on_ready(self):
    print('Invite Manager UP')


  @commands.Cog.listener()
  async def on_member_join(self, member: discord.Member):
    guild = self.client.get_guild(Config.GUILD_ID)
    welcome_channel = guild and guild.get_channel(Config.WELCOME_CHANNEL_ID)

    if welcome_channel and isinstance(welcome_channel, discord.TextChannel):
      await welcome_channel.send(member.mention, embed = Embeds(
        title = member.global_name,
        description = f'**Welcome to the server!** 🎉\n\nDon\'t forget to `git checkout `<#{Config.RULE_CHANNEL_ID}>'
      ))


async def setup(client: commands.Bot):
  await client.add_cog(Invite(client))
