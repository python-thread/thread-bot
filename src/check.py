import discord
from discord import app_commands
from discord.ext import commands

from .config import Config
from typing import (
  Any, NoReturn, Literal, Union, Optional,
  List, Sequence, TypedDict
)


class PermissionRequirement(TypedDict):
  """
  Permission Requirement

  Parameters
  ---------------
  :param type: Wheter to whitelist or blacklist this condition
  :param query: The permission scope
  :param value: The permission value
  """
  type: Literal['wl', 'bl']
  query: Literal['in_channel', 'in_guild', 'has_role', 'has_permission', 'is_developer', 'minimum_role']
  value: Optional[Union[str, int]]

class PermissionGate(TypedDict):
  """
  Permission Gate

  Parameters
  ----------
  :param type: Whether the permission gate is required or optional
  :param requirement: The permission requirement
  """
  type: Literal['required', 'optional']
  requirement: PermissionRequirement

class HybridContext:
  """
  Hybrid Context derrived from any command context
  """

  author: Union[discord.User, discord.Member]
  is_developer: bool
  guild: Optional[discord.Guild]
  channel: Any

  def __init__(self, __ctx: Union[discord.Interaction, commands.Context]) -> None:
    """
    Converts a command context or app command context into a HybridContext

    Parameters
    ----------
    :param __ctx: The command context
    """
    self.author = __ctx.user if isinstance(__ctx, discord.Interaction) else __ctx.author
    self.is_developer = (self.author.id == Config.DEVELOPER_USER_ID)
    self.guild = __ctx.guild
    self.channel = __ctx.channel



def _validate_group(ctx: HybridContext, group: List[PermissionGate]) -> bool:
  required: List[bool] = []
  optional: List[bool] = []

  for gate in group:
    passFlag: bool = False

    match gate['requirement']['query']:
      case 'is_developer':
        passFlag = ((gate['requirement']['type'] == 'wl') and ctx.is_developer)

      case 'has_role':
        if ctx.guild and isinstance(ctx.author, discord.Member):
          passFlag = (gate['requirement']['type'] == 'wl') and any(
            gate['requirement']['value'] in [role.id, role.name]
            for role in ctx.author.roles
          )

      case 'has_permission':
        if ctx.guild and isinstance(ctx.author, discord.Member):
          passFlag = (gate['requirement']['type'] == 'wl') and getattr(
            ctx.author.guild_permissions,
            str(gate['requirement']['value'])
          )

      case 'in_channel':
        if ctx.guild and isinstance(ctx.author, discord.Member):
          passFlag = (gate['requirement']['type'] == 'wl') and (
            gate['requirement']['value'] == ctx.channel.id
          )

      case 'in_guild':
        if ctx.guild and isinstance(ctx.author, discord.Member):
          passFlag = (gate['requirement']['type'] == 'wl') and (
            gate['requirement']['value'] in
            [ctx.guild.id, ctx.guild.name]
          )

      case 'minimum_role':
        if ctx.guild and gate['requirement']['value'] and isinstance(ctx.author, discord.Member):
          role = ctx.guild.get_role(int(gate['requirement']['value']))
          passFlag = bool((gate['requirement']['type'] == 'wl') and role and (
            ctx.author.top_role >= role
          ))

    if gate['type'] == 'required':
      required.append(passFlag)
    else:
      optional.append(passFlag)

  return (
    (((len(required) > 0) and all(required)) or True)
    and
    (((len(optional) > 0) and any(optional)) or True)
  )



def validate(__ctx: Union[discord.Interaction, commands.Context], *gates: Union[PermissionGate, Sequence[PermissionGate]]) -> bool:
  """
  Validates a members access to a command

  Parameters
  ----------
  :param __ctx: Command Context [legacy and app command supported]
  :param gates: List of permission gates
  """
  try:
    ctx = HybridContext(__ctx)
    grouped: List[List[PermissionGate]] = [[]]

    # Separate grouped and ungrouped
    for gate in gates:
      if isinstance(gate, Sequence):
        grouped.append(list(gate))
      else:
        grouped[0].append(gate)

    # Validate
    for gate in grouped:
      if len(gate) > 0:
        passFlag = _validate_group(ctx, gate)
        if not passFlag:
          return False
      
    return True
  except Exception as e:
    raise commands.CheckFailure(f'{e}') from e


class Protected:
  @staticmethod
  def app(*clauses: Union[PermissionGate, Sequence[PermissionGate]]):
    """
    Protect app command usage

    Unclaused permission gates are treated as one clause
    All clauses must pass for the user to be allowed access to the command

    Parameters
    ----------
    :param *: Permission gates or clausees of permission gates
    """
    async def predicate(interaction):
      return validate(interaction, *clauses)
    return app_commands.check(predicate)
  
  @staticmethod
  def legacy(*clauses: Union[PermissionGate, Sequence[PermissionGate]]):
    """
    Protect legacy command usage

    Unclaused permission gates are treated as one clause
    All clauses must pass for the user to be allowed access to the command

    Parameters
    ----------
    :param *: Permission gates or clausees of permission gates
    """
    def predicate(ctx):
     return validate(ctx, *clauses)
    return commands.check(predicate)



class PermissionPreset:
  """Permission Presets for repeatedly used permissions"""

  Developer: PermissionGate = {
    'type': 'required',
    'requirement': {
      'type': 'wl',
      'query': 'is_developer',
      'value': None
    }
  }
  Admin: PermissionGate = {
    'type': 'required',
    'requirement': PermissionRequirement(
      type = 'wl',
      query = 'has_permission',
      value = 'administrator'
    )
  }
  WithinServer: PermissionGate = {
    'type': 'required',
    'requirement': PermissionRequirement(
      type = 'wl',
      query = 'in_guild',
      value = Config.GUILD_ID
    )
  }
  Is_Member: PermissionGate = {
    'type': 'required',
    'requirement': PermissionRequirement(
      type = 'wl',
      query = 'minimum_role',
      value = 'Community'
    )
  }

  def __init__(self, *args, **kwargs) -> NoReturn:
    raise NotImplementedError('Non Instantiable')
