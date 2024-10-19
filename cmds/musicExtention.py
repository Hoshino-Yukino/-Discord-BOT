import traceback
import discord
from discord import app_commands
from core.classes import Cog_Extension
from function.cmdChecks import ownerCheck

autoPlayListFile = "../MusicBot/config/autoplaylist.txt"

class MusicExtention(Cog_Extension):

    @app_commands.guild_only()
    @app_commands.default_permissions()
    
    class AutoPlayListAdmin(app_commands.Group):
        ...
    autoPlayListAdmin = AutoPlayListAdmin(name="autoplaylist",description="Group for AutoPlayList")

    @autoPlayListAdmin.command(name="add",description="Add song to Bot Autoplaylist「Owner ONLY」")
    @app_commands.check(ownerCheck)
    async def autoPlayListAdd(self,interaction:discord.Interaction,url:str,song_name:str,cover_name:str):
        try:
            f = open(autoPlayListFile,mode="r",encoding="utf-8")    
            lines = f.readlines()
            for line in lines:
                print(line)
                if line =="\n":
                    continue
                lineSongName =  line.split("#")[1].split("「")[0]
                lineCoverName = line.split("「")[1].split("」")[0]
                if lineSongName==song_name and lineCoverName==cover_name:
                    await interaction.response.send_message("この曲は既に自動プレイリストに追加されました",ephemeral=True)
                    return
            f.close()
            with open(autoPlayListFile,"a+",encoding="utf-8") as f:
                f.write(f"{url}#{song_name}「{cover_name}」\n")
            await interaction.response.send_message("追加完成しました。",ephemeral=True)
        except:
            traceback.print_exc()
    
    @autoPlayListAdmin.command(name="delete",description="Delete song from Bot Autoplaylist")
    @app_commands.check(ownerCheck)
    async def autoPlayListDelete(self,interaction:discord.Interaction,song_name:str,cover_name:str):
        f = open(autoPlayListFile,mode="r",encoding="utf-8")    
        lines = f.readlines()
        allLine = ""
        changeFlag = False
        for line in lines:
            lineSongName =  line.split("#")[1].split("「")[0]
            lineCoverName = line.split("「")[1].split("」")[0]
            if (lineSongName!=song_name or lineCoverName!=cover_name)and line!="\n":
                allLine  = allLine + line
            else:
                changeFlag = True
        f.close()
        if changeFlag == True:
            with open(autoPlayListFile,"w+",encoding="utf-8") as f:
                f.write(allLine)
                await interaction.response.send_message("消去完成しました。",ephemeral=True)
                f.close()
                return
        await interaction.response.send_message("この曲は自動プレイリストに含まれていません。",ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(MusicExtention(bot))