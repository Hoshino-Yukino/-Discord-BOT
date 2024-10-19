import discord
from discord import app_commands
from core.classes import Cog_Extension
from function.jrrp import *
from function.eco import *


class HelpMenuJP(discord.ui.View):
    currentPage:int = 1

    async def send(self,interaction:discord.Interaction):
        self.interaction:discord.Interaction = interaction
        await interaction.response.send_message(embed = self.create_embed(self.currentPage),view=self,ephemeral=True)

    def create_embed(self,page:int):
        if page == -10:
            embed=discord.Embed(title=" ヘルプ オフ", description="コマンドリストを再度知りたい場合は、`/help` を再度使用してください。", color=0xfa002a)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1032688154429378650/1039103241121701958/kuma.jpg")
            return embed
        
        if page == 9:
            embed=discord.Embed(title="ヘルプ Page9: System Command", color=0x70b0ff)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/850081111241785425.gif")
            embed.add_field(name="/help ", value="ヘルプメニューを表示する", inline=False)
            embed.add_field(name="/ping ", value="PING PONG", inline=False)

        elif page == 1:
            embed=discord.Embed(title="ヘルプ Page1: Amusing Command", color=0x70b0ff)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/850081111241785425.gif")
            embed.add_field(name="/jrrp ", value="今のRPを引く", inline=False)
            embed.add_field(name="/aidraw ", value="AI描画、詳細なパラメータはコマンド内のパラメータ説明を参照してください。", inline=False)
            embed.add_field(name="/来张色图", value="PIXIVからSETUをゲット ~", inline=False)
            embed.add_field(name="/soutu", value="写真付きのコマンドを送信して画像を逆検索します", inline=False)
            embed.add_field(name="フォト検索「Context Menu by message」", value="写真付きのメッセージの画像を逆検索します\n使用方法:\n • 逆検索したい写真付きのメッセージを右クリックします\n • アプリ\n • フォト検索", inline=False)
            

        elif page == 2:
            embed=discord.Embed(title="ヘルプ Page2: Economy Command", color=0x70b0ff)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1032688154429378650/1039103241121701958/kuma.jpg")
            embed.add_field(name="/property ", value="自分の財産を見せて", inline=False)
            embed.add_field(name="/shop ", value="ロールショップメニューを表示", inline=False)
            embed.add_field(name="ヒント: ", value="JRRP と CountingGame は MIRA を獲得できます", inline=False)
        
        elif page == 3:
            embed=discord.Embed(title="ヘルプ Page3: Economy Command 「ギャンブル」", color=0x70b0ff)
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1032688154429378650/1039103241121701958/kuma.jpg")
            embed.add_field(name="/exchange ", value="ミラをチップに交換、またはチップをミラに交換", inline=False)
            embed.add_field(name="/blackjack ", value="ブラックジャックのゲームをプレイする", inline=False)
            embed.add_field(name="/roulette ", value="ルーレットのゲームをする", inline=False)
            embed.add_field(name="/cockfight ", value="闘鶏に賭けます \nまずチキンを買う必要があります", inline=False)
            embed.add_field(name="/item buy chicken ", value="闘鶏をする前に鶏を買う必要がある", inline=False)
            embed.set_footer(text="Powered by UnbelievaBoat")


        elif page == 4:
            embed=discord.Embed(title="ヘルプ Page4: Music Command", color=0x70b0ff)
            embed.set_thumbnail(url="https://camo.githubusercontent.com/13a38b4fe8c6fdcac948830af73f55b1f675f408f37db6768e79de839b4d5320/68747470733a2f2f692e696d6775722e636f6d2f7a7245383048592e706e67")
            embed.add_field(name="!play [URL/query]", value="特定の URL からオーディオを再生するか、YouTube でクエリを検索し、最初の結果をキューに入れます", inline=False)
            embed.add_field(name="!queue", value="キューに入れられているすべてのメディアを表示します", inline=False)
            embed.add_field(name="!np", value="現在再生中のメディアを表示します", inline=False)
            embed.add_field(name="!skip", value="現在のメディアをスキップするために投票する", inline=False)
            embed.add_field(name="!search [service] [#] [query]", value="特定のサービス (デフォルト: YT) でクエリを検索し、最初のいくつかの結果を返します。その後、ユーザーはキューに追加したい場合に結果から選択できます。", inline=False)
            embed.add_field(name="*自動プレイリストについて", value="自動プレイリストに曲を追加したい場合は、DM Modmail でください。", inline=False)

        elif page == 5:
            embed=discord.Embed(title="ヘルプ Page5: Music Command「ONLY FOR DJ ROLE」", color=0x70b0ff)
            embed.set_thumbnail(url="https://camo.githubusercontent.com/13a38b4fe8c6fdcac948830af73f55b1f675f408f37db6768e79de839b4d5320/68747470733a2f2f692e696d6775722e636f6d2f7a7245383048592e706e67")
            embed.add_field(name="!summon", value="ボットを現在あなたの音声チャネルに接続します", inline=False)
            embed.add_field(name="!skip f", value="投票せずに即座にスキップします", inline=False)
            embed.add_field(name="!shuffle", value="キューをシャッフルします", inline=False)

        elif page == 6:
            embed=discord.Embed(title="ヘルプ Page6: Party-Chat Command「ONLY FOR PARTY CREATOR」", color=0x70b0ff)
            embed.set_thumbnail(url="https://cdn-longterm.mee6.xyz/plugins/embeds/images/283779835883683841/b1a18fffd5e1e92c49b83d1e4e938d4263a9d5f3798f1aff059aea1894ede216.png")
            embed.add_field(name="/party limit", value="チャネルで許可されるユーザー数を現在のユーザー数または指定された数に制限します", inline=False)
            embed.add_field(name="/party unlimit", value="チャンネルのユーザー制限を削除します", inline=False)
            embed.add_field(name="/party private", value="音声チャンネルを非公開にして、誰もあなたに直接参加できないようにします", inline=False)
            embed.add_field(name="/party public", value="プライベート チャンネルを再度公開して、誰でも参加できるようにします", inline=False)
            embed.add_field(name="/party kick", value="ユーザーをチャンネルから削除し、再度参加できないようにします", inline=False)
            embed.add_field(name="/party name", value="参加しているチャンネルの名前を直接変更する", inline=False)
            embed.add_field(name="/party transfer", value="チャンネルの所有権をチャンネル内の他のユーザーに譲渡し、そのユーザーが作成者である必要があるコマンドを使用できるようにします", inline=False)
            embed.add_field(name="/party close", value="直ちにパーティーを閉じてください", inline=False)
        
        elif page == 7:
            embed=discord.Embed(title="ヘルプ Page7: Nintendo Friend Code Command", color=0x70b0ff)
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/3/38/Nintendo_switch_logo.png")
            embed.add_field(name="/friend-code set", value="任天堂フレンドコードを登録する", inline=False)
            embed.add_field(name="/friend-code get", value="任天堂フレンドコードを表示・検索", inline=False)
            embed.add_field(name="/friend-code delete", value="任天堂フレンドコードを削除", inline=False)
            embed.add_field(name="Get Nintendo Friend Code「Context Menu by user」", value="選択したユーザーの任天堂フレンドコードを表示・検索\n使用方法:\n • 検索したいユーザーを右クリックします\n • アプリ\n • Get Nintendo Friend Code", inline=False)
        
        elif page == 8:
            embed=discord.Embed(title="ヘルプ Page8: ChatGPT Command", color=0x70b0ff)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1122836104874311734.webp?size=56&quality=high")
            embed.add_field(name="/gpt new", value="ChatGPT で新しい会話を開始する", inline=False)
            embed.add_field(name="/gpt chat", value="ChatGPT で前の会話を続ける", inline=False)
            embed.add_field(name="/gpt 翻訳設定",value="翻訳したい言語を設定します。デフォルトは中国語です",inline=False)
            embed.add_field(name="翻訳「Context Menu by message」",value="選択したテキストメッセージを翻訳します\n使用方法:\n • 翻訳したいテキストメッセージを右クリックします\n • アプリ\n • 翻訳")
            embed.set_footer(text="Powered by CattoGPT")
        return embed
    
    async def update_message(self,currentPage):
        await self.update_buttons()
        await self.interaction.edit_original_response(embed=self.create_embed(currentPage),view=self)
    
    async def update_buttons(self):
        if self.currentPage == 1:
            self.firstButton.disabled  = True
            self.lastButton.disabled = False
            self.backButton.disabled = True
            self.nextButton.disabled = False
            self.firstButton.style = discord.ButtonStyle.gray
            self.backButton.style = discord.ButtonStyle.gray
            self.lastButton.style = discord.ButtonStyle.green
            self.nextButton.style = discord.ButtonStyle.primary

        elif self.currentPage == 9:
            self.firstButton.disabled = False
            self.backButton.disabled = False
            self.lastButton.disabled = True
            self.nextButton.disabled = True
            self.firstButton.style = discord.ButtonStyle.green
            self.lastButton.style = discord.ButtonStyle.gray
            self.nextButton.style = discord.ButtonStyle.gray
            self.backButton.style = discord.ButtonStyle.primary
        else:
            self.firstButton.disabled = False
            self.lastButton.disabled = False
            self.nextButton.disabled = False
            self.backButton.disabled = False
            self.firstButton.style = discord.ButtonStyle.green
            self.lastButton.style = discord.ButtonStyle.green
            self.nextButton.style = discord.ButtonStyle.primary
            self.backButton.style = discord.ButtonStyle.primary

    @discord.ui.button(label="|<<",style=discord.ButtonStyle.grey,disabled=True)
    async def firstButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.currentPage=1
        await self.update_message(self.currentPage)

    @discord.ui.button(label="<<",style=discord.ButtonStyle.grey,disabled=True)
    async def backButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.currentPage -= 1
        await self.update_message(self.currentPage)

    @discord.ui.button(label="EXIT",style=discord.ButtonStyle.danger)
    async def cancleButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        self.clear_items()
        await self.interaction.edit_original_response(embed= self.create_embed(-10),view=self)
        self.stop()
    
    @discord.ui.button(label=">>",style=discord.ButtonStyle.primary)
    async def nextButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.currentPage += 1
        await self.update_message(self.currentPage)

    @discord.ui.button(label=">>|",style=discord.ButtonStyle.green)
    async def lastButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer()
        self.currentPage=6
        await self.update_message(self.currentPage)

    @discord.ui.select(
            placeholder="Select one page",
            options=[
                discord.SelectOption(label="Page1: Amusing Command",value="1"),
                discord.SelectOption(label="Page2: Economy Command",value="2"),
                discord.SelectOption(label="Page2: Economy Command「Gamble」",value="3"),
                discord.SelectOption(label="Page4: Music Command",value="4"),
                discord.SelectOption(label="Page5: Music Command(ONLY DJ ROLE)",value="5"),
                discord.SelectOption(label="Page6: Party-Chat Command",value="6"),
                discord.SelectOption(label="Page7: Nintendo Friend Code Command",value="7"),
                discord.SelectOption(label="Page8: ChatGPT Command",value="8"),
                discord.SelectOption(label="Page9: System Command",value="9"),
            ],
            min_values=1,
            max_values=1
    )
    async def selectCallBack(self,interaction:discord.Interaction,select:discord.ui.Select):
        await interaction.response.defer()
        page = int(select.values[0])
        self.currentPage = page
        await self.update_message(page)


    async def on_timeout(self):
        self.clear_items()
        await self.interaction.edit_original_response(embed= self.create_embed(-10),view=self)

class Help(Cog_Extension):
    @app_commands.command(name="help",description="Open all cmds menu")
    @app_commands.choices(language=[
        discord.app_commands.Choice(name="Japanese",value="Japanese"),
        discord.app_commands.Choice(name="Chinese",value="Chinese"),
        discord.app_commands.Choice(name="English",value="English"),
    ])
    async def shop(self,interaction:discord.Interaction,language:discord.app_commands.Choice[str]):
        pagination_view = HelpMenuJP(timeout=120)
        await pagination_view.send(interaction)

async def setup(bot):
    await bot.add_cog(Help(bot))