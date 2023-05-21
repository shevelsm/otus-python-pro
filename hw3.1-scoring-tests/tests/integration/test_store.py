import unittest
from unittest.mock import MagicMock

from store import RedisAsStorage 


class TestStore(unittest.TestCase):
    def setUp(self):
        self.store = RedisAsStorage()
        self.key = "key"
        self.value = "value"

    def test_store_connected(self):
        self.assertTrue(self.store.set(self.key, self.value))
        self.assertEqual(self.store.get(self.key), self.value)

    def test_store_disconnected(self):
        self.store.get = MagicMock(side_effect=ConnectionError())
        self.assertRaises(ConnectionError, self.store.get, self.key)
