import discord
from discord import app_commands
from discord.ext import commands

from src.utils import Embeds, Error


class Help(commands.Cog):
  """
  Sends this help message
  """

  client: commands.Bot


  def __init__(self, client: commands.Bot):
    self.client = client
    client.remove_command('help')


  @commands.Cog.listener()
  async def on_ready(self):
    print('Help command UP')


  @commands.hybrid_command(
    name = 'help',
    description = 'Sends the Help Command',
    with_app_command = True,
    required = True
  )
  @app_commands.describe(
    query = 'Module\'s or Command\'s name'
  )
  @commands.cooldown(1, 15)
  async def help(self, ctx, query: str = None):
    """Shows all modules of that bot"""

    embed = Embeds(
      title = 'Commands',
      description = f'Use `/help <module>` or `/help <command>` for more information about that module or command\n\u200d'
    )
    embed.color = discord.Color.blurple()

    if not query:
      available_cogs = []
      for cog in self.client.cogs:
        available_commands = []
        for cmd in self.client.get_cog(cog).walk_commands():
          if not cmd.hidden and not str(cmd.help).startswith('hidden') and await cmd.can_run(ctx):
            available_commands.append(cmd)

        if len(available_commands) > 0:
          available_cogs.append(cog)

      embed.add_field(
        name = 'Modules',
        value = '\n\u200d\n'.join(
          f'**{cog}**\n```{str(self.client.cogs[cog].__doc__).lstrip().rstrip()}```' for cog in available_cogs if (
            not str(self.client.cogs[cog].__doc__).startswith('hidden')
          )
        ),
        inline = False
      )

    else:
      found = False
      async def add_to_embed(cmd):
        if await cmd.can_run(ctx):
          embed.add_field(
            name = f'/{cmd.qualified_name}',
            value = f'{str(cmd.help).lstrip().rstrip()}\n‍',
            inline = False
          )

      for cog in self.client.cogs:
        if query.lower() == cog.lower() and not str(self.client.cogs[cog].__doc__).startswith('hidden'):
          embed.description += f'\n**{cog}\'s commands**\n\u200d'
          available_commands_cog = []

          for cmd in self.client.get_cog(cog).walk_commands():
            if (not cmd.hidden and not str(cmd.help).startswith('hidden')) and await cmd.can_run(ctx):
              available_commands_cog.append(cmd)

          if len(available_commands_cog) > 0:
            for i in available_commands_cog: await add_to_embed(i)
            found = True
          break

        elif not str(self.client.cogs[cog].__doc__).startswith('hidden'):
          for cmd in self.client.get_cog(cog).walk_commands():
            if (not cmd.hidden and not str(cmd.help).startswith('hidden')):
              if query.lower().strip() in cmd.qualified_name.lower().strip():
                found = True
                await add_to_embed(cmd)

          if found: break
      if not found:
        raise Error(description = f'Unable to locate module or command [{query}]')

    await ctx.reply(embed = embed)


async def setup(client: commands.Bot):
  await client.add_cog(Help(client))
  