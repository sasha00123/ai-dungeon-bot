import asyncio

from ai_dungeon.ai_dungeon_api.main import create_account
from ai_dungeon.storage.user_info import store_user_info, get_user_info, UserInfo
from ai_dungeon.translations.yandex import *
from kutana import Plugin, Message, Context

plugin = Plugin(name="Start")


@plugin.on_commands(["start"])
async def _(msg: Message, ctx: Context):
    """
    Creates anonymous account.
    Asks user to choose language using most popular languages.
    Changes state to 'language'.
    """
    user_info = (await get_user_info(ctx)) or UserInfo()

    token = await create_account()
    user_info.token = token
    await store_user_info(ctx, user_info)

    await ctx.set_state(user_state='language')
    translations = [
        await translate("Введите любое слово или предложение на своем родном языке.", "ru", language)
        for language in ['en', 'ru', 'es', 'zh', 'fr', 'de']
    ]
    await ctx.reply('\n\n'.join(translations))
