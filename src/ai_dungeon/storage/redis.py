import aioredis
from kutana.storage import Storage
import jsonpickle


class RedisStorage(Storage):
    def __init__(self, url):
        """
        :param url: Redis URL
        """
        self.url = url
        self._redis = None

    async def initiate(self):
        """
        Initializing connection to the database
        """
        self._redis = await aioredis.create_redis_pool(self.url)

    async def save(self, name, value):
        """
        Save key-value pair. Updates if already exists.
        :param name: Key to store
        :param value: Value to associate
        """
        await self._redis.set(name, jsonpickle.encode(value))

    async def load(self, name, default=None):
        """
        Loads key from the database
        :param name: Key of the element
        :param default: Value if Key is not stored in the database
        :return: Value associated with the key in the database if exists, default otherwise
        """
        return jsonpickle.decode((await self._redis.get(name)) or 'null') or default
