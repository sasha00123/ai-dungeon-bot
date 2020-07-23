from kutana import Plugin, Message, Kutana

plugin = Plugin(name="Initialize database")


@plugin.on_start()
async def _(app: Kutana):
    """
        Initializes storage when app is started
    """
    await app.storage.initiate()
