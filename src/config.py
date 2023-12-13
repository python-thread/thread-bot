import os
from dotenv import load_dotenv
from typing import NoReturn, Optional

load_dotenv()

class Config:
  """Configurations"""

  BOT_TOKEN: Optional[str] = os.getenv('BOT_TOKEN')
  COMMAND_PREFIX: str = '$'

  def __init__(self, *args, **kwargs) -> NoReturn:
    raise NotImplementedError('Not instantiable')