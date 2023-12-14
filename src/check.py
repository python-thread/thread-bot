import discord
from discord import app_commands
from discord.ext import commands
from discord import abc
from config import Config

from typing import (
  NoReturn, Literal, Union, Optional,
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
  query: Literal['in_channel', 'has_role', 'has_permission', 'is_developer', 'minimum_role']
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
  channel: Optional[Union[abc.GuildChannel, abc.PrivateChannel, discord.Thread]]

  def __init__(self, __ctx: Union[discord.Interaction, commands.Context]) -> None:
    """
    Converts a command context or app command context into a HybridContext

    Parameters
    ----------
    :param __ctx: The command context
    """
    self.author = (isinstance(__ctx, discord.Interaction) and __ctx.user) or __ctx.author
    self.is_developer = (self.author.id == Config.DEVELOPER_USER_ID)
    self.guild = __ctx.guild
    self.channel = __ctx.channel



def _validate_group(ctx: HybridContext, group: Sequence[PermissionGate]) -> bool:
  required: List[bool] = []
  optional: List[bool] = []

  for gate in group:
    passFlag = False

    match gate['requirement']['query']:
      case 'is_developer':
        passFlag = (gate['requirement']['type'] == 'wl') and ctx.is_developer
        break

      case 'has_role':
        if ctx.guild:
          passFlag = (gate['requirement']['type'] == 'wl') and any(
            gate['requirement']['value'] in [role.id, role.name]
            for role in ctx.author.roles
          )

      case 'has_permission':
        if ctx.guild:
          passFlag = (gate['requirement']['type'] == 'wl') and getattr(
            ctx.author.guild_permissions,
            gate['requirement']['value']
          )

      case 'in_channel':
        if ctx.guild:
          passFlag = (gate['requirement']['type'] == 'wl') and (
            gate['requirement']['value'] == ctx.channel.id
          )

      case 'minimum_role':
        if ctx.guild:
          role = ctx.guild.get_role(gate['requirement']['value'])
          passFlag = (gate['requirement']['type'] == 'wl') and role and (
            ctx.author.top_role >= role
          )

    if gate['type'] == 'required':
      required.append(passFlag)
    else:
      optional.append(passFlag)

  return bool(all(required) and any(optional))



def validate(__ctx: Union[discord.Interaction, commands.Context], *gates: Sequence[Union[PermissionGate, Sequence[PermissionGate]]]) -> bool:
  """
  Validates a members access to a command

  Parameters
  ----------
  :param __ctx: Command Context [legacy and app command supported]
  :param gates: List of permission gates
  """
  ctx = HybridContext(__ctx)

  ungrouped: List[PermissionGate] = []
  grouped: List[List[PermissionGate]] = []

  # Separate grouped and ungrouped
  for gate in gates:
    if isinstance(gate, PermissionGate):
      ungrouped.append(gate)
    else:
      grouped.append(gate)

  # Validate
  joined: List[List[PermissionGate]] = [ungrouped, *grouped]
  for gate in joined:
    passFlag = _validate_group(ctx, gate)
    if not passFlag:
      return False
    
  return True



class Protected():
  def app(*clauses: Union[PermissionGate, Sequence[PermissionGate]]):
    """
    Protect app command usage

    Unclaused permission gates are treated as one clause
    All clauses muts pass for the user to be allowed access to the command

    Parameters
    ----------
    :param *: Permission gates or clausees of permission gates
    """
    async def _run(interaction):
      return validate(interaction, *clauses)
    return app_commands.check(_run)

  def legacy(*clauses: Union[PermissionGate, Sequence[PermissionGate]]):
    """
    Protect legacy command usage

    Unclaused permission gates are treated as one clause
    All clauses muts pass for the user to be allowed access to the command

    Parameters
    ----------
    :param *: Permission gates or clausees of permission gates
    """
    def _run(ctx):
     return validate(ctx, *clauses)
    return commands.check(_run)



class PermissionPreset:
  """Permission Presets for repeatedly used permissions"""

  Developer: PermissionRequirement = {
    'origin': 'guild',
    'type': 'wl',
    'query': 'is_developer',
    'value': None
  }
  Admin: PermissionRequirement = {
    'origin': 'guild',
    'type': 'wl',
    'query': 'has_permission',
    'value': 'administrator'
  }
  WithinServer: PermissionRequirement = {
    'origin': 'guild',
    'type': 'wl',
    'query': 'in_guild',
    'value': Config.GUILD_ID
  }
  Is_Member: PermissionRequirement = {
    'origin': 'data',
    'type': 'wl',
    'query': 'minimum_role',
    'value': 'Community'
  }

  def __init__(self, *args, **kwargs) -> NoReturn:
    raise NotImplementedError('Non Instantiable')
