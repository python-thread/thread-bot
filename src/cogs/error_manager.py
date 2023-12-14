import math
import traceback
import discord
from discord.ext import commands

from src.utils import Error, Embeds
from src.config import Config


class ErrorManager(commands.Cog):
  """hidden"""

  client: commands.Bot


  def __init__(self, client: commands.Bot):
    self.client = client


  @commands.Cog.listener()
  async def on_ready(self):
    print('Error Manager UP')

  @commands.Cog.listener()
  async def on_command_error(self, ctx, error):
    prefix = Config.COMMAND_PREFIX
    embed = Embeds()
    embed.color = discord.Color.dark_red()

    if isinstance(error, Error):
      embed.description = error.description
      for field in error.fields.values():
        field['inline'] = ('inline' in field) and field['inline'] or False
        embed.add_field(**field)

    elif isinstance(error, commands.CommandNotFound):
      embed.description= f'Command not found! `{prefix}help` for a list of commands!'

    elif isinstance(error, commands.BotMissingPermissions):
      missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
      if len(missing) > 2:
        fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
      else:
        fmt = ' and '.join(missing)
        embed.description = 'I need the **{}** permission(s) to run this command.'.format(fmt)

    elif isinstance(error, commands.DisabledCommand):
      embed.description = 'The command has been disabled!'

    elif isinstance(error, commands.CommandOnCooldown):
      embed.description = 'This command is on cooldown, please retry in {}s.'.format(math.ceil(error.retry_after))

    elif isinstance(error, commands.MissingPermissions):
      missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
      if len(missing) > 2:
        fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
      else:
        fmt = ' and '.join(missing)
        embed.description = 'You need the **{}** permission(s) to use this command.'.format(fmt)

    elif isinstance(error, commands.NoPrivateMessage):
      try:
        await ctx.author.send('This command cannot be used in direct messages.')
      except discord.Forbidden:
        pass

    elif isinstance(error, commands.CheckFailure):
      embed.description = 'You do not have permission to use this command!'

    elif isinstance(error, commands.UserInputError):
      embed.description = f'Invalid arguments! `{prefix}help` for a list of commands!'
      embed.add_field(
        name = 'Invalid Arguments',
        value = error,
        inline = False
      )

    elif isinstance(error, commands.CommandError): # Custom Error
      embed.description = str(error)

    await ctx.reply(ctx.author.mention, embed = embed, ephemeral = True)
    print(error)
    traceback.print_exc()



async def setup(client: commands.Bot):
  await client.add_cog(ErrorManager(client))