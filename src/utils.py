import discord
from discord.ext import commands
from datetime import datetime


class Embeds(discord.Embed):
  def __init__(self, color = None, **kwargs):
    super().__init__(**kwargs)
    self.timestamp = datetime.utcnow()
    self.color = color or discord.Color.from_rgb(0,191,255) #Deepskyblue


class Error(commands.CommandError):
  def __init__(self, title: str = 'Error', description: str = '-', fields: dict = {}, **kwargs):
    self.title = title
    self.description = description
    self.fields = fields
    super().__init__(**kwargs)


class ViewPageScroller(discord.ui.View):
  def __init__(self, *, ownerid: int, load_page, pages: list = [], timeout = None):
    self.ownerid = ownerid
    self.pages = pages
    self.current_page = 1
    self.load_page = load_page

    super().__init__(
      timeout = timeout
    )

  async def send_message(self, ctx, *args, **kwargs):
    self.message = await ctx.send(view = self, *args, **kwargs)
    await self.update_message()

  async def update_message(self):
    self.update_buttons()
    await self.message.edit(embed = self.create_embed(), view = self)

  def update_buttons(self):
    if (self.current_page == 1) and (self.current_page != len(self.pages)):
      self.first_page_button.disabled = True
      self.next_button.disabled = False
      self.prev_button.disabled = True
      self.last_page_button.disabled = False

      self.first_page_button.style = discord.ButtonStyle.gray
      self.next_button.style = discord.ButtonStyle.primary
      self.prev_button.style = discord.ButtonStyle.gray
      self.last_page_button.style = discord.ButtonStyle.green

    elif (self.current_page > 1) and (self.current_page == len(self.pages)):
      self.first_page_button.disabled = False
      self.next_button.disabled = True
      self.prev_button.disabled = False
      self.last_page_button.disabled = True

      self.first_page_button.style = discord.ButtonStyle.green
      self.next_button.style = discord.ButtonStyle.gray
      self.prev_button.style = discord.ButtonStyle.primary
      self.last_page_button.style = discord.ButtonStyle.gray

    elif (self.current_page == 1) and (self.current_page == len(self.pages)):
      self.first_page_button.disabled = True
      self.next_button.disabled = True
      self.prev_button.disabled = True
      self.last_page_button.disabled = True

      self.first_page_button.style = discord.ButtonStyle.gray
      self.next_button.style = discord.ButtonStyle.gray
      self.prev_button.style = discord.ButtonStyle.gray
      self.last_page_button.style = discord.ButtonStyle.gray

    else:
      self.first_page_button.disabled = False
      self.next_button.disabled = False
      self.prev_button.disabled = False
      self.last_page_button.disabled = False

      self.first_page_button.style = discord.ButtonStyle.green
      self.next_button.style = discord.ButtonStyle.primary
      self.prev_button.style = discord.ButtonStyle.primary
      self.last_page_button.style = discord.ButtonStyle.green

  def create_embed(self) -> discord.Embed:
    data = self.load_page(self.pages[self.current_page - 1])
    data.set_footer(text=f'Page [{self.current_page}/{len(self.pages)}]\n‍')
    return data


  @discord.ui.button(label="|<", style=discord.ButtonStyle.green)
  async def first_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    if interaction.user.id != self.ownerid: return
    await interaction.response.defer()
    self.current_page = 1

    await self.update_message()

  @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
  async def prev_button(self, interaction:discord.Interaction, button: discord.ui.Button):
    if interaction.user.id != self.ownerid: return
    await interaction.response.defer()
    self.current_page -= 1

    await self.update_message()

  @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
  async def next_button(self, interaction:discord.Interaction, button: discord.ui.Button):
    if interaction.user.id != self.ownerid: return
    await interaction.response.defer()
    self.current_page += 1

    await self.update_message()

  @discord.ui.button(label=">|", style=discord.ButtonStyle.green)
  async def last_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
    if interaction.user.id != self.ownerid: return
    await interaction.response.defer()
    self.current_page = len(self.pages)

    await self.update_message()

  @discord.ui.button(label="Done", style=discord.ButtonStyle.blurple)
  async def done(self, interaction:discord.Interaction, button: discord.ui.Button):
    last = self.create_embed()
    last.set_footer(text=f'Page [{self.current_page}/{len(self.pages)}]\nDisabled due to user\n‍')
    await self.message.edit(embed = last, view = None)
    self.stop()

  async def on_timeout(self) -> None:
    last = self.create_embed()
    last.set_footer(text=f'Page [{self.current_page}/{len(self.pages)}]\nDisabled due to timeout\n‍')
    await self.message.edit(embed = last, view = None)
