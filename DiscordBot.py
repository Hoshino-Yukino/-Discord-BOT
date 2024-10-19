# -*- coding: UTF-8 -*-
import traceback
import discord
from discord.ext import commands
from discord import app_commands
import random
import time
import os
import json
import asyncio
import datetime
from function.countingGame import *
from function.eco import *
from function.auditlog import addLog
from core.localizationTrans import LocaleTranslator

with open('./setting.json','r',encoding='utf8') as setting_file:
    setting = json.load(setting_file)


bot = commands.Bot(command_prefix='.',intents=discord.Intents.all())

bot.remove_command("help")

@bot.event
async def on_ready():
    try:
        await bot.tree.set_translator(LocaleTranslator())
        await bot.tree.sync()
        await addLog(DiscordId=0,Operation="Bot Online")
        print(">> Bot is Online <<")
    except:
        traceback.print_exc()

@bot.event
async def on_message(ctx:discord.Message):
    if ctx.author.bot==False:
        if ctx.channel.id == 1064816598747197450: #Counting Game
            nowNumber = await getLastNumber() + 1
            nowDay = time.strftime("%Y-%m-%d", time.localtime())
            print(await checkCountingLog(ctx.author.id,nowDay))
            if ctx.content==str(nowNumber)and await checkCountingLog(ctx.author.id,nowDay):
                emoji = bot.get_emoji(1040497001097347092)
                await ctx.add_reaction(emoji)
                await ctx.channel.edit(topic=f"The next number to be written is {nowNumber+1}.")
                await insertCounting(ctx.author.id,nowNumber,nowDay)
            else:
                await ctx.delete()
                return
            getMira = 0
            if nowNumber>=1000 and nowNumber % 1000==0:
                getMira = random.randint(80,800)
            elif nowNumber>=100 and nowNumber % 100==0:
                getMira = random.randint(40,400)
            elif random.randint(1,100)>=90:
                getMira = random.randint(20,200)
            if getMira>0:
                if not await ecoIsInit(ctx.author.id):
                    await ecoInit(ctx.author.id)
                ecoUpdate(ctx.author.id,getMira)
                embed=discord.Embed(title="WE HAVE A LUCKY PERSON!", description=f"<@{ctx.author.id}> You received a reward form saying the number **{nowNumber}**! **{getMira}ミラ** has been added to your account.", color=0x2ecc70)
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await ctx.reply(embed=embed)

    await bot.process_commands(ctx) 
    return
    
@bot.tree.error
async def on_app_command_error(interaction:discord.Interaction,error):
    if isinstance(error,app_commands.MissingRole):
        await interaction.response.send_message("You have no permission to do that!",ephemeral=True)
    elif isinstance(error,app_commands.CommandOnCooldown):
        afterLast = datetime.datetime.now()+datetime.timedelta(seconds=error.retry_after)
        await interaction.response.send_message(f'**Still on cooldown**,please try again in {discord.utils.format_dt(afterLast,"R")}',ephemeral=True)
    elif isinstance(error,app_commands.CheckFailure):
        await interaction.response.send_message("You have no permission to do that!",ephemeral=True)
    else:
        raise error

async def load():
    for filename in os.listdir('./cmds'):
        if filename.endswith('.py'):
            await bot.load_extension(f"cmds.{filename[:-3]}")


async def main():
    await load()
    await bot.start(setting['TestTOKEN'])
    # await bot.start(setting['TOKEN'])
asyncio.run(main())