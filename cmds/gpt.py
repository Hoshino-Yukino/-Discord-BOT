import json
import discord
from discord.ext import commands,tasks
from discord import app_commands
from function.cmdChecks import *
import asyncio
import openai
from function.gptDB import *
from function.auditlog import *
import aiohttp
import traceback
import re

with open('./setting.json','r',encoding='utf8') as setting_file:
    setting = json.load(setting_file)

class GPTcmd(commands.Cog):
    def __init__(self,bot):
        self.bot:commands.Bot = bot
        self.gpt4Enable = True
        self.gpt3Enable = True
        self.transMenu = app_commands.ContextMenu(
            name="翻訳",
            callback=self.translation,
        )
        self.bot.tree.add_command(self.transMenu)
        self.checkGPT4Limit.start()
        self.nowService = "KamiyaGPT"
        self.nowServiceToken = setting["Kamiya_APIToken"]
        self.nowServiceEndPoint=setting["Kamiya_EndPoint"]
        self.nowServiceGPt4="KamiyaGPT"
        self.nowServiceGPT4Token=setting["Kamiya_APIToken"]
        self.nowServiceGPT4EndPoint=setting["Kamiya_EndPoint"]

    @app_commands.guild_only()
    @app_commands.checks.dynamic_cooldown(transCooldownExceptOwner)
    async def translation(self,interaction:discord.Interaction,discordMessage:discord.Message):
        try:
            await updateUserState(interaction.user.id)
            if len(discordMessage.content)<=0:
                await interaction.followup.send(content="このメッセージには文字が含まれておらず、埋め込みコンテンツの文字は認められません。")
                return
            messages=list()
            translateInfo = await getTransInfo(interaction.user.id)
            if translateInfo[1]=="gpt-4-0613" and await checkGPT4Enable()==0 and interaction.user.id !=910371227372245002:
                await interaction.response.send_message("GPT4は過剰使用のため管理者によりブロックされています。",ephemeral=True)
                return
            
            if (translateInfo[1]=="gpt-4-0613" and self.gpt4Enable==False) or (translateInfo[1]=="gpt-3.5-turbo-16k-0613" and self.gpt3Enable==False):
                await interaction.response.send_message("この機能またはモデルは管理者によって停止されています。",ephemeral=True)
                return
            await interaction.response.defer(thinking=True,ephemeral=True)
            if translateInfo[1]=="gpt-4-0613":
                openai.api_key=self.nowServiceGPT4Token
                openai.api_base=self.nowServiceGPT4EndPoint
            else:
                openai.api_key=self.nowServiceToken
                openai.api_base=self.nowServiceEndPoint

            systemContent = f"In future conversations, please always act as mytranslation assistant. Whatever content the user send to you, please translate it into {translateInfo[0]} respectively and output it. I don't need to emhpasize it again"
            messages.append({"role": "system", "content": systemContent})
            messages.append({"role": "user", "content": discordMessage.content})

            loop = asyncio.get_event_loop()
            def openAIConnect():
                return openai.ChatCompletion.create(
                model=translateInfo[1],
                messages=messages,
                max_tokens=2000,
                )
            completion = await loop.run_in_executor(None,openAIConnect)
            await updateUserState(interaction.user.id,generatingTimes=1)
            embed = discord.Embed(title="<:ChatGPT:1122836104874311734> ChatGPT Translation",description=discordMessage.content,color=0xd2f123)
            embed.add_field(name=f"「 {translateInfo[0]} 」",value=completion.choices[0].message.content)
            embed.set_footer(text=f"Model: {translateInfo[1]}")
            await interaction.followup.send(embed=embed)
        except:
            await interaction.followup.send(content="FATAL ERROR\nAPIがエラーしています,後で再試行してください",ephemeral=True)

    class GPTGroup(app_commands.Group):
        ...
    gpt = GPTGroup(name="gpt",description="Group for ChatGPT.")

    @gpt.command(description="新会話を始まる | Limit:30/day")
    @app_commands.checks.dynamic_cooldown(topicCooldownExceptOwner)
    @app_commands.describe(content="Your Message")
    @app_commands.choices(model=[
        discord.app_commands.Choice(name="GPT-3.5-turbo-16k-0613",value="gpt-3.5-turbo-16k-0613"),
        discord.app_commands.Choice(name="GPT-4-8k-0613",value="gpt-4-0613"),
    ])
    async def new(self,interaction:discord.Interaction,model:discord.app_commands.Choice[str],content:str):
        await updateUserState(interaction.user.id)
        if await getUserFlag(interaction.user.id)==1:
            await interaction.response.send_message("前のGPT Responseが生成された後に使用する必要があります。\nこれがバグだと思われる場合は、Modmail 経由でモデレータに連絡してください。",ephemeral=True)
            return
        try:
            if model.name=="GPT-3.5-turbo-16k-0613":
                if self.gpt3Enable==False:
                    await interaction.response.send_message("この機能またはモデルは管理者によって停止されています。",ephemeral=True)
                    return
                openai.api_key=self.nowServiceToken
                openai.api_base=self.nowServiceEndPoint
                await interaction.response.defer(thinking=True)
                await initTable(interaction.user.id,isGPT4=0)
                await addMessage(discordId=interaction.user.id,role="user",message=content)
                allMsg = await getUserAllMsg(interaction.user.id)
                messages=list()
                for msg in allMsg:
                    messages.append({'role':msg[1],'content':msg[2]})

                await updateUserState(interaction.user.id,generatingNow=1)
                loop = asyncio.get_event_loop()
                def openAIConnect():
                    return openai.ChatCompletion.create(
                    model=model.value,
                    messages=messages,
                    max_tokens=1500,
                    )
                completion = await loop.run_in_executor(None,openAIConnect)
                await addMessage(discordId=interaction.user.id,role=completion.choices[0].message.role,
                                message=completion.choices[0].message.content)
                await updateUserState(interaction.user.id,generatingNow=0,newTimes=1,generatingTimes=1)
                embed = discord.Embed(title="<:ChatGPT:1122836104874311734> ChatGPT Response",description=completion.choices[0].message.content,color=0xd2f123)
                embed.set_footer(text=f"Model: {model.value} | リクエストを送信: {await checkMsgQuantity(interaction.user.id)}/30")
                await interaction.followup.send(embed=embed)
            elif model.name=="GPT-4-8k-0613":
                if await haveGPT4(interaction.user.id)==0:
                    await interaction.response.send_message("GPT-4を使用する権限はありません。\nご要望や誤りがあれば、Modmail 経由でモデレータに連絡してください。",ephemeral=True)
                    return
                if await checkGPT4Enable()==0 and interaction.user.id != 910371227372245002:
                    await interaction.response.send_message("GPT4は過剰使用のため管理者によりブロックされています。",ephemeral=True)
                    return
                if self.gpt4Enable==False:
                    await interaction.response.send_message("この機能またはモデルは管理者によって停止されています。",ephemeral=True)
                    return
                
                openai.api_key=self.nowServiceGPT4Token
                openai.api_base=self.nowServiceGPT4EndPoint

                await interaction.response.defer(thinking=True)
                await initTable(interaction.user.id,isGPT4=1)
                await addMessage(discordId=interaction.user.id,role="user",message=content)
                allMsg = await getUserAllMsg(interaction.user.id)
                messages=list()
                for msg in allMsg:
                    messages.append({'role':msg[1],'content':msg[2]})

                await updateUserState(interaction.user.id,generatingNow=1)
                loop = asyncio.get_event_loop()
                def openAIConnect():
                    return openai.ChatCompletion.create(
                    model=model.value,
                    messages=messages,
                    max_tokens=1500,
                    )
                completion = await loop.run_in_executor(None,openAIConnect)
                await addMessage(discordId=interaction.user.id,role=completion.choices[0].message.role,
                                message=completion.choices[0].message.content)
                await updateUserState(interaction.user.id,generatingNow=0,newTimes=1,generatingTimes=1)
                embed = discord.Embed(title="<:ChatGPT:1122836104874311734> ChatGPT Response",description=completion.choices[0].message.content,color=0xd2f123)
                embed.set_footer(text=f"Model: {model.value} | リクエストを送信: {await checkMsgQuantity(interaction.user.id)}/15")
                await interaction.followup.send(embed=embed)
        except:
            await interaction.followup.send(content="FATAL ERROR\nAPIがエラーしています,後で再試行してください",ephemeral=True)
            await updateUserState(interaction.user.id,generatingNow=0)
            await dropTable(interaction.user.id)
            traceback.print_exc()



    @gpt.command(description="前回の会話を続ける | 1 セッション内のリクエストの最大数:30")
    @app_commands.describe(content="Your Message")
    async def chat(self,interaction:discord.Interaction,content:str):
        try:
            if await checkTableExist(interaction.user.id) ==False:
                await interaction.response.send_message("You must use `/gpt new` first!",ephemeral=True)
                return
            await updateUserState(interaction.user.id)
            if await getUserFlag(interaction.user.id)==1:
                await interaction.response.send_message("前のGPT Responseが生成された後に使用する必要があります。\nこれがバグだと思われる場合は、Modmail 経由でモデレータに連絡してください。",ephemeral=True)
                return
            
            allMsg = await getUserAllMsg(interaction.user.id)
            if int(allMsg[0][3])==0:
                model = "gpt-3.5-turbo-16k-0613"
                openai.api_key=self.nowServiceToken
                openai.api_base=self.nowServiceEndPoint

            else:
                model = "gpt-4-0613"
                openai.api_key=self.nowServiceGPT4Token
                openai.api_base=self.nowServiceGPT4EndPoint

            if model=="gpt-4-0613" and await checkGPT4Enable()==0 and interaction.user.id !=910371227372245002:
                await interaction.response.send_message("GPT4は過剰使用のため管理者によりブロックされています。",ephemeral=True)
                return
            if (model=="gpt-3.5-turbo-16k-0613" and self.gpt3Enable==False) or (model=="gpt-4-0613" and self.gpt4Enable==False):
                await interaction.response.send_message("この機能またはモデルは管理者によって停止されています。",ephemeral=True)
                return
            await interaction.response.defer(thinking=True)
            messages=list()
            for msg in allMsg:
                messages.append({'role':msg[1],'content':msg[2]})
            messages.append({'role':'user','content':content})
            await updateUserState(interaction.user.id,generatingNow=1)
            loop = asyncio.get_event_loop()
            def openAIConnect():
                return openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=1500,
                )
            completion = await loop.run_in_executor(None,openAIConnect)
            await addMessage(discordId=interaction.user.id,role="user",message=content)
            await addMessage(discordId=interaction.user.id,role=completion.choices[0].message.role,
                            message=completion.choices[0].message.content)
            await updateUserState(interaction.user.id,generatingNow=0,generatingTimes=1)
            embed = discord.Embed(title="<:ChatGPT:1122836104874311734> ChatGPT Response",description=completion.choices[0].message.content,color=0xd2f123)
            
            if model=="gpt-3.5-turbo-16k-0613":
                embed.set_footer(text=f"Model: {model} | リクエストを送信: {await checkMsgQuantity(interaction.user.id)}/30")
            elif model=="gpt-4-0613":
                embed.set_footer(text=f"Model: {model} | リクエストを送信: {await checkMsgQuantity(interaction.user.id)}/15")
            await interaction.followup.send(embed=embed)
            if await checkMsgQuantity(interaction.user.id)>=30 and model=="gpt-3.5-turbo-16k-0613":
                await dropTable(interaction.user.id)
                await interaction.followup.send("セッションのリクエスト数が上限に達しました。\n`/gpt new` を使用してセッションを再開してください。",ephemeral=True)
            elif await checkMsgQuantity(interaction.user.id)>=15 and model=="gpt-4-0613":
                await dropTable(interaction.user.id)
                await interaction.followup.send("セッションのリクエスト数が上限に達しました。\n`/gpt new` を使用してセッションを再開してください。",ephemeral=True)
        except:
            await interaction.followup.send(content="FATAL ERROR\nAPIがエラーしています,後で再試行してください",ephemeral=True)
            await updateUserState(interaction.user.id,generatingNow=0)
            traceback.print_exc()

    @gpt.command(name="translation_config",description="翻訳したい言語、モデルを設定します。設定した言語がGPT言語ライブラリにない場合、翻訳機能に未知の結果が生じる可能性があります。")
    @app_commands.describe(language="The language you want to translate into「In English」",model="The model you want to use in tranlation, if you have permission.")
    @app_commands.choices(model=[
        discord.app_commands.Choice(name="GPT-3.5-turbo-16k-0613",value="gpt-3.5-turbo-16k-0613"),
        discord.app_commands.Choice(name="GPT-4-8k-0613",value="gpt-4-0613"),
    ])

    async def transSet(self,interaction:discord.Interaction,model:discord.app_commands.Choice[str],language:str=None):
        if language!=None:
            pattern = re.compile('^[A-Za-z]+$')
            if pattern.match(language)==None:
                await interaction.response.send_message(content="The `language` value must in English!",ephemeral=True)
                return
            await updateUserState(interaction.user.id,language=language)
        if model.value=="gpt-4-0613" and await haveGPT4(interaction.user.id)==0:
            await interaction.response.send_message(content="GPT-4を使用する権限はありません。",ephemeral=True)
            return
        await updateUserState(interaction.user.id,transModel=model.value)
        if language !=None:
            await interaction.response.send_message(content=f"翻訳言語は{language}、モデルは{model.name}を設定成功しました。",ephemeral=True)
        else:
            await interaction.response.send_message(content=f"翻訳モデルは{model.name}を設定成功しました。",ephemeral=True)


    @app_commands.guild_only()
    @app_commands.default_permissions()
    class GPTConfigGroup(app_commands.Group):
        ...
    gptConfigGroup = GPTConfigGroup(name="gpt_config",description="Group for admin ChatGPT.")

    @gptConfigGroup.command(name="bug_fix",description="生成中のFLAGの占有を解除する 「Admin ONLY」")
    @app_commands.describe(user="The user you want to fix BUG")
    async def bug_fix(self,interaction:discord.Interaction,user:discord.User):
        await adminBugFix(user.id)
        await interaction.response.send_message("完成しました。")
        await addLog(interaction.user.id,f"User:{user.id} Set GENERATION_FLAG=False")
    
    @gptConfigGroup.command(name="gpt4_permission",description="GPT4権限を設定する 「Owner ONLY」")
    @app_commands.check(ownerCheck)
    async def setGPT4(self,interaction:discord.Interaction,user:discord.User,value:bool):
        if value == True:
            intValue=1
        else:
            intValue=0
        await updateUserState(discordId=user.id,gpt4Permission=intValue,transModel="gpt-3.5-turbo-16k-0613")
        await interaction.response.send_message("完成しました。")
        await addLog(interaction.user.id,f"User:{user.id} Set GPT4_Permission={value}")

    @gptConfigGroup.command(name="enable",description="GPT Enable/Disable 「Owner ONLY」")
    @app_commands.check(ownerCheck)
    @app_commands.choices(key=[
        discord.app_commands.Choice(name="GPT-3.5-turbo-16k-0613",value="gpt-3.5"),
        discord.app_commands.Choice(name="GPT-4-8k-0613",value="gpt-4"),
        discord.app_commands.Choice(name="GPT-System",value="system"),
    ])
    async def setEnable(self,interaction:discord.Interaction, key:discord.app_commands.Choice[str], value:bool):
        if key.value == "gpt-3.5":
            self.gpt3Enable = value
        elif key.value=="gpt-4":
            self.gpt4Enable = value
        elif key.value=="system":
            self.gpt3Enable = value
            self.gpt4Enable = value
        await interaction.response.send_message("完成しました。")
        await addLog(interaction.user.id,f"Set {key.name}={value}")

    @gptConfigGroup.command(name="service",description="Set GPT Service 「Owner ONLY」")
    @app_commands.check(ownerCheck)
    @app_commands.choices(service=[
        discord.app_commands.Choice(name="KamiyaGPT",value="KamiyaGPT"),
        discord.app_commands.Choice(name="OhmyGPT",value="OhmyGPT"),
    ],
        model=[
        discord.app_commands.Choice(name="GPT3",value="GPT3"),
        discord.app_commands.Choice(name="GPT4",value="GPT4"),      
    ])
    async def setService(self,interaction:discord.Interaction,model:discord.app_commands.Choice[str], service:discord.app_commands.Choice[str]):
        if model.value=="GPT3":
            if service.value == "CattoGPT":
                self.nowServiceToken=setting["Catto_APIKEY"]
                self.nowServiceEndPoint=setting["Catto_EndPoint"]
                self.nowService="CattoGPT"
            elif service.value=="KamiyaGPT":
                self.nowServiceToken=setting["Kamiya_APIToken"]
                self.nowServiceEndPoint=setting["Kamiya_EndPoint"]
                self.nowService="KamiyaGPT"
            elif service.value=="OhmyGPT":
                self.nowServiceToken=setting["OhmyGPT_APIToken"]
                self.nowServiceEndPoint=setting["OhmyGPT_EndPoint"]
                self.nowService="OhmyGPT"
        elif model.value=="GPT4":
            if service.value == "CattoGPT":
                self.nowServiceGPT4Token=setting["Catto_APIKEY"]
                self.nowServiceGPT4EndPoint=setting["Catto_EndPoint"]
                self.nowServiceGPt4="CattoGPT"
            elif service.value=="KamiyaGPT":
                self.nowServiceGPT4Token=setting["Kamiya_APIToken"]
                self.nowServiceGPT4EndPoint=setting["Kamiya_EndPoint"]
                self.nowServiceGPt4="KamiyaGPT"
            elif service.value=="OhmyGPT":
                self.nowServiceGPT4Token=setting["OhmyGPT_APIToken"]
                self.nowServiceGPT4EndPoint=setting["OhmyGPT_EndPoint"]
                self.nowServiceGPt4="OhmyGPT"
        await interaction.response.send_message("完成しました。")
        await addLog(interaction.user.id,f"Set GPT_Service={service.name}")

    @gptConfigGroup.command(name="info",description="GPT Info 「Owner ONLY」")
    @app_commands.check(ownerCheck)
    async def setService(self,interaction:discord.Interaction):
        await interaction.response.defer(thinking=True,ephemeral=True)
        embed = discord.Embed(title="GPT Service",color=0x4ec9b0)
        try:
            header={
                "Authorization": f'Bearer {setting["Catto_APIKEY"]}'
            }
            async with aiohttp.ClientSession(headers=header) as client:
                async with client.get("https://v2.catto.codes/info") as resp:
                    cattoData = await resp.json()
                await client.close()
            embed.add_field(name="CattoGPT",value=f'GPT3: {cattoData["Normal_Model"]} | GPT4: {"GPT_4"}')
            header={
                "Authorization": f'Bearer {setting["Kamiya_APIToken"]}'
            }
            async with aiohttp.ClientSession(headers=header) as client:
                async with client.get("https://p0.kamiya.dev/api/session/getDetails") as resp:
                    kamiyaData = await resp.json()
                await client.close()
            embed.add_field(name="Kamiya",value=f'Credit: {kamiyaData["data"]["credit"]}')
            await interaction.followup.send(embed=embed,ephemeral=True)
        except:
            traceback.print_exc()
            embed.color=0xfa002a
            embed.description="エラー"
            await interaction.followup.send(embed=embed,ephemeral=True)

    @tasks.loop(minutes=30)
    async def checkGPT4Limit(self):
        if self.nowServiceGPt4=="CattoGPT":
            header={
                "Authorization": f'Bearer {setting["Catto_APIKEY"]}'
            }
            async with aiohttp.ClientSession(headers=header) as client:
                async with client.get("https://v2.catto.codes/info") as resp:
                    limitData = await resp.json()
                await client.close()
            if limitData["GPT_4"]<=150 and await checkGPT4Enable()==1:
                await updateUserState(discordId=0,gpt4Permission=0)
                await self.bot.get_user(910371227372245002).send(f"Catto_GPT4の1日の制限は{limitData['GPT_4']}で、自動的にGPT4をオフにしました。")
                await addLog(0,f"Set GPT4_Enable=False by daily limit")
            elif limitData["GPT_4"]>150 and await checkGPT4Enable()==0:
                await updateUserState(discordId=0,gpt4Permission=1)
                await self.bot.get_user(910371227372245002).send(f"Catto_GPT4の1日の制限は{limitData['GPT_4']}で、自動的にGPT4をオンにしました。")
                await addLog(0,f"Set GPT4_Enable=True by daily limit")
        if self.nowService=="KamiyaGPT":
            header={
                "Authorization": f'Bearer {setting["Kamiya_APIToken"]}'
            }
            async with aiohttp.ClientSession(headers=header) as client:
                async with client.get("https://p0.kamiya.dev/api/session/getDetails") as resp:
                    data = await resp.json()
                await client.close()
            if (self.gpt3Enable==False) and data["data"]["credit"]>=100:
                self.gpt3Enable=True
                await self.bot.get_user(910371227372245002).send(f'Kamiyaの制限は{data["data"]["credit"]}で、自動的にGPT3をオンにしました。')
            elif (self.gpt3Enable==True) and data["data"]["credit"]<100:
                self.gpt3Enable=False
                await self.bot.get_user(910371227372245002).send(f'Kamiyaの制限は{data["data"]["credit"]}で、自動的にGPT3をオフにしました。')
        if self.nowServiceGPt4=="KamiyaGPT":
            header={
                "Authorization": f'Bearer {setting["Kamiya_APIToken"]}'
            }
            async with aiohttp.ClientSession(headers=header) as client:
                async with client.get("https://p0.kamiya.dev/api/session/getDetails") as resp:
                    data = await resp.json()
                await client.close()
            if (self.gpt4Enable==False) and data["data"]["credit"]>=100:
                self.gpt4Enable=True
                await self.bot.get_user(910371227372245002).send(f'Kamiyaの制限は{data["data"]["credit"]}で、自動的にGPT4をオンにしました。')
            elif (self.gpt4Enable==True) and data["data"]["credit"]<100:
                self.gpt4Enable=False
                await self.bot.get_user(910371227372245002).send(f'Kamiyaの制限は{data["data"]["credit"]}で、自動的にGPT4をオフにしました。')

        elif self.nowService=="OhmyGPT":
            pass
async def setup(bot):
    await bot.add_cog(GPTcmd(bot))