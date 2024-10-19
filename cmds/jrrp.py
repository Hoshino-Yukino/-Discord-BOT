import discord
from discord import app_commands
from discord.ext import commands
from discord.interactions import Interaction
import time
import random
import traceback
from function.jrrp import *
from function.eco import *
from function.auditlog import *

class Jrrp(commands.Cog):
    def __init__(self,bot):
        self.bot:commands.Bot = bot
        self.jrrpsMenu = app_commands.ContextMenu(
            name="Draw JRRP",
            callback=self.drawJRRPS,
        )
        self.setJRRP = app_commands.ContextMenu(
            name="Set JRRP",
            callback=self.setJRRPMenu,
        )
        self.bot.tree.add_command(self.jrrpsMenu)
        self.bot.tree.add_command(self.setJRRP)

    @app_commands.command(name="jrrp",description="Draw your JRRP today")
    
    async def jrrp(self,interaction:discord.Interaction):
        author = interaction.user.mention
        author_id = interaction.user.id
        today = time.strftime("%Y-%m-%d", time.localtime())
        MiraFlag = False
        if not await jrrpIsInit(author_id):
            await jrrpInit(author_id)
        todayJrrp = await getTodayJrrp(author_id,today)
        if todayJrrp ==-1:
            MiraFlag = True
            todayJrrp = random.randint(1, 100)
            await jrrpUpdate(author_id,todayJrrp,today)

        embed=discord.Embed(title="JRRP", description=f"{author} 今日のRPは：{todayJrrp}",color=0x2ecc70)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        if not await ecoIsInit(author_id):
            await ecoInit(author_id)
        if MiraFlag==True:
            getMira = 0
            if todayJrrp<20 :
                getMira = random.randint(20,50)
            elif todayJrrp>=20 and todayJrrp<80 :
                getMira = random.randint(50,100)
            elif todayJrrp>=80:
                getMira = random.randint(100,200)
            await ecoUpdate(author_id,getMira)
            embed.set_footer(text=f" {getMira} ミラ をあげました")
        else:
            embed.set_footer(text=f"合わせ：{await ecoCal(author_id)} ミラ")
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @app_commands.default_permissions()
    async def drawJRRPS(self,interaction:discord.Interaction,user:discord.User):
        today = time.strftime("%Y-%m-%d", time.localtime())
        MiraFlag = False
        author = user.mention
        author_id = user.id
        if not await jrrpIsInit(author_id):
            await jrrpInit(author_id)
        todayJrrp = await getTodayJrrp(author_id,today)
        if todayJrrp ==-1:
            MiraFlag = True
            todayJrrp = random.randint(1, 100)
            await jrrpUpdate(author_id,todayJrrp,today)
        
        embed=discord.Embed(title="JRRP", description=f"{author} 今日のRPは：{todayJrrp}",color=0x2ecc70)
        embed.set_thumbnail(url=user.display_avatar.url)
        if not await ecoIsInit(author_id):
            await ecoInit(author_id)
        if MiraFlag==True:
            getMira = 0
            if todayJrrp<20 :
                getMira = random.randint(20,50)
            elif todayJrrp>=20 and todayJrrp<80 :
                getMira = random.randint(50,100)
            elif todayJrrp>=80:
                getMira = random.randint(100,200)
            await ecoUpdate(author_id,getMira)
            embed.set_footer(text=f" {getMira} ミラ をあげました")
        else:
            embed.set_footer(text=f"合わせ：{await ecoCal(author_id)} ミラ")
        await interaction.response.send_message(embed=embed)
        await addLog(interaction.user.id,f"User:{user.id} Roll JRRP")

    @app_commands.command(name="jrrps",description="Draw someone JRRP today「Admin Only」")
    @app_commands.guild_only()
    @app_commands.default_permissions()
    async def drawJRRP(self,interaction:discord.Interaction,user:discord.User):
        today = time.strftime("%Y-%m-%d", time.localtime())
        MiraFlag = False
        author = user.mention
        author_id = user.id
        if not await jrrpIsInit(author_id):
            await jrrpInit(author_id)
        todayJrrp = await getTodayJrrp(author_id,today)
        if todayJrrp ==-1:
            MiraFlag = True
            todayJrrp = random.randint(1, 100)
            await jrrpUpdate(author_id,todayJrrp,today)

        embed=discord.Embed(title="JRRP", description=f"{author} 今日のRPは：{todayJrrp}",color=0x2ecc70)
        embed.set_thumbnail(url=user.display_avatar.url)
        if not await ecoIsInit(author_id):
            await ecoInit(author_id)
        if MiraFlag==True:
            getMira = 0
            if todayJrrp<20 :
                getMira = random.randint(20,50)
            elif todayJrrp>=20 and todayJrrp<80 :
                getMira = random.randint(50,100)
            elif todayJrrp>=80:
                getMira = random.randint(100,200)
            await ecoUpdate(author_id,getMira)
            embed.set_footer(text=f" {getMira} ミラ をあげました")
        else:
            embed.set_footer(text=f"合わせ：{await ecoCal(author_id)} ミラ")
        await interaction.response.send_message(embed=embed)
        await addLog(interaction.user.id,f"User:{user.id} Roll JRRP")



    @app_commands.command(name="setjrrp",description="Set someone JRRP「Admin Only」")
    @app_commands.guild_only()
    @app_commands.default_permissions()
    async def setjrrp(self,interaction:discord.Interaction,user:discord.User,jrrp_value:str="NULL"):
        await interaction.response.defer()
        author = user.mention
        author_id = user.id
        if not await jrrpIsInit(author_id):
            await jrrpInit(author_id)
        if (jrrp_value=="NULL"):
            await jrrpUpdate(author_id,-1,'2000-01-01')
            await interaction.followup.send(f"已重置{author}的今日人品值",ephemeral=True)
            await addLog(interaction.user.id,f"User:{user.id} Reset JRRP")
            return
        today = time.strftime("%Y-%m-%d", time.localtime())
        await jrrpUpdate(author_id,int(jrrp_value),today)
        await interaction.followup.send(f"已设置{author}的今日人品值为{jrrp_value}",ephemeral=True)
        await addLog(interaction.user.id,f"User:{user.id} Set JRRP={jrrp_value}")

    @app_commands.guild_only()
    @app_commands.default_permissions()
    async def setJRRPMenu(self,interaction:discord.Interaction,user:discord.User):
        try:
            setJRRPModal = SetJRRPModal(title="Set JRRP",timeout=300)
            setJRRPModal.user = user
            await interaction.response.send_modal(setJRRPModal)
        except:
            traceback.print_exc()
        

class SetJRRPModal(discord.ui.Modal):
    user:discord.User
    jrrpValue = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="JRRP Value",
        required=False,
        placeholder="Reset JRRP if empty"
    )
    async def on_submit(self, interaction: discord.Interaction):
        try:
            author = self.user.mention
            author_id = self.user.id
            if not await jrrpIsInit(author_id):
                await jrrpInit(author_id)
            try:
                today = time.strftime("%Y-%m-%d", time.localtime())
                await jrrpUpdate(author_id,int(self.jrrpValue.value),today)
                await interaction.response.send_message(f"已设置{author}的今日人品值为{self.jrrpValue}",ephemeral=True)
                await addLog(interaction.user.id,f"User:{self.user.id} Set JRRP={self.jrrpValue}")
            except:
                await jrrpUpdate(author_id,-1,'2000-01-01')
                await interaction.response.send_message(f"已重置{author}的今日人品值",ephemeral=True)
                await addLog(interaction.user.id,f"User:{self.user.id} Reset JRRP")
        except:
            traceback.print_exc()
            

async def setup(bot):
    await bot.add_cog(Jrrp(bot))
