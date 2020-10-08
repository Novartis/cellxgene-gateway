import unittest
from cellxgene_gateway.cache_entry import CacheEntry, CacheEntryStatus
from cellxgene_gateway.cache_key import CacheKey
from cellxgene_gateway.items.item import ItemType
from cellxgene_gateway.items.file.fileitem import FileItem
from cellxgene_gateway.items.file.fileitem_source import FileItemSource

key = CacheKey(
    FileItem("/czi/", "pbmc3k.h5ad", ItemType.h5ad),
    FileItemSource("/tmp", "local"),
)


class TestRenderEntry(unittest.TestCase):
    def test_GIVEN_key_and_port_THEN_returns_loading_CacheEntry(self):
        entry = CacheEntry.for_key("some-key", 1)
        self.assertEqual(entry.status, CacheEntryStatus.loading)

    def test_GIVEN_absolute_static_url_THEN_include_path(self):
        actual = CacheEntry.for_key(key, 8000).rewrite_text_content(
            "src:url(/static/assets/"
        )
        expected = "src:url(http://localhost:5005/source/local/view/czi/pbmc3k.h5ad/static/assets/"
        self.assertEqual(actual, expected)

    def test_GIVEN_absolute_src_THEN_include_path(self):
        actual = CacheEntry.for_key(key, 8000).rewrite_text_content(
            '<link rel="shortcut icon" href="/static/assets/favicon.ico">'
        )
        expected = '<link rel="shortcut icon" href="http://localhost:5005/source/local/view/czi/pbmc3k.h5ad/static/assets/favicon.ico">'
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
