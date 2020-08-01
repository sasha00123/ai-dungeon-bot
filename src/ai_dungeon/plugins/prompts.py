import asyncio

from ai_dungeon.storage.user_info import get_user_info, store_user_info
from ai_dungeon.translations.yandex import translate
from aidungeonapi import AIDungeonClient, AIDungeonScenario, AIDungeonAdventure
from aidungeonapi.aidscenario import ScenarioIDS
from kutana import Plugin, Message, Context

plugin = Plugin(name="Scenarios")


def get_options_message(prompt: str, options: dict):
    """
    Helps to generate options message.
    Might change to buttons later.
    :param prompt: Scenario prompt
    :param options: Scenario options
    :return: Text with available options
    """
    return prompt + '\n' + '\n'.join(
        [f"{i}. {option['title']}" for i, option in enumerate(options, start=1)])


async def process_scenario(ctx, scenario: AIDungeonScenario):
    """

    :param ctx: Request context
    :param scenario: dict containing prompt and options with titles and ids
    """
    user_info = await get_user_info(ctx)
    prompt = (await scenario.obtain_prompt()).replace("${character.name}", user_info.name)

    if options := (await scenario.obtain_options()):
        # Again prompt
        user_info.options = options
        await asyncio.wait((store_user_info(ctx, user_info),
                            ctx.set_state(user_state='prompt'),
                            ctx.reply(await translate(get_options_message(prompt, options), "en", user_info.language))))
    else:
        # Start game
        user_info.options = None
        user_info.prompt = prompt

        await ctx.reply((await translate("Создание игры... Для взаимодействия с ботом используйте команды: ", "ru",
                                         user_info.language)) +
                        "\n/say <text>, \n/do <text>, \n/story <text>\n/cancel - " + (
                            await translate("Закончить игру", "ru", user_info.language)))

        client = await AIDungeonClient(token=user_info.token or '', debug=True)
        adventure_id = await client.create_adventure(scenario.id, user_info.prompt)

        adventure = await AIDungeonAdventure(client, id=adventure_id)

        user_info.adventure = adventure_id
        await store_user_info(ctx, user_info)

        from ai_dungeon.plugins.action import process_actions
        await process_actions(ctx, adventure_id, await adventure.obtain_actions())


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

    client = await AIDungeonClient(token=user_info.token or '', debug=True)
    scenario = await AIDungeonScenario(client, half_id="458612")

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
    client = await AIDungeonClient(token=user_info.token or '', debug=True)
    scenario = await AIDungeonScenario(client, id=sid)

    await process_scenario(ctx, scenario)
