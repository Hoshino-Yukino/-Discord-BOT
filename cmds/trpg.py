import discord
from discord import app_commands
from core.classes import Cog_Extension
from discord.app_commands import locale_str as _T
import random

class Trpg(Cog_Extension):
    @app_commands.command(name="r",description=_T("Draw a dice. Default dice: 1d6"))
    @app_commands.describe(dice=_T("Example: 2d6 - Draw 2 hexahedron"))
    async def r(self,interaction:discord.Interaction,dice:str="NULL"):
        try:
            output = 0
            out_str = "["
            if dice=="NULL":
                dice = "1d6" 
            for i in range(0,int(dice.split("d")[0])):
                now_ran = random.randint(1,int(dice.split("d")[1]))
                output = output + now_ran
                out_str = out_str + str(now_ran)
                if i != int(dice.split("d")[0])-1:
                    out_str = out_str + " , "
            out_str =  out_str + "]"
            await interaction.response.send_message(f"{out_str} = {output}")
            return
        except:
            await interaction.response.send_message(f"パラメータ [ {dice} ] エラー",ephemeral=True)
            return
        



async def setup(bot):
    await bot.add_cog(Trpg(bot))