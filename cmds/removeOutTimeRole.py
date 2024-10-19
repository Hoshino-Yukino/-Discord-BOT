import json
from discord.ext import commands,tasks
from function.role import *

with open('./setting.json','r',encoding='utf8') as setting_file:
    setting = json.load(setting_file)

class RemoveOutTimeRole(commands.Cog):

    def __init__(self,bot):
        self.bot:commands.Bot = bot
        self.removeOutDateRole.start()

    @tasks.loop(minutes=10)
    async def removeOutDateRole(self):
        await self.bot.wait_until_ready()
        conn = sqlite3.connect('DiscordBot.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT discordId,roleId FROM timeRole WHERE datetime('now','localtime')>endTime")
        result = cursor.fetchall()
        for i in range(0,len(result)):
            await self.bot.get_guild(int(setting['ServerId'])).get_member(int(result[i][0])).remove_roles(self.bot.get_guild(int(setting['ServerId'])).get_role(int(result[i][1])),reason="Out Of Date")
            cursor.execute(f"DELETE FROM timeRole WHERE discordId={result[i][0]}")
            conn.commit()
        cursor.close()
        conn.close()
    
async def setup(bot):
    await bot.add_cog(RemoveOutTimeRole(bot))