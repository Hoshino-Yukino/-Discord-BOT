import discord
from discord import app_commands
from core.classes import Cog_Extension
from function.cmdChecks import *
from function.auditlog import *
import discord.ext

class System(Cog_Extension):
    @app_commands.command(name="ping",description="PING PONG")
    async def ping(self,interaction:discord.Interaction):
        await interaction.response.send_message(str(round(self.bot.latency*1000)) + " ms",ephemeral=True,delete_after=30)
    
    @app_commands.command(name="shutdown",description="Shutdown the BOT 「Owner Only」")
    @app_commands.check(ownerCheck)
    @app_commands.default_permissions()
    async def shutdown(self,interaction:discord.Interaction):
        await addLog(interaction.user.id,f"Shutdown BOT")
        await interaction.response.send_message("またねい",ephemeral=True)
        await self.bot.close()  
    
    @app_commands.command(name='sync', description='Owner only')
    @app_commands.check(ownerCheck)
    @app_commands.default_permissions()
    async def sync(self,interaction: discord.Interaction):
        await self.bot.tree.sync(guild=interaction.guild)
        await addLog(interaction.user.id,f"Sync SLASH COMMAND")
        await interaction.response.send_message("Slash command sync complete",ephemeral=True)

    
    @app_commands.guild_only()
    @app_commands.default_permissions()
    class CogEnableGroup(app_commands.Group):
        ...
    cogGroup = CogEnableGroup(name="cog",description="Group for Cog load/unload「Owner only」")


    @cogGroup.command(name='reload', description='Reload Cog「Owner only」')
    @app_commands.check(ownerCheck)
    @app_commands.default_permissions()
    async def reload(self,interaction: discord.Interaction,cog_name:str):
        try:
            await self.bot.reload_extension(f"cmds.{cog_name}")        
            await interaction.response.send_message("完成しました。",ephemeral=True)        
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            await interaction.response.send_message(f"Extension 'cmds.{cog_name}' is already loaded.",ephemeral=True)
        except discord.ext.commands.errors.ExtensionNotFound:
            await interaction.response.send_message(f"Extension 'cmds.{cog_name}' could not be loaded.",ephemeral=True)
        except discord.ext.commands.errors.ExtensionNotLoaded:
            await interaction.response.send_message(f"Extension 'cmds.{cog_name}' has not been loaded.",ephemeral=True)


    @cogGroup.command(name='load', description='Reload Cog「Owner only」')
    @app_commands.check(ownerCheck)
    @app_commands.default_permissions()
    async def load(self,interaction: discord.Interaction,cog_name:str):
        try:
            await self.bot.load_extension(f"cmds.{cog_name}")        
            await interaction.response.send_message("完成しました。",ephemeral=True)        
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            await interaction.response.send_message(f"Extension 'cmds.{cog_name}' is already loaded.",ephemeral=True)
        except discord.ext.commands.errors.ExtensionNotFound:
            await interaction.response.send_message(f"Extension 'cmds.{cog_name}' could not be loaded.",ephemeral=True)
        except discord.ext.commands.errors.ExtensionNotLoaded:
            await interaction.response.send_message(f"Extension 'cmds.{cog_name}' has not been loaded.",ephemeral=True)


    @cogGroup.command(name='unload', description='Reload Cog「Owner only」')
    @app_commands.check(ownerCheck)
    @app_commands.default_permissions()
    async def unload(self,interaction: discord.Interaction,cog_name:str):
        try:
            await self.bot.unload_extension(f"cmds.{cog_name}")        
            await interaction.response.send_message("完成しました。",ephemeral=True)        
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            await interaction.response.send_message(f"Extension 'cmds.{cog_name}' is already loaded.",ephemeral=True)
        except discord.ext.commands.errors.ExtensionNotFound:
            await interaction.response.send_message(f"Extension 'cmds.{cog_name}' could not be loaded.",ephemeral=True)
        except discord.ext.commands.errors.ExtensionNotLoaded:
            await interaction.response.send_message(f"Extension 'cmds.{cog_name}' has not been loaded.",ephemeral=True)
        


async def setup(bot):
    await bot.add_cog(System(bot))