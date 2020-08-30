import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.backend_cache import BackendCache
from cellxgene_gateway.cache_entry import CacheEntry


class TestPruneProcessCache(unittest.TestCase):
    @patch("cellxgene_gateway.util.current_time_stamp", new=lambda: 0)
    @patch("cellxgene_gateway.env.ttl", new="10")
    @patch("cellxgene_gateway.cache_entry.CacheEntry")
    @patch("cellxgene_gateway.cache_entry.CacheEntry")
    def test_GIVEN_one_old_one_new_THEN_prune_old(self, old, new):
        from cellxgene_gateway.prune_process_cache import PruneProcessCache

        cache = BackendCache()
        old.timestamp = -100
        cache.entry_list.append(old)
        new.timestamp = -5
        cache.entry_list.append(new)
        self.assertEqual(len(cache.entry_list), 2)
        ppc = PruneProcessCache(cache)
        ppc.prune()
        self.assertEqual(len(cache.entry_list), 1)
        self.assertEqual(cache.entry_list[0], new)


if __name__ == "__main__":
    unittest.main()
