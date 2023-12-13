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
