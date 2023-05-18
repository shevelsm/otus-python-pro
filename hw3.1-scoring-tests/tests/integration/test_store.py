import unittest
from unittest.mock import MagicMock

from store import RedisAsStorage 


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = RedisAsStorage()
        self.key = "key"
        self.value = "value"

    def test_store_connected(self):
        self.assertTrue(self.store.storage.set(self.key, self.value))
        self.assertEqual(self.store.get(self.key), self.value)

    def test_store_disconnected(self):
        self.redis_storage.db.get = MagicMock(side_effect=ConnectionError())
        self.assertRaises(ConnectionError, self.store.get, self.key)


    def test_cache_connected(self):
        self.assertTrue(self.store.cache_set(self.key, self.value))
        self.assertEqual(self.store.cache_get(self.key), self.value)

    def test_cache_disconnected(self):
        self.redis_storage.db.get = MagicMock(side_effect=ConnectionError())
        self.redis_storage.db.set = MagicMock(side_effect=ConnectionError())

        self.assertEqual(self.store.cache_get(self.key), None)
        self.assertEqual(self.store.cache_set(self.key, self.value), None)
