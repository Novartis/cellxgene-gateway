import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.cache_entry import CacheEntry, CacheEntryStatus


class TestCacheEntry(unittest.TestCase):
    def test_GIVEN_key_and_port_THEN_returns_loading_CacheEntry(self):
        entry = CacheEntry.for_key("some-key", 1)
        self.assertEqual(entry.status, CacheEntryStatus.loading)


if __name__ == "__main__":
    unittest.main()
