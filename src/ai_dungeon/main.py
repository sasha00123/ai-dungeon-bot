from ai_dungeon import config
from ai_dungeon.storage.redis import RedisStorage
from kutana import Kutana, load_plugins
from kutana.backends import Vkontakte, Telegram

import logging

logging.basicConfig(level=logging.DEBUG)

# Create application
if config.REDIS_URL is not None:
    app = Kutana(storage=RedisStorage(config.REDIS_URL))
else:
    app = Kutana()

# Add manager to application
if config.TELEGRAM_TOKEN:
    app.add_backend(Telegram(token=config.TELEGRAM_TOKEN))
if config.VK_TOKEN:
    app.add_backend(Vkontakte(token=config.VK_TOKEN))

# Load and register plugins
app.add_plugins(load_plugins("plugins/"))

if __name__ == "__main__":
    # Run application
    app.run()
