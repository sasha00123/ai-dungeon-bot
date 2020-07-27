from ai_dungeon.storage.user_info import get_user_info
from ai_dungeon.translations.yandex import translate
from kutana import Plugin, Message

plugin = Plugin(name="Actions")


@plugin.on_any_unprocessed_message()
async def _(message: Message, ctx):
    user_info = await get_user_info(ctx)
    await ctx.reply(
        (await translate("Бот не знает, как обработать ваше сообщение! Попробуйте использовать одну из команд: ", "ru",
                         user_info.language)) +
        "\n/say <text>, \n/do <text>, \n/story <text>\n" +
        (await translate("Или перезапустить игру при помощи команды ", "ru", user_info.language)) + "/start")
