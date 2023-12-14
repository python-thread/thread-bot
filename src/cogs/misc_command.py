import emoji
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from src.utils import Embeds, Error
from src.config import Config


class Misc(commands.Cog):
  """Miscellaneous commands"""

  client: commands.Bot


  def __init__(self, client):
    self.client = client


  @commands.Cog.listener()
  async def on_ready(self):
    print('Miscellaneous Commands UP')


  @commands.hybrid_command(
    name = 'ping',
    description = 'Print out the current ping',
    with_app_command = True,
    required = True
  )
  @commands.cooldown(1, 15)
  async def ping(self, ctx: commands.Context):
    """
    **Calculates the bot's latency**

    > **Example**
    ```
    /ping
    ```
    """
    replication_rate = 60
    latency = sum([self.client.latency for _ in range(replication_rate)])/replication_rate
    await ctx.reply(f'{ctx.author.mention}', embed = Embeds(
      title = 'Pong! :ping_pong:',
      description = f'{round(latency*1000, 2)}ms',
      color = discord.Color.purple()
    ))


  @commands.hybrid_command(
    name = 'links',
    description = 'Returns the project links',
    with_app_command = True,
  )
  @commands.cooldown(1, 10, commands.BucketType.channel)
  async def links(self, ctx: commands.Context):
    """
    **Returns the project links**

    > **Example**
    ```
    /links
    ```
    """
    await ctx.reply(ctx.author.mention, embed = Embeds(
      title = 'Project Links',
      description = f'[**Github Organization**](https://github.com/python-thread)\n[**Documentation**](https://thread.ngjx.org)'
    ))


  @commands.hybrid_command(
    name = 'getprefix',
    description = 'Returns the current in-use command prefix',
    with_app_command = True,
    required = True,
    aliases = ['prefix']
  )
  @commands.cooldown(1, 15, commands.BucketType.channel)
  async def getprefix(self, ctx: commands.Context):
    """
    **Returns the current in-use command prefix**

    > **Aliases**
    ```
    prefix, getprefix
    ```

    > **Example**
    ```
    /prefix
    /getprefix
    ```
    """
    await ctx.reply(ctx.author.mention, embed = Embeds(
      title = 'Prefix',
      description = str(Config.COMMAND_PREFIX)
    ))


  @commands.hybrid_command(
    name = 'react',
    description = 'Reacts to the message with specified reaction!',
    with_app_command = True,
    aliases = ['addreaction'],
    required = True
  )
  @app_commands.describe(
    reaction = 'What reaction you would like to add',
    messageid = 'Which message you would like to add to'
  )
  @commands.cooldown(1, 5, commands.BucketType.user)
  async def addreaction(self, ctx: commands.Context, reaction: str, messageid: Optional[str] = None):
    """
    **Reacts to the message with specified reaction!**

    > **Arguments**
    ```
    reaction  | string | required
    messageid | string | default = Latest message in channel
    ```

    > **Example**
    ```
    /react    [str]          (str)
    /react :ping_pong:       12345
    /react :ping_pong: https://.../12345
    ```
    """
    if not ctx.guild or not ctx.message.guild: return

    if not emoji.is_emoji(reaction):
      for emojiinfo in ctx.message.guild.emojis:
        if emojiinfo.name == reaction:
          reaction = emojiinfo.animated and f'<a:{emojiinfo.name}:{emojiinfo.id}>' or f'<:{emojiinfo.name}:{emojiinfo.id}>'
          break

    if messageid:
      id = messageid.startswith('https:') and messageid.split('/')[len(messageid.split('/')) - 1] or messageid
    elif isinstance(ctx.message.channel, discord.TextChannel):
      id = str(ctx.message.channel.last_message_id)
    else:
      raise Error('Unsupported channel type')

    message = await ctx.message.channel.fetch_message(int(id))
    await message.add_reaction(reaction)

    embed = Embeds(title = 'Success')
    embed.set_author(name = ctx.author.name, icon_url = ctx.author.display_avatar)
    embed.add_field(name = "Emoji", value = f'`{reaction}`', inline = False)
    embed.add_field(
      name = "Message ID",
      value = f'https://discord.com/channels/{ctx.guild.id}/{ctx.message.channel.id}/{id}',
      inline = False
    )

    await ctx.reply(ctx.author.mention, embed = embed, ephemeral = True)


async def setup(client: commands.Bot):
  await client.add_cog(Misc(client))
