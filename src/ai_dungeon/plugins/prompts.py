import asyncio

from ai_dungeon.ai_dungeon_api.main import create_account, retrieve_scenario, get_adventure_info, \
    create_adventure_from_scenario
from ai_dungeon.storage.user_info import get_user_info, store_user_info
from ai_dungeon.translations.yandex import translate
from kutana import Plugin, Message, Context

plugin = Plugin(name="Scenarios")


def get_options_message(scenario: dict):
    """
    Helps to generate options message.
    Might change to buttons later.
    :param scenario: dict containing prompt and options with titles and ids
    :return: Text with available options
    """
    return scenario['prompt'] + '\n' + '\n'.join(
        [f"{i}. {option['title']}" for i, option in enumerate(scenario['options'], start=1)])


async def process_scenario(ctx, scenario: dict):
    """

    :param ctx: Request context
    :param scenario: dict containing prompt and options with titles and ids
    """
    user_info = await get_user_info(ctx)
    scenario['prompt'] = scenario['prompt'].replace("${character.name}", user_info.name)

    if scenario['options']:
        # Again prompt
        user_info.options = scenario['options']
        await asyncio.wait((store_user_info(ctx, user_info),
                            ctx.set_state(user_state='prompt'),
                            ctx.reply(await translate(get_options_message(scenario), "en", user_info.language))))
    else:
        # Start game
        user_info.options = None
        user_info.prompt = scenario['prompt']

        await ctx.reply((await translate("Создание игры... Для взаимодействия с ботом используйте команды: ", "ru",
                                         user_info.language)) +
                        "\n/say <text>, \n/do <text>, \n/story <text>\n/cancel - " + (
                            await translate("Закончить игру", "ru", user_info.language)))

        aid = await create_adventure_from_scenario(user_info, scenario['id'])
        adventure = await get_adventure_info(user_info, aid)

        user_info.adventure = adventure['id']
        await store_user_info(ctx, user_info)

        from ai_dungeon.plugins.action import process_actions
        await process_actions(ctx, adventure)


@plugin.on_commands(["play"], user_state='ready')
async def _(msg: Message, ctx: Context):
    """
    Asks user for his nickname
    """
    user_info = await get_user_info(ctx)
    await asyncio.wait((ctx.set_state(user_state='name'),
                        ctx.reply(await translate("Введите своё имя", "ru", user_info.language))))


@plugin.on_any_message(user_state='name')
async def _(msg: Message, ctx: Context):
    """
    Stores name and starts initial scenario
    """
    user_info = await get_user_info(ctx)
    user_info.name = msg.text
    await store_user_info(ctx, user_info)

    scenario = await retrieve_scenario(user_info)
    await process_scenario(ctx, scenario)


@plugin.on_match(pattern=r'^\d+$', user_state='prompt')
async def _(msg: Message, ctx: Context):
    """
    Selected options from enumerated options list.
    """
    user_info = await get_user_info(ctx)
    option_num = int(msg.text)
    if option_num > len(user_info.options) or option_num < 1:
        await ctx.reply(await translate("Неверный выбор!", "ru", user_info.language))
        return
    sid = user_info.options[option_num - 1]['id']
    scenario = await retrieve_scenario(user_info, sid)
    await process_scenario(ctx, scenario)
