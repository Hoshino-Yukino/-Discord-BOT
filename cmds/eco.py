import json
import aiohttp
import discord
from discord import app_commands
from core.classes import Cog_Extension
from function.jrrp import *
from function.eco import *
from function.auditlog import *

class ECO(Cog_Extension):
    @app_commands.command(name="property",description="Show your total property")
    @app_commands.guild_only()
    async def property(self,interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not await ecoIsInit(interaction.user.id):
            await ecoInit(interaction.user.id)
        url = f"https://unbelievaboat.com/api/v1/guilds/{interaction.guild_id}/users/{interaction.user.id}"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIxMTE5MzIxMDA2MDc1NDE2MDcxIiwiaWF0IjoxNjg2OTM3MzIzfQ.Q456uta_0TjtaDvbkvxxI7JM3eV2nn8mR5ygAPYSit4"
        }
        async with aiohttp.ClientSession(headers=headers) as client:
            async with client.get(url) as resp:
                chipTotal = await resp.text()
            await client.close()
        chipTotal = int(chipTotal.split('"cash":')[1].split(",")[0])

        embed = discord.Embed(title=interaction.user.display_name,color=0x5865f2)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="ミラ",value=f"<:mira:1120418935397961858> {format(await ecoCal(interaction.user.id),',')}",inline=True)
        embed.add_field(name="チップ",value=f"<:chip:1120258740189413377> {format(chipTotal,',')}")
        await interaction.followup.send(embed=embed,ephemeral=True)
    
    @app_commands.command(name="property_set",description="Set someone property")
    @app_commands.guild_only()
    @app_commands.choices(asset_class=[
        discord.app_commands.Choice(name="Mira",value="Mira"),
        discord.app_commands.Choice(name="Chip",value="Chip"),
    ])
    @app_commands.default_permissions()
    async def setProperty(self,interaction:discord.Interaction,user:discord.User,asset_class:discord.app_commands.Choice[str],value:int):
        if asset_class.value=="Mira":
            if not await ecoIsInit(user.id):
                await ecoInit(user.id)
            await ecoSet(user.id,int(value))
            await interaction.response.send_message(content=f"已设置{user.name} 的ミラ<:mira:1120418935397961858>为 {value}",ephemeral=True)
        elif asset_class.value=="Chip":
            url = f"https://unbelievaboat.com/api/v1/guilds/{interaction.guild_id}/users/{interaction.user.id}"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIxMTE5MzIxMDA2MDc1NDE2MDcxIiwiaWF0IjoxNjg2OTM3MzIzfQ.Q456uta_0TjtaDvbkvxxI7JM3eV2nn8mR5ygAPYSit4"
            }
            payload = {
                "cash": value,
                "reason":"Admin Set"
            }
            async with aiohttp.ClientSession(headers=headers) as client:
                async with client.put(url,data=json.dumps(payload)) as resp:
                    chipTotal = await resp.text()
                await client.close()
            await interaction.response.send_message(content=f"已设置{user.name} 的チップ<:chip:1120258740189413377>为 {value}",ephemeral=True)
        await addLog(interaction.user.id,f"User:{user.id} Set {asset_class.value}={value}")

    @app_commands.command(name="property_update",description="Update someone property")
    @app_commands.guild_only()
    @app_commands.choices(asset_class=[
        discord.app_commands.Choice(name="Mira",value="Mira"),
        discord.app_commands.Choice(name="Chip",value="Chip"),
    ])
    @app_commands.default_permissions()
    async def updateproperty(self,interaction:discord.Interaction,user:discord.User,asset_class:discord.app_commands.Choice[str],value:int):
        if asset_class.value=="Mira":
            if not await ecoIsInit(user.id):
                await ecoInit(user.id)
            await ecoUpdate(user.id,int(value))
            await interaction.response.send_message(content=f"已更新{user.name} 的ミラ<:mira:1120418935397961858> {value}",ephemeral=True)
        elif asset_class.value=="Chip":
            url = f"https://unbelievaboat.com/api/v1/guilds/{interaction.guild_id}/users/{interaction.user.id}"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIxMTE5MzIxMDA2MDc1NDE2MDcxIiwiaWF0IjoxNjg2OTM3MzIzfQ.Q456uta_0TjtaDvbkvxxI7JM3eV2nn8mR5ygAPYSit4"
            }
            payload = {
                "cash": value,
                "reason":"Admin Update"
            }
            async with aiohttp.ClientSession(headers=headers) as client:
                async with client.patch(url,data=json.dumps(payload)) as resp:
                    chipTotal = await resp.text()
                await client.close()
            await interaction.response.send_message(content=f"已更新{user.name} 的チップ<:chip:1120258740189413377> {value}",ephemeral=True)
        await addLog(interaction.user.id,f"User:{user.id} Update {asset_class.value}={value}")

    @app_commands.command(name="showproperty",description="Show someone property")
    @app_commands.guild_only()
    @app_commands.default_permissions()
    async def showproperty(self,interaction:discord.Interaction,user:discord.User):
        await interaction.response.defer(ephemeral=True)
        if not await ecoIsInit(user.id):
            await ecoInit(user.id)
        url = f"https://unbelievaboat.com/api/v1/guilds/{interaction.guild_id}/users/{user.id}"
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIxMTE5MzIxMDA2MDc1NDE2MDcxIiwiaWF0IjoxNjg2OTM3MzIzfQ.Q456uta_0TjtaDvbkvxxI7JM3eV2nn8mR5ygAPYSit4"
        }
        async with aiohttp.ClientSession(headers=headers) as client:
            async with client.get(url) as resp:
                chipTotal = await resp.text()
            await client.close()
        chipTotal = int(chipTotal.split('"cash":')[1].split(",")[0])

        embed = discord.Embed(title=user.display_name,color=0x5865f2)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ミラ",value=f"<:mira:1120418935397961858> {format(await ecoCal(user.id),',')}",inline=True)
        embed.add_field(name="チップ",value=f"<:chip:1120258740189413377> {format(chipTotal,',')}")
        await interaction.followup.send(embed=embed,ephemeral=True)


    @app_commands.command(name="exchange",description="Mira:Chip = 1:1")
    @app_commands.guild_only()
    @app_commands.choices(exchange_type=[
        discord.app_commands.Choice(name="MiraToChip",value="MiraToChip"),
        discord.app_commands.Choice(name="ChipToMira",value="ChipToMira"),
    ])
    async def exchange(self,interaction:discord.Interaction,exchange_type:discord.app_commands.Choice[str],value:int):
        url = f"https://unbelievaboat.com/api/v1/guilds/{interaction.guild_id}/users/{interaction.user.id}"
        errorEmbed = discord.Embed(title="Exchange ERROR",)
        errorEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1032688154429378650/1039103241121701958/kuma.jpg")
        errorEmbed.color=0xfa002a
        
        okEmbed = discord.Embed(title="Exchange OK",)
        okEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1032688154429378650/1039103241121701958/kuma.jpg")
        okEmbed.color=0x38ff99
        okEmbed.add_field(name=":white_check_mark: 交換成功しました", value=exchange_type.value, inline=False)

        if exchange_type.value=="MiraToChip":
            if (await ecoIsInit(interaction.user.id))==False:
                errorEmbed.add_field(name=":x: 交換失敗しました", value="ミラ 不足", inline=False)
                await interaction.response.send_message(embed=errorEmbed,ephemeral=True)
                await ecoInit(interaction.user.id)
                return
            if (await ecoCal(interaction.user.id))<value:
                errorEmbed.add_field(name=":x: 交換失敗しました", value="ミラ 不足", inline=False)
                await interaction.response.send_message(embed=errorEmbed,ephemeral=True)
                return
            await ecoUpdate(DiscordId=interaction.user.id,changeMira=-value)
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIxMTE5MzIxMDA2MDc1NDE2MDcxIiwiaWF0IjoxNjg2OTM3MzIzfQ.Q456uta_0TjtaDvbkvxxI7JM3eV2nn8mR5ygAPYSit4"
            }
            payload = {
                "cash": value,
                "reason":"Exchange MiraToChip"
            }
            async with aiohttp.ClientSession(headers=headers) as client:
                async with client.patch(url,data=json.dumps(payload)) as resp:
                    chipTotal = await resp.text()
                await client.close()
            chipTotal = chipTotal.split('"cash":')[1].split(",")[0]
            miraTotal = await ecoCal(interaction.user.id)
            okEmbed.add_field(name="Mira",value=f"<:mira:1120418935397961858>{miraTotal}",inline=True)
            okEmbed.add_field(name="Chip",value=f"<:chip:1120258740189413377>{chipTotal}",inline=True)
            await interaction.response.send_message(embed=okEmbed,ephemeral=True)
            return
        
        elif exchange_type.value=="ChipToMira":
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIxMTE5MzIxMDA2MDc1NDE2MDcxIiwiaWF0IjoxNjg2OTM3MzIzfQ.Q456uta_0TjtaDvbkvxxI7JM3eV2nn8mR5ygAPYSit4"
            }
            async with aiohttp.ClientSession(headers=headers) as client:
                async with client.get(url) as resp:
                    chipTotal = await resp.text()
                await client.close()
            chipTotal = int(chipTotal.split('"cash":')[1].split(",")[0])
            if chipTotal<value:
                errorEmbed.add_field(name=":x: 交換失敗しました", value="チップ 不足", inline=False)
                await interaction.response.send_message(embed=errorEmbed,ephemeral=True)
                return
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiIxMTE5MzIxMDA2MDc1NDE2MDcxIiwiaWF0IjoxNjg2OTM3MzIzfQ.Q456uta_0TjtaDvbkvxxI7JM3eV2nn8mR5ygAPYSit4"
            }
            payload = {
                "cash": -value,
                "reason":"Exchange ChipToMira"
            }
            async with aiohttp.ClientSession(headers=headers) as client:
                async with client.patch(url,data=json.dumps(payload)) as resp:
                    chipTotal = await resp.text()
                await client.close()
            chipTotal = chipTotal.split('"cash":')[1].split(",")[0]
            await ecoUpdate(DiscordId=interaction.user.id,changeMira=value)
            miraTotal = await ecoCal(interaction.user.id)            
            okEmbed.add_field(name="Mira",value=f"<:mira:1120418935397961858>{miraTotal}",inline=True)
            okEmbed.add_field(name="Chip",value=f"<:chip:1120258740189413377>{chipTotal}",inline=True)
            await interaction.response.send_message(embed=okEmbed,ephemeral=True)
            return


async def setup(bot):
    await bot.add_cog(ECO(bot))