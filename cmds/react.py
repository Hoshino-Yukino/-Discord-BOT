import discord
from discord.ext import commands
from core.classes import Cog_Extension

class ReAct(Cog_Extension):
    @commands.Cog.listener() #新成员反应获得メンバー身份
    async def on_raw_reaction_add(self,data):
        if data.user_id == 983983161543376947:
            return
        guild = self.bot.get_guild(data.guild_id)
        role = guild.get_role(1036281244356452393)
        channal = guild.get_channel(982274193477492797)
        message = channal.get_partial_message(983981442679840840)
        if (data.channel_id == 982274193477492797)and(data.message_id == 983981442679840840)and (data.member.top_role.is_default() == True):
            await data.member.add_roles(role)
        await message.remove_reaction(data.emoji,data.member)

    @commands.command() #给rule添加反应
    async def rec(self,ctx):
        if str(ctx.author.id) == '910371227372245002':
            guild = ctx.guild
            print("in")
            channal = guild.get_channel(982274193477492797)
            message:discord.Message = channal.get_partial_message(983981442679840840)
            await message.add_reaction(self.bot.get_emoji(1138790905797689415))

async def setup(bot):
    await bot.add_cog(ReAct(bot))