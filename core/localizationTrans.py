import json
import traceback
import discord
from discord import app_commands


with open('./i18n.json','r',encoding='utf8') as transFile:
    transData = json.load(transFile)

class LocaleTranslator(app_commands.Translator):
    async def load(self):
        print("Translator Load OK")
    async def translate(self, string: app_commands.locale_str, locale: discord.Locale, context: app_commands.TranslationContext):
        """
        `locale_str` is the string that is requesting to be translated
        `locale` is the target language to translate to
        `context` is the origin of this string, eg TranslationContext.command_name, etc
        This function must return a string (that's been translated), or `None` to signal no available translation available, and will default to the original.
        """
        try:
            if locale==discord.Locale.american_english or locale==discord.Locale.british_english:
                returnMessage = transData[string.message]["en"]
            elif locale==discord.Locale.chinese:
                returnMessage = transData[string.message]["zh_CN"]
            elif locale==discord.Locale.japanese:
                returnMessage = transData[string.message]["ja"]
            else:
                returnMessage = transData[string.message]["en"]
        except:
            returnMessage = string.message
        return returnMessage
            