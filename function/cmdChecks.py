import discord
import json
from discord import app_commands

with open('./setting.json','r',encoding='utf8') as setting_file:
    setting = json.load(setting_file)

def ownerCheck(interaction:discord.Interaction) -> bool:
    return interaction.user.id== int(setting['OwnerID'])

def topicCooldownExceptOwner(interaction:discord.Interaction):
    if interaction.user.id== int(setting['OwnerID']):
        return None
    return app_commands.Cooldown(30,86400)

def dmOwnerCheck(interaction:discord.Interaction) ->bool:
    if interaction.channel.type==discord.ChannelType.private:
        return interaction.user.id== int(setting['OwnerID'])
    else:
        return True

def transCooldownExceptOwner(interaction:discord.Interaction):
    if interaction.user.id== int(setting['OwnerID']):
        return None
    return app_commands.Cooldown(300,86400)