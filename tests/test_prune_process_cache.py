import unittest
from unittest.mock import patch, seal

from cellxgene_gateway.backend_cache import BackendCache
from cellxgene_gateway.cache_key import CacheKey
from cellxgene_gateway.items.file.fileitem import FileItem
from cellxgene_gateway.items.file.fileitem_source import FileItemSource
from cellxgene_gateway.items.item import ItemType

key = CacheKey(
    FileItem("/czi/", name="pbmc3k.h5ad", type=ItemType.h5ad),
    FileItemSource("/tmp", "local"),
)


class TestPruneProcessCache(unittest.TestCase):
    @patch("cellxgene_gateway.util.current_time_stamp", new=lambda: 0)
    @patch("cellxgene_gateway.env.ttl", new="10")
    @patch("cellxgene_gateway.cache_entry.CacheEntry")
    @patch("cellxgene_gateway.cache_entry.CacheEntry")
    def test_GIVEN_one_old_one_new_THEN_prune_old(self, old, new):
        from cellxgene_gateway.prune_process_cache import PruneProcessCache

        cache = BackendCache()
        old.timestamp = -100
        old.foo = 12
        old.pid = 1
        old.key = key
        old.terminate.return_value = None
        seal(old)
        new.key = key
        cache.entry_list.append(old)
        new.timestamp = -5
        seal(new)
        cache.entry_list.append(new)
        self.assertEqual(len(cache.entry_list), 2)
        ppc = PruneProcessCache(cache)
        ppc.prune()
        self.assertEqual(len(cache.entry_list), 1)
        self.assertEqual(cache.entry_list[0], new)
        self.assertEqual(cache.entry_list[0], new)
        self.assertTrue(old.terminate.called)


if __name__ == "__main__":
    unittest.main()
