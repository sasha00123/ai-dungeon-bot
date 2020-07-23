from ai_dungeon.storage.user_info import get_user_info, store_user_info
from kutana import Plugin, Message
from ai_dungeon.translations.yandex import *

plugin = Plugin(name='Language')


@plugin.on_any_message(user_state='language')
async def _(msg: Message, ctx):
    """
    Detects and stores user language. Moves to ready state
    """
    user_info = await get_user_info(ctx)
    lang = await detect_language(msg.text)
    user_info.language = lang
    await store_user_info(ctx, user_info)

    await ctx.set_state(user_state='ready')
    await ctx.reply(await translate(f"Выбран язык: {lang}", "ru", user_info.language))
    await ctx.reply(await translate(f"Чтобы начать игру, отправь: ", "ru", user_info.language) + "/play")
