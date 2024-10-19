import discord
from discord import app_commands
from discord.ext import commands
import re
import traceback
from function.nintendofc import *

class NintendoFriendCode(commands.Cog):
    def __init__(self,bot):
        self.bot:commands.Bot = bot
        self.getNFCode = app_commands.ContextMenu(
            name="Get Nintendo Friend Code",
            callback=self.getNFC,
        )
        self.bot.tree.add_command(self.getNFCode)

    class NFCGroup(app_commands.Group):
        ...
    nfcGroup = NFCGroup(name="friend-code",description="Group for Nintendo Friend Code.")

    @nfcGroup.command(description="任天堂フレンドコードを登録する")
    async def set(self,interaction:discord.Interaction):
        try:
            setNFCModal = SetNFCModal(title="Set Nintendo Friend Code",timeout=300)
            await interaction.response.send_modal(setNFCModal)
        except:
            traceback.print_exc()

    @nfcGroup.command(description="任天堂フレンドコードを表示")
    async def get(self,interaction:discord.Interaction,user:discord.User):
        if await nfcIsInit(user.id):
            await interaction.response.send_message(f"{user.mention} の任天堂フレンドコードは `{await getNfc(user.id)}`",ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.mention} は任天堂フレンドコードを登録していないみたいだ!",ephemeral=True)

    @nfcGroup.command(description="任天堂フレンドコードを削除")
    async def delete(self,interaction:discord.Interaction):
        if await nfcIsInit(interaction.user.id):
            await delnfc(interaction.user.id)
            await interaction.response.send_message(f"{interaction.user.mention} の任天堂フレンドコードの設定を削除しました!",ephemeral=True)
        else:
            await interaction.response.send_message(f"{interaction.user.mention} は任天堂フレンドコードを登録していないみたいだ!",ephemeral=True)

    async def getNFC(self,interaction:discord.Interaction,user:discord.User):
        if await nfcIsInit(user.id):
            await interaction.response.send_message(f"{user.mention} の任天堂フレンドコードは `{await getNfc(user.id)}`",ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.mention} は任天堂フレンドコードを登録していないみたいだ!",ephemeral=True)
        

class SetNFCModal(discord.ui.Modal):
    user:discord.User
    nfcValue = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Code",
        required=True,
        placeholder="SW-****-****-****"
    )
    async def on_submit(self, interaction: discord.Interaction):
        try:
            nfcRule=re.compile('SW-[0-9]{4}-[0-9]{4}-[0-9]{4}')
            if (re.match(nfcRule,self.nfcValue.value)==None):
                await interaction.response.send_message(f"フレンドコードを正しく入力してください!",ephemeral=True)
                return
            if await nfcIsInit(interaction.user.id):
                await nfcUpdate(interaction.user.id,self.nfcValue.value)
            else:
                await nfcInit(interaction.user.id,self.nfcValue.value)
            await interaction.response.send_message(f"任天堂フレンドコードを `{self.nfcValue.value}` で登録したぞ!",ephemeral=True)
        except:
            traceback.print_exc()


async def setup(bot):
    await bot.add_cog(NintendoFriendCode(bot))
