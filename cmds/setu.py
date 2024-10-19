# -*- coding: UTF-8 -*-
import asyncio
import datetime
import discord
from discord import app_commands
from core.classes import Cog_Extension
from discord.ext import tasks,commands
import aiohttp
import traceback
from function.eco import ecoUpdate
from urllib.parse import quote

class SETU(Cog_Extension):
    @app_commands.command(name="来张色图",description="Draw a SETU from PIXIV ~",nsfw=True)
    @app_commands.describe(r18="图片是否为 R18 限制级，默认为False",tags="返回匹配指定标签的作品，可使用&、|")
    async def setu(self,interaction:discord.Interaction,r18:bool=False,tags:str=""):
        badPic=0
        await interaction.response.defer(thinking=True)
        valueErrorFlag = True
        while valueErrorFlag:
            try:
                tags = quote(tags.replace("&","&tag=").replace("｜","|")).replace("%7C","|").replace("%26","&").replace("%3D","=")
                url = f"https://api.lolicon.app/setu/v2?r18={int(r18)}&tag={tags}&proxy=https://pixiv.swqh.online"
                async with aiohttp.ClientSession() as client:
                    async with client.get(url) as resp:
                        setuAPIResponse = await resp.text()
                    await client.close()
                if setuAPIResponse=='{"error":"","data":[]}'and resp.status==200:
                    await interaction.followup.send(content="API错误或tags过于苛刻，无法检索到相关图片")
                    return
                picURL = setuAPIResponse.split("https://")[1].split('"')[0]
                picURL = "https://" + picURL
                pid = picURL.split("img/")[1].split("/")[6].split('"')[0].split("_")[0]
                async with aiohttp.ClientSession() as client:
                    async with client.get(picURL) as resp:
                        setuResponse = resp.ok
                    await client.close()
                if setuResponse !=True:
                    raise ValueError()
                else:
                    valueErrorFlag=False

                pixiv_url = "https://www.pixiv.net/artworks/" + pid
                author = setuAPIResponse.split('"author":"')[1].split('"')[0]
                title = setuAPIResponse.split('"title":"')[1].split('"')[0]
                resultEmbed=discord.Embed(title="「" +author +"」/「" + title  +"」", color=0x0088ff)
                resultEmbed.add_field(name="URL", value=pixiv_url, inline=False)
                resultEmbed.set_image(url=picURL)
                resultEmbed.set_footer(text="Lolicon API")
                setuReact = SetuReact(timeout=None,bot=self.bot)
                await setuReact.send(embed=resultEmbed,interaction=interaction)
                return
            except ValueError:
                traceback.print_exc()
                await asyncio.sleep(5)
                badPic = badPic + 1
                if badPic >= 5:
                    await interaction.followup.send(content="API错误，请稍后重试")
                    return
                pass
            except:
                await interaction.followup.send(content="API错误，请稍后重试")
                traceback.print_exc()
                return
    
    @app_commands.command(name="删除色图投票")
    @app_commands.guild_only()
    @app_commands.default_permissions()
    async def delSetuVote(self,interaction:discord.Interaction,message_id:str):
        try:
            guild = self.bot.get_guild(interaction.guild_id)
            channal= guild.get_channel(interaction.channel_id)
            message = channal.get_partial_message(int(message_id))
            message = await message.fetch()
            if len(message.embeds)==1 and len(message.components)>0 and message.embeds[0].footer.text=="Lolicon API" :
                await message.edit(content=None,view=None)
                await interaction.response.send_message("成功しました",ephemeral=True)
            else:
                await interaction.response.send_message("不正のパラメータです",ephemeral=True)
        except:
            await interaction.response.send_message("不正のパラメータです",ephemeral=True)



class SetuReact(discord.ui.View):
    def __init__(self, *, timeout: float,bot:discord):
        super().__init__(timeout=timeout)
        self.bot:commands.Bot = bot
        self.timeRemain = self.timeRemainSet

    votesHotFaceMax=5
    votesHeartEyeMax=10
    votesFaceWithRaisedEyebrowMax=10
    votesSweatMax=5
    timeRemainSet = 888

    @tasks.loop(seconds=1)
    async def timer(self):
        self.timeRemain = self.timeRemain - 1
        if self.timeRemain <=0:
            if self.finishFlag==True:
                return
            if self.votesHotFace < self.votesHeartEye:
                maxVotes=self.votesHeartEye
                maxVotesName="HeartEye"
            else:
                maxVotes=self.votesHotFace
                maxVotesName="HotFace"
            if maxVotes < self.votesFaceWithRaisedEyebrow:
                maxVotes = self.votesFaceWithRaisedEyebrow
                maxVotesName = "FaceWithRaisedEyebrow"
            if maxVotes < self.votesSweat:
                maxVotes = self.votesSweat
                maxVotesName = "Sweat"            
            
            self.voteHotFace.label=f"「 {self.votesHotFace} 」"
            self.voteHeartEye.label=f"「 {self.votesHeartEye} 」"
            self.voteFaceWithRaisedEyebrow.label=f"「 {self.votesFaceWithRaisedEyebrow} 」"
            self.voteSweat.label=f"「 {self.votesSweat} 」" 
            self.voteHotFace.disabled=True
            self.voteHeartEye.disabled=True
            self.voteFaceWithRaisedEyebrow.disabled=True
            self.voteSweat.disabled=True

            if maxVotesName == "HotFace":
                self.voteHeartEye.style=discord.ButtonStyle.secondary
                self.voteSweat.style=discord.ButtonStyle.secondary
                self.voteFaceWithRaisedEyebrow.style=discord.ButtonStyle.secondary
            elif maxVotesName == "HeartEye":
                self.voteHotFace.style=discord.ButtonStyle.secondary
                self.voteSweat.style=discord.ButtonStyle.secondary
                self.voteFaceWithRaisedEyebrow.style=discord.ButtonStyle.secondary
            elif maxVotesName == "FaceWithRaisedEyebrow":
                self.voteHotFace.style=discord.ButtonStyle.secondary
                self.voteHeartEye.style=discord.ButtonStyle.secondary
                self.voteSweat.style=discord.ButtonStyle.secondary
                self.voteFaceWithRaisedEyebrow.style=discord.ButtonStyle.primary
            elif maxVotesName == "Sweat":
                self.voteHotFace.style=discord.ButtonStyle.secondary
                self.voteHeartEye.style=discord.ButtonStyle.secondary
                self.voteFaceWithRaisedEyebrow.style=discord.ButtonStyle.secondary

            if (self.votesHotFace == self.votesHeartEye) and (self.votesHeartEye==self.votesFaceWithRaisedEyebrow) and (self.votesFaceWithRaisedEyebrow==self.votesSweat):
                self.voteHeartEye.style=discord.ButtonStyle.secondary
                self.voteSweat.style=discord.ButtonStyle.secondary
                self.voteFaceWithRaisedEyebrow.style=discord.ButtonStyle.secondary
                self.voteHotFace.style=discord.ButtonStyle.secondary

            await self.interaction.edit_original_response(view=self,content="`投票終了しました`")
            self.timer.stop()
            self.stop()


    async def send(self,interaction:discord.Interaction,embed:discord.Embed):
        self.interaction:discord.Interaction = interaction
        self.votedId=list()
        self.votesHotFace=0
        self.votesHeartEye=0
        self.votesFaceWithRaisedEyebrow=0
        self.votesSweat=0
        self.finishFlag=False
        timeStamp = datetime.datetime.now() + datetime.timedelta(seconds=self.timeRemainSet)
        discordTimeStamp = discord.utils.format_dt(timeStamp,style="R")
        self.timer.start()

        await interaction.followup.send(embed=embed,view=self,wait=True,content=f"投票時間 「 残り{discordTimeStamp} 」")

    async def win(self,emoji:str):
        if emoji=="HotFace" or emoji=="HeartEye":
            self.clear_items()
            await self.interaction.edit_original_response(view=self)
            originalResponse = await  self.interaction.original_response()
            await originalResponse.pin(reason=f"{emoji} votes exceeded the threshold")

            if emoji=="HotFace":
                await ecoUpdate(DiscordId=self.interaction.user.id,changeMira=200)
            else:
                await ecoUpdate(DiscordId=self.interaction.user.id,changeMira=100)

        elif emoji=="Sweat":
            await self.interaction.delete_original_response()

        elif emoji=="FaceWithRaisedEyebrow":
            self.voteHotFace.disabled=True
            self.voteHeartEye.disabled=True
            self.voteFaceWithRaisedEyebrow.disabled=True
            self.voteSweat.disabled=True

            self.voteHotFace.style=discord.ButtonStyle.secondary
            self.voteHeartEye.style=discord.ButtonStyle.secondary
            self.voteSweat.style=discord.ButtonStyle.secondary
            self.voteFaceWithRaisedEyebrow.style=discord.ButtonStyle.primary

            self.voteHotFace.label=f"「 {self.votesHotFace} 」"
            self.voteHeartEye.label=f"「 {self.votesHeartEye} 」"
            self.voteFaceWithRaisedEyebrow=f"「 {self.votesFaceWithRaisedEyebrow} 」"
            self.voteSweat=f"「 {self.votesSweat} 」"
            
            await self.interaction.edit_original_response(view=self,content=None)
        self.finishFlag=True
        self.timer.cancel()
        self.stop()

    @discord.ui.button(emoji="🥵",style=discord.ButtonStyle.green)
    async def voteHotFace(self,interaction:discord.Interaction,button:discord.ui.Button):
        try:
            if interaction.user.id in self.votedId:
                await interaction.response.send_message(f"{interaction.user.mention} は既に投票したんですよ",ephemeral=True,delete_after=10)
                return
            self.votesHotFace = self.votesHotFace + 1
            self.votedId.append(interaction.user.id)
            await interaction.response.send_message(f"記録しました",ephemeral=True,delete_after=10)
            if self.votesHotFace >= self.votesHotFaceMax:
                await self.win(emoji="HotFace")
        except:
            traceback.print_exc()

    @discord.ui.button(emoji="😍",style=discord.ButtonStyle.primary)
    async def voteHeartEye(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id in self.votedId:
            await interaction.response.send_message(f"{interaction.user.mention} は既に投票したんですよ",ephemeral=True,delete_after=10)
            return
        self.votesHeartEye = self.votesHeartEye + 1
        self.votedId.append(interaction.user.id)
        await interaction.response.send_message(f"記録しました",ephemeral=True,delete_after=10)
        if self.votesHeartEye >= self.votesHeartEyeMax:
            await self.win(emoji="HeartEye")

    @discord.ui.button(emoji="🤨",style=discord.ButtonStyle.secondary)
    async def voteFaceWithRaisedEyebrow(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id in self.votedId:
            await interaction.response.send_message(f"{interaction.user.mention} は既に投票したんですよ",ephemeral=True,delete_after=10)
            return
        self.votesFaceWithRaisedEyebrow = self.votesFaceWithRaisedEyebrow + 1
        self.votedId.append(interaction.user.id)
        await interaction.response.send_message(f"記録しました",ephemeral=True,delete_after=10)
        if self.votesFaceWithRaisedEyebrow >= self.votesFaceWithRaisedEyebrowMax:
            await self.win(emoji="FaceWithRaisedEyebrow")
            
    @discord.ui.button(emoji="😓",style=discord.ButtonStyle.danger)
    async def voteSweat(self,interaction:discord.Interaction,button:discord.ui.Button):
        if interaction.user.id in self.votedId:
            await interaction.response.send_message(f"{interaction.user.mention} は既に投票したんですよ",ephemeral=True,delete_after=10)
            return
        self.votesSweat = self.votesSweat + 1
        self.votedId.append(interaction.user.id)
        await interaction.response.send_message(f"記録しました",ephemeral=True,delete_after=10)
        if self.votesSweat >= self.votesSweatMax:
            await self.win(emoji="Sweat")
    
async def setup(bot):
    await bot.add_cog(SETU(bot))

