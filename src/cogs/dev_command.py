from discord.ext import commands
from src.check import Protected, PermissionPreset

class DevCommands(commands.Cog, command_attrs = dict(hidden = True), group_extras = dict(hidden = True)):
  """hidden"""

  client: commands.Bot


  def __init__(self, client: commands.Bot):
    self.client = client


  @commands.Cog.listener()
  async def on_ready(self):
    print('Developer Commands UP')


  @commands.command()
  @Protected.legacy(PermissionPreset.Developer)
  async def syncSlashCommands(self, ctx: commands.Context):
    try:
      Sync = await self.client.tree.sync()
      print(f'Synced {len(Sync)} command(s)')
      await ctx.reply(f'{ctx.author.mention} Synced {len(Sync)} command(s)')
    except Exception as e:
      print(e)

  @commands.command()
  @Protected.legacy(PermissionPreset.Developer)
  async def load(self, ctx: commands.Context, extension):
    await self.client.load_extension(f'.cogs.{extension}', package = 'src')
    await ctx.message.add_reaction('✅')

  @commands.command()
  @Protected.legacy(PermissionPreset.Developer)
  async def unload(self, ctx: commands.Context, extension):
    await self.client.unload_extension(f'.cogs.{extension}', package = 'src')
    await ctx.message.add_reaction('✅')

  @commands.command()
  @Protected.legacy(PermissionPreset.Developer)
  async def reload(self, ctx: commands.Context, extension):
    await self.client.unload_extension(f'.cogs.{extension}', package = 'src')
    await self.client.load_extension(f'.cogs.{extension}', package = 'src')
    await ctx.message.add_reaction('✅')
  


async def setup(client: commands.Bot):
  await client.add_cog(DevCommands(client))