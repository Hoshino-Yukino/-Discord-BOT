import discord
from discord import app_commands
from discord.ext import commands
from PicImageSearch import SauceNAO,Ascii2D
from scrapingant_client import ScrapingAntClient
import json

with open('./setting.json','r',encoding='utf8') as setting_file:
    setting = json.load(setting_file)

class PicSearch(commands.Cog):

    def __init__(self,bot):
        self.bot:commands.Bot = bot
        self.searchMenu = app_commands.ContextMenu(
            name="フォト検索",
            callback=self.contextSearch,
        )
        self.bot.tree.add_command(self.searchMenu)

    @app_commands.command(name="search",description="Image search")
    @app_commands.choices(
        mode=[
            discord.app_commands.Choice(name="SauceNao",value="SauceNao"),
            discord.app_commands.Choice(name="Ascii2d",value="Ascii2d"),
    ])
    @app_commands.describe(mode="Search mode",image="The image you want to search")
    async def search(self,interaction:discord.Interaction,mode:discord.app_commands.Choice[str]="NULL",image:discord.Attachment=None):
        if image==None or image.content_type.find("image")==-1:
            await interaction.response.send_message(content="You must send image with the cmd",ephemeral=True)
            return
        await interaction.response.defer(thinking=True)
        try:
            if mode.value=="SauceNao":
                par = "-s"
            elif mode.value=="Ascii2d":
                par = "-a"
        except:
            par = "NULL"
    
        if par=="-s":
            try:
                pic_url = image.proxy_url
                saucenao = SauceNAO(api_key=setting["saucenao_apikey"],numres=10)
                resp = await saucenao.search(url=pic_url)
                max_item = 0
                now_search = 1
                while now_search<=resp.results_returned-1:
                    if resp.raw[now_search].similarity>=resp.raw[max_item].similarity:
                        max_item = now_search
                    now_search = now_search + 1
                embed=discord.Embed(title="「" +resp.raw[max_item].author +"」/「" + resp.raw[max_item].title  +"」", color=0x0088ff)
                embed.set_thumbnail(url=resp.raw[max_item].thumbnail)
                embed.add_field(name="Similarity", value=str(str(resp.raw[max_item].similarity)) + "%", inline=False)
                if(resp.raw[max_item].url!=""):
                    embed.add_field(name="Artist", value=resp.raw[max_item].url, inline=False)
                if(resp.raw[max_item].author_url!=""):
                    embed.add_field(name="Arthur", value=resp.raw[max_item].author_url, inline=False)
                if(resp.raw[max_item].url=="" and resp.raw[max_item].author_url=="" and resp.raw[max_item].source!=""):
                    embed.add_field(name="同人誌検索中。。。",value="少々お待ちください",inline=False)
                    doujin = await interaction.followup.send(embed=embed,wait=True)
                    client = ScrapingAntClient(token=setting["ScrapingAnt_token"])
                    result = await client.general_request_async(url='https://nhentai.net/search/?q='+resp.raw[max_item].source)
                    result_list = result.content.split('<a href="/g/')
                    embed.remove_field(1)
                    if len(result_list)<=1:
                        embed.add_field(name="検索結果",value="何もありません")
                        await doujin.edit(embed=embed)
                        return
                    now_result = 1
                    embed.add_field(name="検索結果:",value="合わせ：" + str(len(result_list)-1))
                    while now_result<len(result_list):
                        embed.add_field(name=result_list[now_result].split('<div class="caption">')[1].split('</div>')[0],
                            value="https://nhentai.net/g/" + result_list[now_result].split('"')[0],inline=False)
                        now_result = now_result + 1
                    await doujin.edit(embed=embed)
                    return
                await interaction.followup.send(embed=embed)
                return
            except Exception as reason:
                print(reason)
                sau_err=True
                await interaction.followup.send("SauceNao搜索出错",ephemeral=True)
                return
        if par=="-a":
            try:
                pic_url = image.proxy_url
                ascii2d = Ascii2D(bovw=False)
                resp = await ascii2d.search(url=pic_url)
                selected = resp.raw[0]
                if not (selected.title or selected.url):
                    selected = resp.raw[1]
                if not (selected.title or selected.url):
                    embed=discord.Embed(title="「Ascii2d未收录图片详情」", color=0x0088ff)
                else:
                    embed=discord.Embed(title="「" +selected.author +"」/「" + selected.title  +"」", color=0x0088ff)
                embed.set_thumbnail(url=selected.thumbnail)
                if(selected.author!=""):
                    embed.add_field(name="Artist", value=selected.url, inline=False)
                if selected.author!="":
                    embed.add_field(name="Author", value=selected.author, inline=False)
                await interaction.followup.send(embed=embed)
                return
            except Exception as reason:
                print (reason)
                await interaction.followup.send("Ascii2d色合検索出错",ephemeral=True)
                return
        
        sau_err=False
        pic_url = image.proxy_url
        saucenao = SauceNAO(api_key=setting["saucenao_apikey"])
        try:
            resp = await saucenao.search(url=pic_url)
            max_item = 0
            now_search = 1
            while now_search<=resp.results_returned-1:
                if resp.raw[now_search].similarity>=resp.raw[max_item].similarity:
                    max_item = now_search
                now_search = now_search + 1
            embed=discord.Embed(title="「" +resp.raw[max_item].author +"」/「" + resp.raw[max_item].title  +"」", color=0x0088ff)
            embed.set_thumbnail(url=resp.raw[max_item].thumbnail)
            embed.add_field(name="Similarity", value=str(str(resp.raw[max_item].similarity)) + "%", inline=False)
            if(resp.raw[max_item].url!=""):
                embed.add_field(name="Artist", value=resp.raw[max_item].url, inline=False)
            if(resp.raw[max_item].author_url!=""):
                embed.add_field(name="Arthur", value=resp.raw[max_item].author_url, inline=False)
            if(resp.raw[max_item].url=="" and resp.raw[max_item].author_url=="" and resp.raw[max_item].source!=""):
                embed.add_field(name="同人誌検索中。。。",value="少々お待ちください",inline=False)
                doujin = await interaction.followup.send(embed=embed,wait=True)
                client = ScrapingAntClient(token=setting["ScrapingAnt_token"])
                result = await client.general_request_async(url='https://nhentai.net/search/?q='+resp.raw[max_item].source)
                result_list = result.content.split('<a href="/g/')
                embed.remove_field(1)
                if len(result_list)<=1:
                    embed.add_field(name="検索結果",value="何もありません")
                    await doujin.edit(embed=embed)
                    return
                now_result = 1
                embed.add_field(name="検索結果:",value="合わせ：" + str(len(result_list)-1))
                while now_result<len(result_list):
                    embed.add_field(name=result_list[now_result].split('<div class="caption">')[1].split('</div>')[0],
                        value="https://nhentai.net/g/" + result_list[now_result].split('"')[0],inline=False)
                    now_result = now_result + 1
                await doujin.edit(embed=embed)
                return
            if resp.raw[max_item].similarity < 80:
                embed.add_field(name="PS", value="相似度过低，将使用Ascii2D色合検索")
            await interaction.followup.send(embed=embed)
        except:
            sau_err=True
            await interaction.followup.send("SauceNao搜索出错，将使用Ascii2D色合検索",ephemeral=True)
        
        if resp.raw[0].similarity < 80 or sau_err==True:
            try:
                ascii2d = Ascii2D(bovw=False)
                resp = await ascii2d.search(url=pic_url)
                selected = resp.raw[0]
                if not (selected.title or selected.url):
                    selected = resp.raw[1]
                if not (selected.title or selected.url):
                    embed=discord.Embed(title="「Ascii2d未收录图片详情」", color=0x0088ff)
                else:
                    embed=discord.Embed(title="「" +selected.author +"」/「" + selected.title  +"」", color=0x0088ff)
                embed.set_thumbnail(url=selected.thumbnail)
                if(selected.author!=""):
                    embed.add_field(name="Artist", value=selected.url, inline=False)
                if selected.author!="":
                    embed.add_field(name="Author", value=selected.author, inline=False)
                await interaction.followup.send(embed=embed)
            except:
                await interaction.followup.send("Ascii2d色合検索出错",ephemeral=True)

    @app_commands.guild_only()
    async def contextSearch(self,interaction:discord.Interaction,message:discord.Message):
        if len(message.attachments)==0 and message.embeds[0].image==None:
            await interaction.response.send_message(content="Must be used in the message with picture",ephemeral=True)
            return
        await interaction.response.defer(thinking=True,ephemeral=True)
        imageCount=0
        for image in message.attachments:
            if image.content_type.find("image")==-1:
                continue  
            imageCount = imageCount + 1  
            sau_err=False
            pic_url = image.proxy_url
            saucenao = SauceNAO(api_key=setting["saucenao_apikey"])
            try:
                resp = await saucenao.search(url=pic_url)
                max_item = 0
                now_search = 1
                while now_search<=resp.results_returned-1:
                    if resp.raw[now_search].similarity>=resp.raw[max_item].similarity:
                        max_item = now_search
                    now_search = now_search + 1
                embed=discord.Embed(title="「" +resp.raw[max_item].author +"」/「" + resp.raw[max_item].title  +"」", color=0x0088ff)
                embed.set_thumbnail(url=resp.raw[max_item].thumbnail)
                embed.add_field(name="Similarity", value=str(str(resp.raw[max_item].similarity)) + "%", inline=False)
                if(resp.raw[max_item].url!=""):
                    embed.add_field(name="Artist", value=resp.raw[max_item].url, inline=False)
                if(resp.raw[max_item].author_url!=""):
                    embed.add_field(name="Arthur", value=resp.raw[max_item].author_url, inline=False)
                if(resp.raw[max_item].url=="" and resp.raw[max_item].author_url=="" and resp.raw[max_item].source!=""):
                    embed.add_field(name="同人誌検索中。。。",value="少々お待ちください",inline=False)
                    doujin = await interaction.followup.send(embed=embed,wait=True,ephemeral=True)
                    client = ScrapingAntClient(token=setting["ScrapingAnt_token"])
                    result = await client.general_request_async(url='https://nhentai.net/search/?q='+resp.raw[max_item].source)
                    result_list = result.content.split('<a href="/g/')
                    embed.remove_field(1)
                    if len(result_list)<=1:
                        embed.add_field(name="検索結果",value="何もありません")
                        await doujin.edit(embed=embed)
                        return
                    now_result = 1
                    embed.add_field(name="検索結果:",value="合わせ：" + str(len(result_list)-1))
                    while now_result<len(result_list):
                        embed.add_field(name=result_list[now_result].split('<div class="caption">')[1].split('</div>')[0],
                            value="https://nhentai.net/g/" + result_list[now_result].split('"')[0],inline=False)
                        now_result = now_result + 1
                    await doujin.edit(embed=embed)
                    return
                if resp.raw[max_item].similarity < 80:
                    embed.add_field(name="PS", value="相似度过低，将使用Ascii2D色合検索")
                await interaction.followup.send(embed=embed,ephemeral=True)
            except:
                sau_err=True
                await interaction.followup.send("SauceNao搜索出错，将使用Ascii2D色合検索",ephemeral=True)
            
            if resp.raw[0].similarity < 80 or sau_err==True:
                try:
                    ascii2d = Ascii2D(bovw=False)
                    resp = await ascii2d.search(url=pic_url)
                    selected = resp.raw[0]
                    if not (selected.title or selected.url):
                        selected = resp.raw[1]
                    if not (selected.title or selected.url):
                        embed=discord.Embed(title="「Ascii2d未收录图片详情」", color=0x0088ff)
                    else:
                        embed=discord.Embed(title="「" +selected.author +"」/「" + selected.title  +"」", color=0x0088ff)
                    embed.set_thumbnail(url=selected.thumbnail)
                    if(selected.author!=""):
                        embed.add_field(name="Artist", value=selected.url, inline=False)
                    if selected.author!="":
                        embed.add_field(name="Author", value=selected.author, inline=False)
                    await interaction.followup.send(embed=embed,ephemeral=True)
                except:
                    await interaction.followup.send("Ascii2d色合検索出错",ephemeral=True)

        if message.embeds[0].image!=None:
            imageCount = imageCount + 1  
            sau_err=False
            pic_url = message.embeds[0].image.url
            saucenao = SauceNAO(api_key=setting["saucenao_apikey"])
            try:
                resp = await saucenao.search(url=pic_url)
                max_item = 0
                now_search = 1
                while now_search<=resp.results_returned-1:
                    if resp.raw[now_search].similarity>=resp.raw[max_item].similarity:
                        max_item = now_search
                    now_search = now_search + 1
                embed=discord.Embed(title="「" +resp.raw[max_item].author +"」/「" + resp.raw[max_item].title  +"」", color=0x0088ff)
                embed.set_thumbnail(url=resp.raw[max_item].thumbnail)
                embed.add_field(name="Similarity", value=str(str(resp.raw[max_item].similarity)) + "%", inline=False)
                if(resp.raw[max_item].url!=""):
                    embed.add_field(name="Artist", value=resp.raw[max_item].url, inline=False)
                if(resp.raw[max_item].author_url!=""):
                    embed.add_field(name="Arthur", value=resp.raw[max_item].author_url, inline=False)
                if(resp.raw[max_item].url=="" and resp.raw[max_item].author_url=="" and resp.raw[max_item].source!=""):
                    embed.add_field(name="同人誌検索中。。。",value="少々お待ちください",inline=False)
                    doujin = await interaction.followup.send(embed=embed,wait=True,ephemeral=True)
                    client = ScrapingAntClient(token=setting["ScrapingAnt_token"])
                    result = await client.general_request_async(url='https://nhentai.net/search/?q='+resp.raw[max_item].source)
                    result_list = result.content.split('<a href="/g/')
                    embed.remove_field(1)
                    if len(result_list)<=1:
                        embed.add_field(name="検索結果",value="何もありません")
                        await doujin.edit(embed=embed)
                        return
                    now_result = 1
                    embed.add_field(name="検索結果:",value="合わせ：" + str(len(result_list)-1))
                    while now_result<len(result_list):
                        embed.add_field(name=result_list[now_result].split('<div class="caption">')[1].split('</div>')[0],
                            value="https://nhentai.net/g/" + result_list[now_result].split('"')[0],inline=False)
                        now_result = now_result + 1
                    await doujin.edit(embed=embed)
                    return
                if resp.raw[max_item].similarity < 80:
                    embed.add_field(name="PS", value="相似度过低，将使用Ascii2D色合検索")
                await interaction.followup.send(embed=embed,ephemeral=True)
            except:
                sau_err=True
                await interaction.followup.send("SauceNao搜索出错，将使用Ascii2D色合検索",ephemeral=True)
            
            if resp.raw[0].similarity < 80 or sau_err==True:
                try:
                    ascii2d = Ascii2D(bovw=False)
                    resp = await ascii2d.search(url=pic_url)
                    selected = resp.raw[0]
                    if not (selected.title or selected.url):
                        selected = resp.raw[1]
                    if not (selected.title or selected.url):
                        embed=discord.Embed(title="「Ascii2d未收录图片详情」", color=0x0088ff)
                    else:
                        embed=discord.Embed(title="「" +selected.author +"」/「" + selected.title  +"」", color=0x0088ff)
                    embed.set_thumbnail(url=selected.thumbnail)
                    if(selected.author!=""):
                        embed.add_field(name="Artist", value=selected.url, inline=False)
                    if selected.author!="":
                        embed.add_field(name="Author", value=selected.author, inline=False)
                    await interaction.followup.send(embed=embed,ephemeral=True)
                except:
                    await interaction.followup.send("Ascii2d色合検索出错",ephemeral=True)
        if imageCount==0:
            await interaction.followup.send(content="Must be used in the message with picture",ephemeral=True)


async def setup(bot):
    await bot.add_cog(PicSearch(bot))