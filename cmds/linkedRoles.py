import datetime
import json
import aiohttp
import discord
from urllib import parse
from discord import app_commands
from core.classes import Cog_Extension
from function.cmdChecks import *
from function.jrrp import *
from function.eco import *
from function.auditlog import addLog
from function.role import addLinkedRoleData,removeRoleData,getDiscordTokens,storeDiscordTokens
with open('./setting.json','r',encoding='utf8') as setting_file:
    setting = json.load(setting_file)

class LinkedRoles(Cog_Extension):
    @app_commands.command(name="edit-metadata",description="Edit user's metadata to edit linked-roles 「Owner/Admin ONLY」")
    @app_commands.check(dmOwnerCheck)
    @app_commands.default_permissions()
    @app_commands.choices(
        metadata=[
            discord.app_commands.Choice(name="グランドマスター",value="UroborosOwner"),
            discord.app_commands.Choice(name="アンギス",value="UroborosAdmin"),
            discord.app_commands.Choice(name="レギオン",value="UroborosModerator"),
    ])
    async def editMetadata(self,interaction:discord.Interaction,user:discord.Member,metadata:discord.app_commands.Choice[str],value:bool):
        if (interaction.user.id != 910371227372245002) and (user.id==910371227372245002):
            interaction.response.send_message(content="You have no permission to do that", ephemeral=True)
        if (interaction.user.top_role.id==1123703097517162587) and (user.top_role.id==1123703097517162587):
            interaction.response.send_message(content="You have no permission to do that", ephemeral=True)
        if (interaction.user.top_role.id==1123703097517162587) and (metadata.value!="Moderator"):
            interaction.response.send_message(content="You have no permission to do that", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True,thinking=True)
        if value==True:
            await addLinkedRoleData(DiscordId=user.id,Role=metadata.value)
            await interaction.followup.send("セットアップ成功しました。")
            await user.send(content=f"{interaction.user.mention}はあなたの`{metadata.name}`ロールを設定しました。ウロボロスサーバーに入って連携ロールをクリックして修正を取得してください。")
            await addLog(interaction.user.id,f"User:{user.id}, set metadata {metadata.value}=True")
            return
        else:
            returnFlag = await removeRoleData(DiscordId=user.id,Role=metadata.value)
            
            if returnFlag == 1:
                tokens= await getDiscordTokens(user.id)
                if (datetime.datetime.now() - datetime.datetime.strptime(tokens[3].split(".")[0],"%Y-%m-%d %H:%M:%S")).total_seconds() >= 0:
                    url = 'https://discord.com/api/v10/oauth2/token'
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }                  
                    body = {
                        'client_id': setting["CLIENT_ID"],
                        'client_secret': setting["CLIENT_SECRET"],
                        'grant_type': 'refresh_token',
                        'refresh_token': tokens[2],
                    }
                    # print(parse.urlencode(body))
                    # response = requests.post(url, data=body) 
                    # responseTokens = response.json()                   
                    async with aiohttp.ClientSession(headers=headers) as client:
                        async with client.post(url,data=parse.urlencode(body)) as resp:
                            responseTokens = await resp.json()
                        await client.close()
                    await storeDiscordTokens(user.id, responseTokens)
                    accessToken = responseTokens['access_token']
                else:
                    accessToken = tokens[1]
                url = f'https://discord.com/api/v10/users/@me/applications/{setting["CLIENT_ID"]}/role-connection'
                owner=False
                admin=False
                moderator=False
                returnFlag=0
                if tokens[4]==1:
                    owner=True
                if tokens[5]==1:
                    returnFlag=1
                if tokens[6]==1:
                    moderator=True
                metadata = {
                    'owner': owner,
                    'admin': admin,
                    'moderator': moderator,
                }
                headers={
                    'Authorization': f'Bearer {accessToken}',
                    'Content-Type': 'application/json',
                }                
                body = {
                    'platform_name': 'Linked Role Discord Bot',
                    'metadata': metadata,
                }
                async with aiohttp.ClientSession(headers=headers) as client:
                    async with client.put(url,data=json.dumps(body)) as resp:
                        tokens = await resp.json()
                    await client.close()
            await interaction.followup.send("セットアップ成功しました。")
            await addLog(interaction.user.id,f"User:{user.id}, set metadata {metadata.value}=False")
            return
        
        

async def setup(bot):
    await bot.add_cog(LinkedRoles(bot))