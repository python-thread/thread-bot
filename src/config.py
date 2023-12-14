import os
from dotenv import load_dotenv
from typing import NoReturn

load_dotenv()

class Config:
  """Configurations"""

  BOT_TOKEN: str = os.getenv('BOT_TOKEN')

  GUILD_ID: int = 1184345962412507157
  RULE_CHANNEL_ID: int = 1184494394682916954
  WELCOME_CHANNEL_ID: int = 1184345962861314050

  COMMAND_PREFIX: str = '$'
  DEVELOPER_USER_ID: int = 470966329931857921

  def __init__(self, *args, **kwargs) -> NoReturn:
    raise NotImplementedError('Not instantiable')
  