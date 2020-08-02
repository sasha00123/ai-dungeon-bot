from ai_dungeon.storage.user_info import get_user_info, insert_action
from ai_dungeon.translations.yandex import translate
from aidungeonapi import AIDungeonClient, AIDungeonAdventure
from kutana import Plugin, Message

plugin = Plugin(name="Actions")


async def process_actions(ctx, adventure_id, actions, skip_read=True):
    """
        Iterates over actions. Prints newly added actions. Saves to the app storage.
    """
    user_info = await get_user_info(ctx)
    new_actions = []
    for action in actions:
        added = await insert_action(ctx, adventure_id, action)
        if added or not skip_read:
            new_actions.append(action)
    text = ''.join([action['text'] for action in new_actions])
    if text:
        await ctx.reply(await translate(text, "en", user_info.language))
    await ctx.set_state(user_state='game')


@plugin.on_commands(commands=['do', 'say', 'story'], user_state='game')
async def _(msg: Message, ctx):
    """
        Handles /do, /say and /story.
        If died, returns to 'ready' state.
    """
    user_info = await get_user_info(ctx)

    client = await AIDungeonClient(token=user_info.token or '', debug=True)
    adventure = await AIDungeonAdventure(client, id=user_info.adventure)

    await adventure.send_text(await translate(ctx.body, user_info.language, "en"), ctx.command)

    await process_actions(ctx, adventure.id, await adventure.obtain_actions())

    if await adventure.obtain_has_died():
        await ctx.set_state(user_state='ready')
        await ctx.reply((await translate("Game over. To start again, send: ", "en", user_info.language)) + "/play")


@plugin.on_commands(commands=['cancel'])
async def _(msg: Message, ctx):
    """
        Command to stop history.
    """
    user_info = await get_user_info(ctx)
    # Avoid skipping language entry
    if ctx.user_state and ctx.user_state != 'language':
        await ctx.set_state(user_state='ready')
        await ctx.reply(await translate("Game over", "en", user_info.language))


@plugin.on_any_unprocessed_message(user_state='game')
async def _(message: Message, ctx):
    user_info = await get_user_info(ctx)
    await ctx.reply(
        (await translate("Бот не знает, как обработать ваше сообщение! Попробуйте использовать одну из команд: ", "ru",
                         user_info.language)) +
        "\n/say <text>, \n/do <text>, \n/story <text>\n" +
        (await translate("Или перезапустить игру при помощи команды ", "ru", user_info.language)) + "/start")


@plugin.on_commands(commands=['undo', 'redo', 'retry'], user_state='game')
async def _(message: Message, ctx):
    user_info = await get_user_info(ctx)

    client = await AIDungeonClient(token=user_info.token or '', debug=True)
    adventure = await AIDungeonAdventure(client, id=user_info.adventure)

    await adventure.send_simple_action(ctx.command)

    await ctx.reply(await translate((await adventure.obtain_last_action())['text'], "en", user_info.language))


@plugin.on_commands(commands=['full_story'], user_state='game')
async def _(message: Message, ctx):
    user_info = await get_user_info(ctx)

    client = await AIDungeonClient(token=user_info.token or '', debug=True)
    adventure = await AIDungeonAdventure(client, id=user_info.adventure)

    await process_actions(ctx, adventure.id, await adventure.obtain_actions(), skip_read=False)


@plugin.on_commands(commands=['last'], user_state='game')
async def _(message: Message, ctx):
    user_info = await get_user_info(ctx)

    client = await AIDungeonClient(token=user_info.token or '', debug=True)
    adventure = await AIDungeonAdventure(client, id=user_info.adventure)

    await ctx.reply(await translate((await adventure.obtain_last_action())['text'], "en", user_info.language))
