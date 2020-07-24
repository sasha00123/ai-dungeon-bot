from ai_dungeon.ai_dungeon_api.main import adventure_send_action
from ai_dungeon.storage.user_info import get_user_info, insert_action
from ai_dungeon.translations.yandex import translate
from kutana import Plugin, Message

plugin = Plugin(name="Actions")


async def process_actions(ctx, adventure):
    """
        Iterates over actions. Prints newly added actions. Saves to the app storage.
    """
    user_info = await get_user_info(ctx)
    new_actions = []
    for action in adventure['actions']:
        added = await insert_action(ctx, adventure, action)
        if added:
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

    adventure = await adventure_send_action(user_info, {
        'type': ctx.command,
        'text': await translate(ctx.body, user_info.language, "en"),
        'id': user_info.adventure
    })

    await process_actions(ctx, adventure)

    if adventure['died']:
        await ctx.set_state(user_state='ready')
        await ctx.reply((await translate("Game over. To start again, send: ", "en", user_info.language)) + "/play")


@plugin.on_commands(commands=['cancel'])
async def _(msg: Message, ctx):
    """
        Command to stop history.
    """
    user_info = await get_user_info(ctx)
    if ctx.user_state and ctx.user_state != 'language':
        await ctx.set_state(user_state='ready')
        await ctx.reply(await translate("Game over", "en", user_info.language))
