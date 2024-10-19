import asyncio
import random
import aiofiles
import discord
from discord import app_commands
from discord.ext import commands,tasks
from function.auditlog import addLog
from function.cmdChecks import ownerCheck
from function.eco import *
import json
import aiohttp
from function.eco import *
import traceback

with open('./setting.json','r',encoding='utf8') as setting_file:
    setting = json.load(setting_file)
class AiDraw(commands.Cog):

    def __init__(self,bot):
        self.bot:commands.Bot = bot
        self.aiDrawFlag = False
        self.checkKamiyaLimit.start()

    @tasks.loop(hours=1)
    async def checkKamiyaLimit(self):
        header={
            "Authorization": setting["KamiyaToken"]
        }
        async with aiohttp.ClientSession(headers=header) as client:
            async with client.get(f'https://p0.kamiya.dev/api/session/getDetails') as resp:
                r = await resp.json()
                await client.close()
        if r["data"]["credit"]<=50 and self.aiDrawFlag==True:
            self.aiDrawFlag=False
            await self.bot.get_user(910371227372245002).send(f'Kamiyaの制限は{r["data"]["credit"]}で、自動的にAiDrawをオフにしました。')
            await addLog(0,f"Set Kamiya_Enable=False by limit")
        elif r["data"]["credit"]>50 and self.aiDrawFlag==False:
            self.aiDrawFlag=True
            await self.bot.get_user(910371227372245002).send(f'Kamiyaの制限は{r["data"]["credit"]}で、自動的にAiDrawをオンにしました。')
            await addLog(0,f"Set Kamiya_Enable=True by limit")
    
    @app_commands.command(name="aidraw_enable",description="Owner ONLY")
    @app_commands.guild_only()
    @app_commands.default_permissions()
    @app_commands.check(ownerCheck)
    async def aiDrawEnableSet(self,interaction:discord.Interaction,value:bool):
        self.aiDrawFlag = value
        await interaction.response.send_message("完成しました。",ephemeral=True)

    @app_commands.command(name="aidraw",description="Use AI to draw a PIC. Limit:50/day")
    @app_commands.checks.cooldown(50,86400,key=lambda i:(i.user.id))
    @app_commands.guild_only()
    @app_commands.choices(
    sampler=[
        discord.app_commands.Choice(name="DPM++ 2M Karras「Default」",value="DPM++ 2M Karras"),
        discord.app_commands.Choice(name="DPM++ 2M",value="DPM++ 2M"),
        discord.app_commands.Choice(name="DPM++ 2S a Karras",value="DPM++ 2S a Karras"),
        discord.app_commands.Choice(name="Euler a",value="Euler a")
    ],
    model=[
        discord.app_commands.Choice(name="original「Default」",value="original"),
        discord.app_commands.Choice(name="anything-v3.0",value="anything_v3"),
        discord.app_commands.Choice(name="Anything-v4.5",value="Anything-v4.5-pruned-mergedVae"),
        discord.app_commands.Choice(name="AbyssOrangeMix2",value="abyss_orange_mix_2"),
        discord.app_commands.Choice(name="AbyssOrangeMix3 A2 (AOM3A2)",value="aom3a2"),
        discord.app_commands.Choice(name="BlueMoonMix 蓝月",value="bluemoonmix_v1"),
        discord.app_commands.Choice(name="WhiteDistanceMixV4",value="whitedistancemixv4"),
        discord.app_commands.Choice(name="DisillusionMix 幻灭",value="disillusionmix_3"),
        discord.app_commands.Choice(name="MIXProV3.5",value="mixprov35"),
        discord.app_commands.Choice(name="MIXProV3",value="mixprov3"),
        discord.app_commands.Choice(name="NyanMix",value="nyanmix"),
        discord.app_commands.Choice(name="Night Sky YOZORA",value="yozora"),
        discord.app_commands.Choice(name="RefSlaveV2",value="refslavev2"),
        discord.app_commands.Choice(name="BasilMix",value="basil_mix"),
        discord.app_commands.Choice(name="SukiyakiMixV1",value="sukiyaki_mix_v1"),
        discord.app_commands.Choice(name="PVCGK",value="pvcgk"),
        discord.app_commands.Choice(name="Cheese Daddy's Landscapes mix",value="cdlandscapesmix"),
        discord.app_commands.Choice(name="pastelMixStylizedAnime",value="pastelMixStylizedAnime")
    ])
    @app_commands.describe(prompt="Default: masterpiece, best quality, 1girl,",
                           negative_prompt="Default:lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,",
                           sampling_steps="1-50 注意：超过35导致4倍MIRA开销 Default:28",
                           cfg_scale="1-30, Default:7.0",
                           width="宽度 注意：宽度x高度>640000将导致8倍MIRA开销 Default:518",
                           height="高度 注意：宽度x高度>640000将导致8倍MIRA开销 Default:518",
                           seed="Default：random")
    async def aidraw(self,interaction:discord.Interaction,
                    model:discord.app_commands.Choice[str]="original",
                    prompt:str="masterpiece, best quality, 1girl",
                    negative_prompt:str="lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry",
                    sampling_steps:int=28,cfg_scale:float=7.0,
                    sampler:discord.app_commands.Choice[str]="DPM++ 2M Karras",
                    width:int=512, height:int=512, seed:int=-1):
        embed=discord.Embed(title="「AI DRAW」", color=0x68ffb5)

        costmira=-5

        if self.aiDrawFlag==False:
            embed.add_field(name=":x: ＡＩ作図失敗しました", value="システムオフ")
            embed.color=0xfa002a
            await interaction.response.send_message(embed=embed)
            return

        if seed== -1:
            seed = random.randint(1000000000,9999999999)
        
        if sampling_steps<1 or sampling_steps>50 or width<1 or height<1 or cfg_scale<1 or cfg_scale>150:
            embed.add_field(name=":x: ＡＩ作図失敗しました", value="参数错误")
            embed.color=0xfa002a
            await interaction.response.send_message(embed=embed,ephemeral=True,delete_after=30)
            return

        if width*height>640000:
            costmira=costmira*8
        if sampling_steps>35:
            costmira = costmira*4
        
        if not await ecoIsInit(interaction.user.id):
            embed.add_field(name=":x: ＡＩ作図失敗しました", value="ミラ 不足")
            embed.color=0xfa002a
            await interaction.response.send_message(embed=embed,ephemeral=True,delete_after=30)
            return
        
        if await ecoCal(interaction.user.id)+costmira<0:
            embed.add_field(name=":x: ＡＩ作図失敗失敗しました", value="ミラ 不足")
            embed.color=0xfa002a
            await interaction.response.send_message(embed=embed,ephemeral=True,delete_after=30)
            return

        await interaction.response.defer()
        
        try:
            sampler = sampler.value
        except:
            pass
        try:
            model = model.value
        except:
            pass

        header={
            "Authorization": "Bearer sk-1jwfxiuzNwlhOdsBs6vAY0kDai3Cr3JED6q3mP6hTi3ieVwO"
        }
        payload = {
            "type": "text2image",
            "prompts": prompt,
            "negativePrompts":negative_prompt,
            "step": sampling_steps,
            "width": width,
            "height": height,
            "cfg": cfg_scale,
            "model": model,
            "sampling":sampler,
            "seed":seed
        }
        try:
            async with aiohttp.ClientSession(headers=header) as client:
                async with client.post(f'https://p0.kamiya.dev/api/image/generate',json=payload) as resp:
                    r = await resp.json()
                    await client.close()
                    
            if r['status']!=200:
                raise ValueError
            
            picMetaId = r["data"]["metaid"]
            picHashId = r["data"]["hashid"]
            picName = f"{picMetaId}.png"
            picDirectURL = "./pic/" + picName

            while True:
                try:
                    async with aiohttp.ClientSession(headers=header) as client:
                        async with client.get(f'https://p0.kamiya.dev/api/image/generate/{picHashId}',json=payload) as resp:
                            r = await resp.json()
                            await client.close()
                    if r["data"]["status"]=="generated":
                        picURL = r["data"]["metadata"]["jpg"]
                        break
                except:
                    await asyncio.sleep(5)
                    continue

            async with aiohttp.ClientSession() as session:
                async with session.get(picURL) as resp:
                    async with aiofiles.open(f"{picDirectURL}", "wb") as f:
                        await f.write(await resp.content.read())
                        await f.close()
                await session.close()

            pic = discord.File(picDirectURL)
            seed = seed
            size = f"{width}x{height}"
            embed.add_field(name="Model",value=model)
            embed.add_field(name="Prompt",value=prompt)
            embed.add_field(name="Negative Prompt",value=negative_prompt)
            embed.add_field(name="Seed",value=seed)
            embed.add_field(name="Size",value=size)
            embed.add_field(name="Sampler",value=sampler)
            embed.add_field(name="Sampling_steps",value=sampling_steps)
            embed.add_field(name="CFG scale",value=cfg_scale)
            embed.set_footer(text=f"Cost Mira: {costmira-(2*costmira)}")
            
            await ecoUpdate(DiscordId=interaction.user.id,changeMira=costmira)
            await interaction.followup.send(embed=embed,ephemeral=False,file=pic)
        except ValueError:
            embed.add_field(name=":x: ＡＩ作図失敗しました", value="敏感な単語があります出力/無効なパラメータ/ 1回の要求制限を超えます")
            embed.color=0xfa002a
            await interaction.followup.send(embed=embed)
            return
        except Exception as reason:
            traceback.print_exc()
            embed.add_field(name=":x: ＡＩ作図失敗しました", value="システムエラー")
            embed.color=0xfa002a
            await interaction.followup.send(embed=embed)
            return


async def setup(bot):
    await bot.add_cog(AiDraw(bot))