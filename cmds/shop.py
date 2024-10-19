import discord
from discord import app_commands
from core.classes import Cog_Extension
from function.eco import *
from function.role import *
class PaginationView(discord.ui.View):
    currentPage:int = 1

    async def send(self,interaction:discord.Interaction):
        self.interaction:discord.Interaction = interaction
        await interaction.response.send_message(embed = self.create_embed(self.currentPage),view=self,ephemeral=True)

    def create_embed(self,page:int):
        if page == -10:
            embed=discord.Embed(title="ロール 商店オフ", description="If you want to buy someting, plz use /shop again.", color=0xfa002a)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1032688154429378650/1039103241121701958/kuma.jpg")
            return embed
        elif page == 0:
            embed=discord.Embed(title=":white_check_mark: 「DJ」ロールの購入ありがとう", color=0x38ff99)
            return embed
        embed=discord.Embed(title="ロール 商店", color=0xf47fff)
        embed.set_thumbnail(url="https://jmusicbot.com/assets/images/logo.png")
        if page == 1:
            embed.add_field(name="MusicBot DJ - ROLE 🎵", value="100 <:mira:1120418935397961858> / 一日", inline=False)
        elif page == 2:
            embed.add_field(name="MusicBot DJ - ROLE 🎵", value="500 <:mira:1120418935397961858> / 一週間", inline=False)
        elif page == 3:
            embed.add_field(name="MusicBot DJ - ROLE 🎵", value="1800 <:mira:1120418935397961858> / 一か月", inline=False)
        embed.add_field(name=":dvd: command: !summon",value="Connects the bot to your current voice channel",inline=False)
        embed.add_field(name=":exclamation: command: !skip f",value="Instantly skip without vote",inline=False)
        embed.add_field(name=":trident: command: !shuffle f",value="Shuffles the queue",inline=False)
        embed.add_field(name=":notes: Maximum length of a song",value="10min to 15min",inline=False)
        embed.add_field(name=":notes: Maximum number of songs a user is allowed to queue",value="5 to 10",inline=False)
        embed.add_field(name=":notes: Maximum number of songs a playlist is allowed to have to be queued",value="20 to Unlimited",inline=False)
        embed.add_field(name=":notes: Remove any song from the queue at any point",value="False to True",inline=False)
        embed.add_field(name=":notes: Queue songs even when karaoke mode is activated",value="False to True",inline=False)
        return embed
    
    async def update_message(self,currentPage):
        await self.update_buttons()
        await self.interaction.edit_original_response(embed=self.create_embed(currentPage),view=self)
    
    async def update_buttons(self):
        if self.currentPage == 1:
            self.backButton.disabled = True
            self.backButton.style = discord.ButtonStyle.gray
        elif self.currentPage == 3:
            self.nextButton.disabled = True
            self.nextButton.style = discord.ButtonStyle.gray
        else:
            self.nextButton.disabled = False
            self.backButton.disabled = False
            self.nextButton.style = discord.ButtonStyle.primary
            self.backButton.style = discord.ButtonStyle.primary


    @discord.ui.button(label="<<",style=discord.ButtonStyle.grey,disabled=True)
    async def backButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.currentPage -= 1
        await self.update_message(self.currentPage)

    @discord.ui.button(label="CANCLE",style=discord.ButtonStyle.danger)
    async def cancleButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        self.clear_items()
        await self.interaction.edit_original_response(embed= self.create_embed(-10),view=self)
        self.stop()
    
    @discord.ui.button(label="BUY",style=discord.ButtonStyle.green)
    async def buyButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        if not await ecoIsInit(interaction.user.id):
            await ecoInit(interaction.user.id)
        days = 0
        costMira = 0
        if self.currentPage==1:
            costMira = -100
            days = 1
        elif self.currentPage==2:
            costMira = -500
            days = 7
        elif self.currentPage==3:
            costMira = -1800
            days = 30
        if await ecoCal(interaction.user.id)+costMira>=0:
            await ecoUpdate(interaction.user.id,costMira)
            self.clear_items()
            await self.interaction.edit_original_response(embed= self.create_embed(0),view=self)
            if await checkHaveRole(interaction.user.id,1064945290500645045)==False:
                await addRole(interaction.user.id,1064945290500645045,days)
                await interaction.user.add_roles(interaction.guild.get_role(1064945290500645045))
            else:
                await updateRoleTime(interaction.user.id,1064945290500645045,days)
            self.stop()
        else:
            embed = self.create_embed(self.currentPage)
            embed.color=0xfa002a
            embed.add_field(name=":x: 購入失敗しました", value="<:mira:1120418935397961858> 不足", inline=False)
            await self.interaction.edit_original_response(embed=embed,view=self)
        

    @discord.ui.button(label=">>",style=discord.ButtonStyle.primary)
    async def nextButton(self,interaction:discord.Integration,button:discord.ui.Button):
        await interaction.response.defer()
        self.currentPage += 1
        await self.update_message(self.currentPage)
    
    async def on_timeout(self):
        self.clear_items()
        await self.interaction.edit_original_response(embed= self.create_embed(-10),view=self)

class Shop(Cog_Extension):
    @app_commands.command(name="shop",description="Show role shop menu")
    @app_commands.guild_only()
    async def shop(self,interaction:discord.Interaction):
        pagination_view = PaginationView(timeout=120)
        await pagination_view.send(interaction)

async def setup(bot):
    await bot.add_cog(Shop(bot))
