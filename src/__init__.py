import os
import discord
from discord.ext import commands

from .config import Config


client = commands.Bot(
  command_prefix = Config.COMMAND_PREFIX,
  intents = discord.Intents.all()
)

# Configuration
@client.event
async def on_ready():
  print(f'Client [{client.user}] UP')

@client.event
async def on_message(message: str):
  # Allow text to invoke comamnds
  await client.process_commands(message)


# Loading cogs
async def load_cogs():
  for filename in os.listdir(os.path.join(os.getcwd(), 'src', 'cogs')):
    if filename.endswith('.py'):
      await client.load_extension(
        f'.cogs.{filename.split("/")[-1][:-3]}',
        package = 'src'
      )


# Main runner
async def main():
  async with client:
    await load_cogs()
    await client.start(Config.BOT_TOKEN)
