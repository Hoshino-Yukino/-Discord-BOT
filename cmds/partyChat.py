import discord
from discord.ext import commands,tasks
from discord import app_commands
from function.PartyChat import *
import traceback

class PartyChat(commands.Cog):
    
    def __init__(self,bot):
        self.bot:commands.Bot = bot
        self.deleteEmptyChannel.start()
        self.deleteLeaveRole.start()

    ### LOOP-TASKS ###
    @tasks.loop(seconds=2)
    async def deleteEmptyChannel(self):
        try:
            await self.bot.wait_until_ready()
            conn = sqlite3.connect('DiscordBot.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT VoiceChannelId,RoleId From PartyChat Where Status!=-1")
            result = cursor.fetchall()
            for i in range(0,len(result)):
                channel = self.bot.get_channel(result[i][0])
                if not channel.members:
                    for channelSet in channel.category.channels:
                        await channelSet.delete(reason="Empty Party Channel")
                    await channel.category.delete(reason="Empty Party Channel Category")
                    await channel.guild.get_role(result[i][1]).delete(reason="Empty Party Channel Role")
                    await delKickHis(result[i][0])
                    cursor.execute(f"DELETE FROM PartyChat WHERE VoiceChannelId={channel.id}")
                    conn.commit()
            cursor.close()
            conn.close()
        except:
            traceback.print_exc()

    @tasks.loop(seconds=2)
    async def deleteLeaveRole(self):
        try:
            await self.bot.wait_until_ready()
            conn = sqlite3.connect('DiscordBot.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT VoiceChannelId,RoleId,CreatorId From PartyChat")
            result = cursor.fetchall()
            for i in range(0,len(result)):
                VoiceChannelId = result[i][0]
                RoleId = result[i][1]
                role = self.bot.get_channel(VoiceChannelId).guild.get_role(RoleId)
                for roleMember in role.members:
                    if roleMember.id == result[i][2]:
                        continue
                    if not roleMember in self.bot.get_channel(VoiceChannelId).members:
                        await roleMember.remove_roles(role,reason="Leave Party Channel")
                        
            cursor.close()
            conn.close()
        except:
            pass
    
    ### LOOP-TASKS END ###
    
    @app_commands.guild_only()
    class PartyGroup(app_commands.Group):
        ...
    partyGroup = PartyGroup(name="party",description="Group for party chat cmds.")

    @partyGroup.command(description="「Party Creator ONLY」Make your party private, preventing anyone from joining you directly")
    async def private(self,interaction:discord.Interaction):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must use in PartyChat",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        VoiceChannelId = await getVoiceChannel(interaction.channel_id)
        if await checkPrivate(VoiceChannelId):
            await interaction.response.send_message(f'Your channel is already private. Use `/party public` to make it public again.')
            return
        await interaction.guild.get_channel(VoiceChannelId).set_permissions(interaction.guild.default_role,connect=False,reason="Set party private")
        temporaryApplyChannel = await interaction.channel.category.create_voice_channel(name=f"⇩ Apply to join")
        result = await getKickHis(VoiceChannelId)
        for i in range(0,len(result)):
            await temporaryApplyChannel.set_permissions(interaction.guild.get_member(result[i][0]),connect=False)
        await temporaryApplyChannel.move(beginning=True,category=interaction.channel.category,reason="Set party private")
        await toPrivateChannel(VoiceChannelId,temporaryApplyChannel.id)
        await interaction.response.send_message(f'Your channel is now private! \nA "⇩ Apply to join" channel will appear above your one shortly. When someone enters this channel to request to join you, I will send a message here asking you to approve or deny their request.')

    @partyGroup.command(description="「Party Creator ONLY」Make your private party public again, so anyone can join")
    async def public(self,interaction:discord.Interaction):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must use in PartyChat",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        VoiceChannelId = await getVoiceChannel(interaction.channel_id)
        if not await checkPrivate(VoiceChannelId):
            await interaction.response.send_message(f'Your channel is already public. Use `/party private` to make it private instead.')

        await interaction.guild.get_channel(VoiceChannelId).set_permissions(interaction.guild.default_role,connect=True,reason="Set party public")
        await interaction.guild.get_channel(await getApplyChannel(VoiceChannelId)).delete(reason="Set party public")
        await toPublicChannel(VoiceChannelId)
        await interaction.response.send_message(f'Your channel is now public!')

    @partyGroup.command(description="「Party Creator ONLY」Limit the number of users allowed in your channel")
    @app_commands.describe(limit_num="Only the number of users allowed in your channel")
    async def limit(self,interaction:discord.Interaction,limit_num:int):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must be used in PartyChat.",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        if limit_num<=0:
            await interaction.response.send_message("The limit_num must >0",ephemeral=True)
            return
        if limit_num>50:
            await interaction.response.send_message("The limit_num must <=50",ephemeral=True)
            return
        VoiceChannelId = await getVoiceChannel(interaction.channel_id)
        await interaction.guild.get_channel(VoiceChannelId).edit(user_limit=limit_num,reason="Edit party limit")
        await interaction.response.send_message(f'Your channel has been limited to {limit_num} people.')

    @partyGroup.command(description="「Party Creator ONLY」Remove the user limit in your channel")
    async def unlimit(self,interaction:discord.Interaction):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must be used in PartyChat.",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        VoiceChannelId = await getVoiceChannel(interaction.channel_id)
        await interaction.guild.get_channel(VoiceChannelId).edit(user_limit=0,reason="Edit party limit")
        await interaction.response.send_message(f'Your channel are unlimited')

    @partyGroup.command(description="「Party Creator ONLY」Remove a user from your channel and prevent them from joining again")
    @app_commands.describe(user="The user you want to remove")
    async def ban(self,interaction:discord.Interaction,user:discord.Member):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must be used in PartyChat.",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        if user.top_role.permissions.administrator==True:
            await interaction.response.send_message("You can't kick a Server Administrator.",ephemeral=True)
            return
        
        VoiceChannelId = await getVoiceChannel(interaction.channel_id)
        CreatorId = await getCreator(VoiceChannelId)
        if user not in interaction.guild.get_channel(VoiceChannelId).members:
            await interaction.response.send_message(f"Can't find any user in your channel with the name <@{user.id}>",ephemeral=True)
            return
        await addKickHis(VoiceChannelId,user.id)
        await user.move_to(None,reason=f"From {interaction.user.display_name} ban")
        await interaction.guild.get_channel(VoiceChannelId).set_permissions(user,connect=False,reason=f"From {interaction.user.display_name} ban")
        await interaction.response.send_message(f":bangbang: KICK :bangbang:\n<@{user.id}> was kicked from <@{CreatorId}>'s channel.")

    @partyGroup.command(description="「Party Creator ONLY」Edit bitrate of the party")
    @app_commands.describe(bitrate="Set a custom bitrate (in kbps) for PartyChat Default:64")
    async def bitrate(self,interaction:discord.Interaction,bitrate:int=64):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must be used in PartyChat.",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        if(bitrate<8 or bitrate>96):
            await interaction.response.send_message("Bitrate should be >=8kbps and <=96kpbs")
        VoiceChannelId = await getVoiceChannel(interaction.channel_id)
        await interaction.guild.get_channel(VoiceChannelId).edit(bitrate=(bitrate*1000),reason="Edit party bitrate")
        await interaction.response.send_message(f'Done! From now on, the PartyChat will have their bitrate set to {bitrate}kbps.')

    @partyGroup.command(description="「Party Creator ONLY」Directly change the name of the PartyChat")
    @app_commands.choices(
        select=[
            discord.app_commands.Choice(name="Category",value="Category"),
            discord.app_commands.Choice(name="VoiceChannel",value="VoiceChannel"),
            discord.app_commands.Choice(name="TextChannel",value="TextChannel")
        ])
    @app_commands.describe(select="The channel you want to change name",
                           channelname="The name of the channel you want to change Default: Creator's Area/Creator's Channel")
    async def name(self,interaction:discord.Interaction,select:discord.app_commands.Choice[str],channelname:str="NULL"):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must be used in PartyChat.",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        if select.value=="VoiceChannel":
            if channelname=="NULL":
                CreatorId = await getCreator(await getVoiceChannel(interaction.channel.id))
                Creator = interaction.guild.get_member(CreatorId)
                channelname=f"{Creator.name}'s Channel"
            VoiceChannelId = await getVoiceChannel(interaction.channel_id)
            await interaction.guild.get_channel(VoiceChannelId).edit(name=channelname,reason="Edit party name")
            await interaction.response.send_message(f'Done! VoiceChannel name has been set {channelname}')
        elif select.value=="Category":
            if channelname=="NULL":
                CreatorId = await getCreator(await getVoiceChannel(interaction.channel.id))
                Creator = interaction.guild.get_member(CreatorId)
                channelname=f"{Creator.name}'s Area"
            channelname = "「Party」" + channelname
            VoiceChannelId = await getVoiceChannel(interaction.channel_id)
            await interaction.guild.get_channel(VoiceChannelId).category.edit(name=channelname,reason="Edit party name")
            await interaction.response.send_message(f'Done! Category name has been set {channelname}')
        else:
            if channelname=="NULL":
                channelname=f"💬private-chat"
            TextChannelId = await getTextChannel(interaction.channel_id)
            await interaction.guild.get_channel(TextChannelId).edit(name=channelname,reason="Edit party name")
            await interaction.response.send_message(f'Done! TextChannel name has been set {channelname}')
    
    @partyGroup.command(description="「Party Creator ONLY」Transfer ownership of your channel to someone else in the channel")
    @app_commands.describe(user="The user you want to transfer ownership")
    async def transfer(self,interaction:discord.Interaction,user:discord.Member):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must be used in PartyChat.",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        VoiceChannelId = await getVoiceChannel(interaction.channel_id)
        if user not in interaction.guild.get_channel(VoiceChannelId).members:
            await interaction.response.send_message(f"Can't find any user in your channel with the name <@{user.id}>",ephemeral=True)
            return
        await trasferOwner(VoiceChannelId,user.id)
        await interaction.guild.get_channel(VoiceChannelId).category.edit(name=f"「Party」{user.name}'s Area",reason="Transfer the party creator")
        await interaction.guild.get_channel(VoiceChannelId).edit(name=f"{user.name}'s Channel",reason="Transfer the party creator")
        await interaction.response.send_message(f'Done! PartyChat OwenrShip has been set <@{user.id}>')
    
    @partyGroup.command(description="「Party Creator ONLY」Close the party immediately.")
    async def close(self,interaction:discord.Interaction):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must be used in PartyChat.",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        for members in interaction.channel.guild.get_channel(await getVoiceChannel(interaction.channel_id)).members:
            await members.move_to(channel=None,reason=f"Party close by {interaction.user.display_name}")
        try:
            await interaction.response.send_message(f'OK! The party will close shortly.')
        except:
            pass
        
    @partyGroup.command(description="「Party Creator ONLY」Allow someone join your party again")
    @app_commands.describe(user="The user you want to remove from ban list")
    async def unban(self,interaction:discord.Interaction,user:discord.Member):
        if not await isPartyChat(interaction.channel_id):
            await interaction.response.send_message("The cmd must be used in PartyChat.",ephemeral=True)
            return
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        if await isKicked(interaction.channel_id,user.id):
            await interaction.response.send_message(f"{user.display_name} never been kicked ",ephemeral=True)
            return
        
        VoiceChannelId = await getVoiceChannel(interaction.channel_id)
        await delOneKick(VoiceChannelId,user.id)
        await interaction.guild.get_channel(VoiceChannelId).set_permissions(user,connect=None,reason=f"From {interaction.user.display_name} unban")
        if not await isPublicPartyChannel(VoiceChannelId=VoiceChannelId):
            await interaction.guild.get_channel(await getApplyChannel(VoiceChannelId)).set_permissions(user,connect=None,reason=f"From {interaction.user.display_name} unban")
        await interaction.response.send_message(f":bangbang: OK :bangbang:\n<@{user.id}> can join the party again.")


    @commands.Cog.listener()
    async def on_voice_state_update(self,member:discord.Member,before:discord.VoiceState,after:discord.VoiceState):
        #UROBOROS PARTY CHAT MAIN CHANNEL:1039061803914764379
        if after.channel.id==1039061803914764379:
            temporaryCategory = await after.channel.guild.create_category(name=f"「Party」{member.display_name}'s Party")
            temporaryVoiceChannel = await temporaryCategory.create_voice_channel(name=f"{member.display_name}'s Channel")
            temporaryRole = await after.channel.guild.create_role(name=f"🎤🤖vc {temporaryVoiceChannel.id}")
            temporaryTextChannel = await temporaryCategory.create_text_channel(name="💬private-chat")
            await temporaryCategory.move(before=member.guild.get_channel(1039181862293213275).category)
            await member.move_to(temporaryVoiceChannel)
            await temporaryVoiceChannel.edit(user_limit=5)
            await member.add_roles(temporaryRole)
            await temporaryTextChannel.edit(topic=f":eye: This channel is only visible to members who join your voice channel once, and admins of this server. It will be deleted when everyone leaves. VC ID: {temporaryVoiceChannel.id}")
            await temporaryTextChannel.edit(nsfw=True)
            await temporaryVoiceChannel.set_permissions(temporaryRole,connect=True)
            await temporaryVoiceChannel.set_permissions(temporaryRole,connect=True)
            await temporaryTextChannel.set_permissions(temporaryRole,view_channel=True)
            await temporaryTextChannel.set_permissions(member.guild.default_role,view_channel=False)
            await createParty(VoiceChannelId=temporaryVoiceChannel.id,TextChannelId=temporaryTextChannel.id,CategoryId=temporaryCategory.id,CreatorId=member.id,RoleId=temporaryRole.id)
            return

        if await isPublicPartyChannel(after.channel.id):
            await member.add_roles(member.guild.get_role(await getRoleId(VoiceChannelId=after.channel.id)))
            return
        
        if await isApplyChannel(after.channel.id):
            try:
                VoiceChannelId = await getVoiceChannel(after.channel.id)
                TextChannelId = await getTextChannel(VoiceChannelId)
                apply_view = PartyApply(timeout=120)
                await apply_view.send(member=member,voiceChannelId=VoiceChannelId,textChannelId=TextChannelId,applyChannelId=after.channel.id)
            except:
                traceback.print_exc()
        
        if await isPublicPartyChannel(before.channel.id):
            await member.remove_roles(member.guild.get_role(await getRoleId(VoiceChannelId=before.channel.id)))
            if len(before.channel.members)==0:
                for channel in before.channel.category.channels:
                    await channel.delete()
                await before.channel.category.delete()
                await member.guild.get_role(await getRoleId(VoiceChannelId=before.channel.id)).delete()
                await deleteParty(VoiceChannelId=before.channel.id)
            return

class PartyApply(discord.ui.View):
    user:discord.Member=None
    voiceChannelId:int=0
    applyChannelId:int=0
    applyMessage:discord.Message
    async def send(self,member:discord.Member,voiceChannelId,textChannelId:int,applyChannelId:int):
        self.user = member
        self.voiceChannelId=voiceChannelId
        self.applyChannelId=applyChannelId
        content = f"Hey <@{await getCreator(voiceChannelId)}>,\n<@{member.id}>would like to join your private voice channel.\n• ✅ to allow.\n• ❌ to deny this time.\n• ⛔ to deny and block future requests from them."
        self.applyMessage = await member.guild.get_channel(textChannelId).send(content=content,view=self)

    @discord.ui.button(emoji="✅",style=discord.ButtonStyle.green)
    async def allowButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        try:
            await self.user.move_to(self.user.guild.get_channel(self.voiceChannelId),reason="Private party pass the audit")
            await self.applyMessage.edit(view=None)
            await self.applyMessage.delete(delay=30)
            return
        except:
            traceback.print_exc()
    @discord.ui.button(emoji="❌",style=discord.ButtonStyle.gray)
    async def denyButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        await self.user.move_to(channel=None,reason="Private party deny the audit")
        await self.applyMessage.edit(view=None)
        await self.applyMessage.delete(delay=30)
        return
    @discord.ui.button(emoji="⛔",style=discord.ButtonStyle.danger)
    async def blockButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        if not (await isPartyCreator(interaction.channel_id,interaction.user.id) or interaction.user.top_role.permissions.administrator==True):
            await interaction.response.send_message("You have no Permission to do that.",ephemeral=True)
            return
        try:
            await self.user.guild.get_channel(self.applyChannelId).set_permissions(self.user,connect=False)
            await self.user.guild.get_channel(self.voiceChannelId).set_permissions(self.user,connect=False)
            await addKickHis(self.voiceChannelId,self.user.id)
            await self.user.move_to(channel=None)
            await self.applyMessage.edit(view=None)
            await self.applyMessage.delete(delay=30)
            return
        except:
            traceback.print_exc()

    async def on_timeout(self):
        await self.applyMessage.delete(delay=30)


async def setup(bot):
    await bot.add_cog(PartyChat(bot))