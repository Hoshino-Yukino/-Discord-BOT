import asyncio
import aiofiles
import aiohttp
import discord
from discord.ext import commands,tasks
import traceback
import datetime
from PIL import Image
from function.splatoonPic import *


class Splatoon3(commands.Cog):

    def __init__(self,bot):
        self.bot:commands.Bot = bot
        self.postStageSchedules.start()

    ### SPLATOON3 STAGE SCHEDULE ###
    times = [
        datetime.time(hour=0),datetime.time(hour=2),datetime.time(hour=4),
        datetime.time(hour=6),datetime.time(hour=8),datetime.time(hour=10),
        datetime.time(hour=12),datetime.time(hour=14),datetime.time(hour=16),
        datetime.time(hour=18),datetime.time(hour=20),datetime.time(hour=22)
    ]   

    # @tasks.loop(minutes=1)
    @tasks.loop(time=times)
    async def postStageSchedules(self):
        try:
            await self.bot.get_channel(1096242499795816448).last_message.delete()
        except:
            pass
        while True:
            try:
                async with aiohttp.ClientSession() as client:
                    async with client.get("https://splatoon3.ink/data/schedules.json") as resp:
                        schedulesData = await resp.json()
                    await client.close()
                # while True:
                #     async with aiohttp.ClientSession() as client:
                #         async with client.get("https://splatoon3.ink/data/schedules.json") as resp:
                #             schedulesData = await resp.json()
                #         await client.close()
                #     pvpEndTime = datetime.datetime.strptime(schedulesData["data"]["regularSchedules"]["nodes"][0]["endTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                #     if (pvpEndTime-datetime.datetime.now()).total_seconds()<0:
                #         print(1)
                #         break
                #     await asyncio.sleep(10)
                #     print(2)

                async with aiohttp.ClientSession() as client:
                    async with client.get("https://splatoon3.ink/data/locale/ja-JP.json") as resp:
                        jpData = await resp.json()
                    await client.close()

                allEmbed = list()
                allFile = list()

                if schedulesData["data"]["festSchedules"]["nodes"][0]["festMatchSetting"]!=None:
                    #Fes Battle
                    pvpNode = 0
                    while True:
                        pvpStartTime = datetime.datetime.strptime(schedulesData["data"]["festSchedules"]["nodes"][pvpNode]["startTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                        pvpEndTime = datetime.datetime.strptime(schedulesData["data"]["festSchedules"]["nodes"][pvpNode]["endTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                        if (datetime.datetime.now()-pvpStartTime).total_seconds()>=0 and (pvpEndTime-datetime.datetime.now()).total_seconds()>=0:
                            break
                        pvpNode = pvpNode + 1
                    fesBattleEmbed=discord.Embed(title=f"<:fesBattle:1104726692515299359>フェスマッチ", color=0x19d719,description=f"{pvpStartTime} ~ {pvpEndTime}")
                    fesBattleStageName=""
                    for i in [0,1]:
                        stageId = schedulesData["data"]["festSchedules"]["nodes"][pvpNode]["festMatchSetting"]["vsStages"][i]["id"]
                        if i == 0:
                            fesBattleStageName = fesBattleStageName + jpData["stages"][stageId]["name"] + "◀️ ▶️"
                        else:
                            fesBattleStageName = fesBattleStageName + jpData["stages"][stageId]["name"]
                        for stagesList in schedulesData["data"]["vsStages"]["nodes"]:
                            if stagesList["id"]==stageId:
                                stageURL = stagesList["originalImage"]["url"]
                                break
                        async with aiohttp.ClientSession() as client:
                            async with client.get(stageURL) as resp:
                                f = await aiofiles.open(f"./splatoonPic/fesBattle-{i}.png",'wb')
                                await f.write(await resp.read())
                                await f.close()
                            await client.close() 
                    fesBattleStagePic1 = Image.open("./splatoonPic/fesBattle-0.png")
                    fesBattleStagePic2 = Image.open("./splatoonPic/fesBattle-1.png")
                    pvpPic(fesBattleStagePic1,fesBattleStagePic2).save("./splatoonPic/fesBattle.png")
                    fesBattleStagePic1.close()
                    fesBattleStagePic2.close()
                    fesBattleEmbed.add_field(name="<:regularBattle2:1097503391250382910>ナワバリバトル",value=fesBattleStageName,inline=False)
                    fesBattleFile = discord.File("./splatoonPic/fesBattle.png",filename="fesBattle.png")
                    fesBattleEmbed.set_image(url = "attachment://fesBattle.png")
                    fesBattleEmbed.set_footer(text="Powered by splatoon3.ink")
                    allEmbed.append(fesBattleEmbed)
                    allFile.append(fesBattleFile)

                    #Fes Tri Battle
                    fesTriStartTime = datetime.datetime.strptime(schedulesData["data"]["currentFest"]["midtermTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                    fesTriEndTime = datetime.datetime.strptime(schedulesData["data"]["currentFest"]["endTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                    fesTriStartTime = discord.utils.format_dt(fesTriStartTime,style="f")
                    fesTriEndTime = discord.utils.format_dt(fesTriEndTime,style="f")
                    fesTriBattleEmbed=discord.Embed(title=f"<:fesBattle:1104726692515299359>フェスマッチ", color=0x19d719,description=f"{fesTriStartTime} ~ {fesTriEndTime}")
                    stageId = schedulesData["data"]["currentFest"]["tricolorStage"]["id"]
                    fesTriBattleStageName = jpData["stages"][stageId]["name"]
                    stageURL = schedulesData["data"]["currentFest"]["tricolorStage"]["image"]["url"]
                    async with aiohttp.ClientSession() as client:
                        async with client.get(stageURL) as resp:
                            f = await aiofiles.open(f"./splatoonPic/fesTriBattle.png",'wb')
                            await f.write(await resp.read())
                            await f.close()
                        await client.close() 
                    fesTriBattleEmbed.add_field(name="<:fesBattle:1104726692515299359>トリカラマッチ",value=fesTriBattleStageName,inline=False)
                    fesTriBattleFile = discord.File("./splatoonPic/fesTriBattle.png",filename="fesTriBattle.png")
                    fesTriBattleEmbed.set_image(url = "attachment://fesTriBattle.png")
                    fesTriBattleEmbed.set_footer(text="Powered by splatoon3.ink")
                    allEmbed.append(fesTriBattleEmbed)
                    allFile.append(fesTriBattleFile)

                else:
                    pvpNode = 0
                    while True:
                        pvpStartTime = datetime.datetime.strptime(schedulesData["data"]["regularSchedules"]["nodes"][pvpNode]["startTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                        pvpEndTime = datetime.datetime.strptime(schedulesData["data"]["regularSchedules"]["nodes"][pvpNode]["endTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                        if (datetime.datetime.now()-pvpStartTime).total_seconds()>=0 and (pvpEndTime-datetime.datetime.now()).total_seconds()>=0:
                            break
                        pvpNode = pvpNode + 1

                    pvpStartTime = discord.utils.format_dt(pvpStartTime,style="f")
                    pvpEndTime = discord.utils.format_dt(pvpEndTime,style="f")

                    #Regular Battle
                    regularBattleEmbed=discord.Embed(title=f"<:regularBattle1:1097503381754495016>レギュラーマッチ", color=0x19d719,description=f"{pvpStartTime} ~ {pvpEndTime}")
                    regularBattleStageName=""
                    for i in [0,1]:
                        stageId = schedulesData["data"]["regularSchedules"]["nodes"][pvpNode]["regularMatchSetting"]["vsStages"][i]["id"]
                        if i == 0:
                            regularBattleStageName = regularBattleStageName + jpData["stages"][stageId]["name"] + "◀️ ▶️"
                        else:
                            regularBattleStageName = regularBattleStageName + jpData["stages"][stageId]["name"]
                        for stagesList in schedulesData["data"]["vsStages"]["nodes"]:
                            if stagesList["id"]==stageId:
                                stageURL = stagesList["originalImage"]["url"]
                                break
                        async with aiohttp.ClientSession() as client:
                            async with client.get(stageURL) as resp:
                                f = await aiofiles.open(f"./splatoonPic/regularBattle-{i}.png",'wb')
                                await f.write(await resp.read())
                                await f.close()
                            await client.close() 
                    regularBattleStagePic1 = Image.open("./splatoonPic/regularBattle-0.png")
                    regularBattleStagePic2 = Image.open("./splatoonPic/regularBattle-1.png")
                    pvpPic(regularBattleStagePic1,regularBattleStagePic2).save("./splatoonPic/regularBattle.png")
                    regularBattleStagePic1.close()
                    regularBattleStagePic2.close()
                    regularBattleEmbed.add_field(name="<:regularBattle2:1097503391250382910>ナワバリバトル",value=regularBattleStageName,inline=False)
                    regularBattleFile = discord.File("./splatoonPic/regularBattle.png",filename="regularBattle.png")
                    regularBattleEmbed.set_image(url = "attachment://regularBattle.png")
                    regularBattleEmbed.set_footer(text="Powered by splatoon3.ink")
                    allEmbed.append(regularBattleEmbed)
                    allFile.append(regularBattleFile)

                    #BankaraBattle Challenge
                    bankaraBattleChallengeEmbed=discord.Embed(title=f"<:bankaraBattle:1097503386699571240>バンカラーマッチ「チャレンジ」", color=0xf54910,description=f"{pvpStartTime} ~ {pvpEndTime}")
                    bankaraBattleChallengeStageName=""
                    for i in [0,1]:
                        stageId = schedulesData["data"]["bankaraSchedules"]["nodes"][pvpNode]["bankaraMatchSettings"][0]["vsStages"][i]["id"]
                        if i == 0:
                            bankaraBattleChallengeStageName = bankaraBattleChallengeStageName + jpData["stages"][stageId]["name"] + "◀️ ▶️"
                        else:
                            bankaraBattleChallengeStageName = bankaraBattleChallengeStageName + jpData["stages"][stageId]["name"]
                        for stagesList in schedulesData["data"]["vsStages"]["nodes"]:
                            if stagesList["id"]==stageId:
                                stageURL = stagesList["originalImage"]["url"]
                                break
                    
                        async with aiohttp.ClientSession() as client:
                            async with client.get(stageURL) as resp:
                                f = await aiofiles.open(f"./splatoonPic/bankaraChallenge-{i}.png",'wb')
                                await f.write(await resp.read())
                                await f.close()
                            await client.close()  
                    ruleId = schedulesData["data"]["bankaraSchedules"]["nodes"][pvpNode]["bankaraMatchSettings"][0]["vsRule"]["id"]
                    ruleName = jpData["rules"][ruleId]["name"]
                    if(ruleName=="ガチヤグラ"):
                        ruleName = "<:gachiyagura:1097503398472986674>" + ruleName
                    elif(ruleName=="ガチホコバトル"):
                        ruleName = "<:gachihokobatoru:1097503413295648830>" + ruleName
                    elif(ruleName=="ガチエリア"):
                        ruleName = "<:gachieria:1097503404454072432>" + ruleName
                    elif(ruleName=="ガチアサリ"):
                        ruleName = "<:gachiasari:1097503408648355961>" + ruleName
                
                    bankaraChallengeStagePic1 = Image.open("./splatoonPic/bankaraChallenge-0.png")
                    bankaraChallengeStagePic2 = Image.open("./splatoonPic/bankaraChallenge-1.png")
                    pvpPic(bankaraChallengeStagePic1,bankaraChallengeStagePic2).save("./splatoonPic/bankaraChallenge.png")
                    bankaraChallengeStagePic1.close()
                    bankaraChallengeStagePic2.close()
                    bankaraBattleChallengeEmbed.add_field(name=ruleName,value=bankaraBattleChallengeStageName)
                    bankaraBattleChallengeFile = discord.File("./splatoonPic/bankaraChallenge.png",filename="bankaraChallenge.png")
                    bankaraBattleChallengeEmbed.set_image(url = "attachment://bankaraChallenge.png")
                    bankaraBattleChallengeEmbed.set_footer(text="Powered by splatoon3.ink")
                    allEmbed.append(bankaraBattleChallengeEmbed)
                    allFile.append(bankaraBattleChallengeFile)

                    #BankaraBattle Open
                    bankaraBattleOpenEmbed=discord.Embed(title=f"<:bankaraBattle:1097503386699571240>バンカラーマッチ「オープン」", color=0xf54910,description=f"{pvpStartTime} ~ {pvpEndTime}")
                    bankaraBattleOpenStagesName=""
                    for i in [0,1]:
                        stageId = schedulesData["data"]["bankaraSchedules"]["nodes"][pvpNode]["bankaraMatchSettings"][1]["vsStages"][i]["id"]
                        if i == 0:
                            bankaraBattleOpenStagesName = bankaraBattleOpenStagesName + jpData["stages"][stageId]["name"] + "◀️ ▶️"
                        else:
                            bankaraBattleOpenStagesName = bankaraBattleOpenStagesName + jpData["stages"][stageId]["name"]
                        for stagesList in schedulesData["data"]["vsStages"]["nodes"]:
                            if stagesList["id"]==stageId:
                                stageURL = stagesList["originalImage"]["url"]
                                break
                        
                        async with aiohttp.ClientSession() as client:
                            async with client.get(stageURL) as resp:
                                f = await aiofiles.open(f"./splatoonPic/bankaraOpen-{i}.png",'wb')
                                await f.write(await resp.read())
                                await f.close()
                            await client.close() 
                    ruleId = schedulesData["data"]["bankaraSchedules"]["nodes"][pvpNode]["bankaraMatchSettings"][1]["vsRule"]["id"]
                    ruleName = jpData["rules"][ruleId]["name"]
                    if(ruleName=="ガチヤグラ"):
                        ruleName = "<:gachiyagura:1097503398472986674>" + ruleName
                    elif(ruleName=="ガチホコバトル"):
                        ruleName = "<:gachihokobatoru:1097503413295648830>" + ruleName
                    elif(ruleName=="ガチエリア"):
                        ruleName = "<:gachieria:1097503404454072432>" + ruleName
                    elif(ruleName=="ガチアサリ"):
                        ruleName = "<:gachiasari:1097503408648355961>" + ruleName
                    
                    bankaraBattleOpenEmbed.add_field(name=ruleName,value=bankaraBattleOpenStagesName)
                    bankaraOpenStagePic1 = Image.open("./splatoonPic/bankaraOpen-0.png")
                    bankaraOpenStagePic2 = Image.open("./splatoonPic/bankaraOpen-1.png")
                    pvpPic(bankaraOpenStagePic1,bankaraOpenStagePic2).save("./splatoonPic/bankaraOpen.png")
                    bankaraOpenStagePic1.close()
                    bankaraOpenStagePic2.close()
                    bankaraBattleOpenfile = discord.File("./splatoonPic/bankaraOpen.png",filename="bankaraOpen.png")
                    bankaraBattleOpenEmbed.set_image(url = "attachment://bankaraOpen.png")
                    bankaraBattleChallengeEmbed.set_footer(text="Powered by splatoon3.ink")
                    allEmbed.append(bankaraBattleOpenEmbed)
                    allFile.append(bankaraBattleOpenfile)


                    #X-Battle
                    xBattleEmbed=discord.Embed(title=f"<:xBattle:1097503393825685646>Xマッチ", color=0x0fdb9a,description=f"{pvpStartTime} ~ {pvpEndTime}")
                    xBattleStagesName=""
                    for i in [0,1]:
                        stageId = schedulesData["data"]["xSchedules"]["nodes"][pvpNode]["xMatchSetting"]["vsStages"][i]["id"]
                        if i == 0:
                            xBattleStagesName = xBattleStagesName + jpData["stages"][stageId]["name"] + "◀️ ▶️"
                        else:
                            xBattleStagesName = xBattleStagesName + jpData["stages"][stageId]["name"]

                        for stagesList in schedulesData["data"]["vsStages"]["nodes"]:
                            if stagesList["id"]==stageId:
                                stageURL = stagesList["originalImage"]["url"]
                                break
                        
                        async with aiohttp.ClientSession() as client:
                            async with client.get(stageURL) as resp:
                                f = await aiofiles.open(f"./splatoonPic/xBattle-{i}.png",'wb')
                                await f.write(await resp.read())
                                await f.close()
                            await client.close() 
                    
                    ruleId = schedulesData["data"]["xSchedules"]["nodes"][pvpNode]["xMatchSetting"]["vsRule"]["id"]
                    ruleName = jpData["rules"][ruleId]["name"]
                    if(ruleName=="ガチヤグラ"):
                        ruleName = "<:gachiyagura:1097503398472986674>" + ruleName
                    elif(ruleName=="ガチホコバトル"):
                        ruleName = "<:gachihokobatoru:1097503413295648830>" + ruleName
                    elif(ruleName=="ガチエリア"):
                        ruleName = "<:gachieria:1097503404454072432>" + ruleName
                    elif(ruleName=="ガチアサリ"):
                        ruleName = "<:gachiasari:1097503408648355961>" + ruleName

                    xBattleEmbed.add_field(name=ruleName,value=xBattleStagesName)

                    xBattleStagePic1 = Image.open("./splatoonPic/xBattle-0.png")
                    xBattleStagePic2 = Image.open("./splatoonPic/xBattle-1.png")
                    pvpPic(xBattleStagePic1,xBattleStagePic2).save("./splatoonPic/xBattle.png")
                    xBattleStagePic1.close()
                    xBattleStagePic2.close()
                    xBattlefile = discord.File("./splatoonPic/xBattle.png",filename="xBattle.png")
                    xBattleEmbed.set_image(url = "attachment://xBattle.png")
                    xBattleEmbed.set_footer(text="Powered by splatoon3.ink")
                    allEmbed.append(xBattleEmbed)
                    allFile.append(xBattlefile)

                    #event-Battle
                    for timePeriods in schedulesData["data"]["eventSchedules"]["nodes"][0]["timePeriods"]:
                        eventStartTime = datetime.datetime.strptime(timePeriods["startTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                        eventEndTime = datetime.datetime.strptime(timePeriods["endTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                        lastStart = (datetime.datetime.now() - eventStartTime).total_seconds()
                        lastEnd = (eventEndTime - datetime.datetime.now()).total_seconds()
                        
                        if lastStart>0 and lastEnd>0:

                            eventId = schedulesData["data"]["eventSchedules"]["nodes"][0]["leagueMatchSetting"]["leagueMatchEvent"]["id"]
                            eventName = jpData["events"][eventId]["name"]
                            
                            eventRegulation:str = jpData["events"][eventId]["regulation"]
                            eventRegulation = eventRegulation.replace("<br /><br />","<br />")
                            eventRegulation = "・ " + eventRegulation.replace("<br />","\n") + "\n"
                            eventEmbed=discord.Embed(title=f"<:eventBattle:1119186275614871612>{eventName}", color=0xea4074,description=f"{pvpStartTime} ~ {pvpEndTime}")
                            eventEmbed.add_field(name="インフォー",value=eventRegulation,inline=False)
                            for i in [0,1]:
                                stageId = schedulesData["data"]["eventSchedules"]["nodes"][0]["leagueMatchSetting"]["vsStages"][i]["id"]
                                if i == 0:
                                    eventStagesName = jpData["stages"][stageId]["name"] + "◀️ ▶️"
                                else:
                                    eventStagesName = eventStagesName + jpData["stages"][stageId]["name"]

                                for stagesList in schedulesData["data"]["vsStages"]["nodes"]:
                                    if stagesList["id"]==stageId:
                                        stageURL = stagesList["originalImage"]["url"]
                                        break
                                
                                async with aiohttp.ClientSession() as client:
                                    async with client.get(stageURL) as resp:
                                        f = await aiofiles.open(f"./splatoonPic/eventBattle-{i}.png",'wb')
                                        await f.write(await resp.read())
                                        await f.close()
                                    await client.close() 
                            ruleId = schedulesData["data"]["eventSchedules"]["nodes"][0]["leagueMatchSetting"]["vsRule"]["id"]
                            ruleName = jpData["rules"][ruleId]["name"]
                            if(ruleName=="ガチヤグラ"):
                                ruleName = "<:gachiyagura:1097503398472986674>" + ruleName
                            elif(ruleName=="ガチホコバトル"):
                                ruleName = "<:gachihokobatoru:1097503413295648830>" + ruleName
                            elif(ruleName=="ガチエリア"):
                                ruleName = "<:gachieria:1097503404454072432>" + ruleName
                            elif(ruleName=="ガチアサリ"):
                                ruleName = "<:gachiasari:1097503408648355961>" + ruleName
                            elif(ruleName=="ナワバリバトル"):
                                ruleName = "<:regularBattle2:1097503391250382910>" + ruleName
                            
                            eventEmbed.add_field(name=ruleName,value=eventStagesName,inline=False)
                            
                            eventStagePic1 = Image.open("./splatoonPic/eventBattle-0.png")
                            eventStagePic2 = Image.open("./splatoonPic/eventBattle-1.png")
                            pvpPic(eventStagePic1,eventStagePic2).save("./splatoonPic/eventBattle.png")
                            eventStagePic1.close()
                            eventStagePic2.close()
                            eventBattlefile = discord.File("./splatoonPic/eventBattle.png",filename="eventBattle.png")
                            eventEmbed.set_image(url = "attachment://eventBattle.png")
                            eventEmbed.set_footer(text="Powered by splatoon3.ink")
                            allEmbed.append(eventEmbed)
                            allFile.append(eventBattlefile)

                #SalmonRun
                pveNode = 0
                while True:
                    pveStartTime = datetime.datetime.strptime(schedulesData["data"]["coopGroupingSchedule"]["regularSchedules"]["nodes"][pveNode]["startTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                    pveEndTime = datetime.datetime.strptime(schedulesData["data"]["coopGroupingSchedule"]["regularSchedules"]["nodes"][pveNode]["endTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                    if (datetime.datetime.now()-pveStartTime).total_seconds()>=0 and (pveEndTime-datetime.datetime.now()).total_seconds()>=0:
                        break
                    pveNode = pveNode + 1

                salmonRegular:list = schedulesData["data"]["coopGroupingSchedule"]["regularSchedules"]["nodes"][pveNode]["setting"]["coopStage"]
                pveLastTime = discord.utils.format_dt(pveEndTime,style="R")
                # datetime.datetime.strptime(f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day} {datetime.datetime.now().hour}:00:00","%Y-%m-%d %H:%M:%S")
                pveStartTime = discord.utils.format_dt(pveStartTime,style="f")
                pveEndTime = discord.utils.format_dt(pveEndTime,style="f")
                salMonRunEmbed=discord.Embed(title=f"<:kumasan:1097503418907635732>サーモンラン", color=0xf6542d,description=f"{pveStartTime} ~ {pveEndTime}「残り {pveLastTime} 」")
                
                if len(salmonRegular)>0:
                    stageId = salmonRegular["id"]
                    stageURL = salmonRegular["image"]["url"]
                    stageName = "•" + jpData["stages"][stageId]["name"]
                    weaponName = ""
                    async with aiohttp.ClientSession() as client:
                        async with client.get(stageURL) as resp:
                            f = await aiofiles.open(f"./splatoonPic/salmonRegularStage.png",'wb')
                            await f.write(await resp.read())
                            await f.close()
                        await client.close() 
                    i = 0
                    for weapon in schedulesData["data"]["coopGroupingSchedule"]["regularSchedules"]["nodes"][pveNode]["setting"]["weapons"]:
                        weaponId = weapon["__splatoon3ink_id"]
                        weaponURL = weapon["image"]["url"]
                        if i !=3:
                            weaponName= weaponName + " • "+ jpData["weapons"][weaponId]["name"]+ "\n" 
                        else:
                            weaponName= weaponName + " • "+ jpData["weapons"][weaponId]["name"]
                        async with aiohttp.ClientSession() as client:
                            async with client.get(weaponURL) as resp:
                                f = await aiofiles.open(f"./splatoonPic/salmonRegularWeapon-{i}.png",'wb')
                                await f.write(await resp.read())
                                await f.close()
                            await client.close() 
                        i = i + 1
                    salmonRegularStagePic = Image.open("./splatoonPic/salmonRegularStage.png")
                    salmonRegularWeapon1 = Image.open("./splatoonPic/salmonRegularWeapon-0.png").resize((70,70))
                    salmonRegularWeapon2 = Image.open("./splatoonPic/salmonRegularWeapon-1.png").resize((70,70))
                    salmonRegularWeapon3 = Image.open("./splatoonPic/salmonRegularWeapon-2.png").resize((70,70))
                    salmonRegularWeapon4 = Image.open("./splatoonPic/salmonRegularWeapon-3.png").resize((70,70))
                    salmonrunPic(salmonRegularStagePic,salmonRegularWeapon1,salmonRegularWeapon2,salmonRegularWeapon3,salmonRegularWeapon4).save("./splatoonPic/salmonRegular.png")
                    salmonRegularStagePic.close()
                    salmonRegularWeapon1.close()
                    salmonRegularWeapon2.close()
                    salmonRegularWeapon3.close()
                    salmonRegularWeapon4.close()
                    salMonRunEmbed.add_field(name="「ステージ」",value=stageName,inline=False)
                    salMonRunEmbed.add_field(name="「支給ブキ」",value=weaponName)
                    salMonRunfile = discord.File("./splatoonPic/salmonRegular.png",filename="salmonRegular.png")
                    salMonRunEmbed.set_image(url = "attachment://salmonRegular.png")
                    salMonRunEmbed.set_footer(text="Powered by splatoon3.ink")
                    allEmbed.append(salMonRunEmbed)
                    allFile.append(salMonRunfile)
                
                #Big-RUN TO-DO

                #Team-Contest
                if len(schedulesData["data"]["coopGroupingSchedule"]["teamContestSchedules"]["nodes"])>0:
                    teamContestStartTime = datetime.datetime.strptime(schedulesData["data"]["coopGroupingSchedule"]["teamContestSchedules"]["nodes"][0]["startTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                    teamContestEndTime = datetime.datetime.strptime(schedulesData["data"]["coopGroupingSchedule"]["teamContestSchedules"]["nodes"][0]["endTime"].replace("T"," ").replace("Z",""),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours=9)
                    teamContestLastTime = discord.utils.format_dt(teamContestEndTime,style="R")
                    teamContestStartTime = discord.utils.format_dt(teamContestStartTime,style="f")
                    teamContestEndTime = discord.utils.format_dt(teamContestEndTime,style="f")
                    teamContestEmbed=discord.Embed(title=f"<:goldenegg:1124779346310213763>バイトチームコンテスト", color=0xfdd500,description=f"{teamContestStartTime} ~ {teamContestEndTime}「 残り {teamContestLastTime} 」")
                    
                    stageId = schedulesData["data"]["coopGroupingSchedule"]["teamContestSchedules"]["nodes"][0]["setting"]["coopStage"]["id"]
                    stageURL = schedulesData["data"]["coopGroupingSchedule"]["teamContestSchedules"]["nodes"][0]["setting"]["coopStage"]["image"]["url"]
                    stageName = "•" + jpData["stages"][stageId]["name"]
                    weaponName = ""
                    async with aiohttp.ClientSession() as client:
                        async with client.get(stageURL) as resp:
                            f = await aiofiles.open(f"./splatoonPic/teamContestStage.png",'wb')
                            await f.write(await resp.read())
                            await f.close()
                        await client.close() 
                    i = 0
                    for weapon in schedulesData["data"]["coopGroupingSchedule"]["teamContestSchedules"]["nodes"][0]["setting"]["weapons"]:
                        weaponId = weapon["__splatoon3ink_id"]
                        weaponURL = weapon["image"]["url"]
                        if i !=3:
                            weaponName= weaponName + " • "+ jpData["weapons"][weaponId]["name"]+ "\n" 
                        else:
                            weaponName= weaponName + " • "+ jpData["weapons"][weaponId]["name"]
                        async with aiohttp.ClientSession() as client:
                            async with client.get(weaponURL) as resp:
                                f = await aiofiles.open(f"./splatoonPic/teamContestWeapon-{i}.png",'wb')
                                await f.write(await resp.read())
                                await f.close()
                            await client.close() 
                        i = i + 1
                    teamContestStagePic = Image.open("./splatoonPic/teamContestStage.png")
                    teamContestWeapon1 = Image.open("./splatoonPic/teamContestWeapon-0.png").resize((70,70))
                    teamContestWeapon2 = Image.open("./splatoonPic/teamContestWeapon-1.png").resize((70,70))
                    teamContestWeapon3 = Image.open("./splatoonPic/teamContestWeapon-2.png").resize((70,70))
                    teamContestWeapon4 = Image.open("./splatoonPic/teamContestWeapon-3.png").resize((70,70))
                    salmonrunPic(teamContestStagePic,teamContestWeapon1,teamContestWeapon2,teamContestWeapon3,teamContestWeapon4).save("./splatoonPic/teamContest.png")
                    teamContestStagePic.close()
                    teamContestWeapon1.close()
                    teamContestWeapon2.close()
                    teamContestWeapon3.close()
                    teamContestWeapon4.close()
                    teamContestEmbed.add_field(name="「ステージ」",value=stageName,inline=False)
                    teamContestEmbed.add_field(name="「支給ブキ」",value=weaponName)
                    teamContestfile = discord.File("./splatoonPic/teamContest.png",filename="teamContest.png")
                    teamContestEmbed.set_image(url = "attachment://teamContest.png")
                    teamContestEmbed.set_footer(text="Powered by splatoon3.ink")
                    allEmbed.append(teamContestEmbed)
                    allFile.append(teamContestfile)

                    # 1096242499795816448
                    # test: 1068098801526657087
                await self.bot.get_channel(1096242499795816448).send(files=allFile,embeds=allEmbed)

                return
            except:
                traceback.print_exc()
                await asyncio.sleep(10)
        
    
async def setup(bot):
    await bot.add_cog(Splatoon3(bot))