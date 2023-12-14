import discord
from discord import app_commands
from discord.ext import commands

from src.utils import Embeds, Error, ViewPageScroller
from typing import Optional, List


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
  @commands.cooldown(1, 15, commands.BucketType.user)
  async def help(self, ctx: commands.Context, *, query: Optional[str] = None):
    """
    **Help command of the bot**

    > **Arguments**
    ```
    query | string | default=None
    ```

    > **Example**
    ```
    /help
    /help ping
    ```
    """
    embed_data: dict[str, list[list]] = {}
    page_limit = 1

    async def load_cog_commands(cog, cmds):
      if str(self.client.cogs[cog].__doc__).startswith('hidden'): return
      if not cog in embed_data:
        embed_data[cog] = [[]]

      for i in cmds:
        if i.hidden or str(i.help).startswith('hidden') or not await i.can_run(ctx): continue
        if len(embed_data[cog][-1]) >= page_limit:
          embed_data[cog].append([i])
        else:
          embed_data[cog][-1].append(i)

    
    if not query:
      for cogname in self.client.cogs:
        if str(self.client.cogs[cogname].__doc__).startswith('hidden'): continue # Skip hidden cogs

        cog = self.client.get_cog(cogname)
        if cog:
          await load_cog_commands(cogname, cog.walk_commands())

    else:
      query = ''.join(query)
      for cogname in self.client.cogs:
        if query.lower() == cogname.lower() and not str(self.client.cogs[cogname].__doc__).startswith('hidden'):
          cog = self.client.get_cog(cogname)
          if not cog: continue

          await load_cog_commands(cogname, cog.walk_commands())
          break

        elif not str(self.client.cogs[cogname].__doc__).startswith('hidden'):
          cog = self.client.get_cog(cogname)
          if not cog: continue

          for cmd in cog.walk_commands():
            if query.lower().strip() in cmd.qualified_name.lower().strip():
              await load_cog_commands(cogname, [cmd])


    if not embed_data:
      raise Error(
        description = f'Unable to locate module or command' + ((query and f'[{query}]') or '')
      )
    
    else: #clean up
      cleaned = []
      for cogName, pages in embed_data.items():
        for page in pages:
          cleaned.append([cogName, list(page)])
      

    #Setup embed screen navigation
    def load_page(data: tuple):
      if not self.client.user:
        raise Error('Client not logged in!')

      embed = Embeds(
        title = 'Commands',
        description = f'Use `/help <module>` or `/help <command>` for more information about that module or command\n\n**{data[0]}\'s commands**\n\u200d'
      )
      embed.color = discord.Color.blurple()
      embed.set_author(name = self.client.user.name, icon_url = self.client.user.display_avatar)

      for i in data[1]:
        embed.add_field(
          name = f'/{i.qualified_name}',
          value = f'{str(i.help).lstrip().rstrip()}\n‍',
          inline = False
        )

      return embed
      
    scroll_embed = ViewPageScroller(
      ownerid = ctx.author.id,
      load_page = load_page,
      pages = cleaned,
      timeout = 180
    )

    await scroll_embed.send_message(ctx)


  @help.autocomplete('query')
  async def help_autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
    data = []
    command_names = []
    for i in self.client.commands:
      if i.hidden or str(i.help).startswith('hidden'): continue
      command_names += list(i.aliases) + [i.name]

    for name in [cog for cog in self.client.cogs if not str(self.client.cogs[cog].__doc__).startswith('hidden')] + command_names:
      if current.lower() in name.lower():
        data.append(app_commands.Choice(
          name = name,
          value = name
        ))
    return data[0:24]


async def setup(client):
  await client.add_cog(Help(client))
