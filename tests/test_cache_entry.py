import unittest

from flask import Flask

from cellxgene_gateway import flask_util
from cellxgene_gateway.cache_entry import CacheEntry, CacheEntryStatus
from cellxgene_gateway.cache_key import CacheKey
from cellxgene_gateway.gateway import app
from cellxgene_gateway.items.file.fileitem import FileItem
from cellxgene_gateway.items.file.fileitem_source import FileItemSource
from cellxgene_gateway.items.item import ItemType

key = CacheKey(
    FileItem("/czi/", name="pbmc3k.h5ad", type=ItemType.h5ad),
    FileItemSource("/tmp", "local"),
)


class TestRenderEntry(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def test_GIVEN_key_and_port_THEN_returns_loading_CacheEntry(self):
        entry = CacheEntry.for_key("some-key", 1)
        self.assertEqual(entry.status, CacheEntryStatus.loading)

    def test_GIVEN_absolute_static_url_THEN_include_path(self):
        flask_util.include_source_in_url = False
        actual = CacheEntry.for_key(key, 8000).rewrite_text_content(
            "src:url(/static/assets/"
        )
        expected = "src:url(/view/czi/pbmc3k.h5ad/static/assets/"
        self.assertEqual(actual, expected)

    def test_GIVEN_absolute_src_THEN_include_path(self):
        flask_util.include_source_in_url = False
        actual = CacheEntry.for_key(key, 8000).rewrite_text_content(
            '<link rel="shortcut icon" href="/static/assets/favicon.ico">'
        )
        expected = '<link rel="shortcut icon" href="/view/czi/pbmc3k.h5ad/static/assets/favicon.ico">'
        self.assertEqual(actual, expected)

    def test_GIVEN_absolute_static_url_include_source_THEN_include_path(self):
        flask_util.include_source_in_url = True
        actual = CacheEntry.for_key(key, 8000).rewrite_text_content(
            "src:url(/static/assets/"
        )
        expected = "src:url(/source/local/view/czi/pbmc3k.h5ad/static/assets/"
        self.assertEqual(actual, expected)

    def test_GIVEN_absolute_src_include_source_THEN_include_path(self):
        flask_util.include_source_in_url = True
        actual = CacheEntry.for_key(key, 8000).rewrite_text_content(
            '<link rel="shortcut icon" href="/static/assets/favicon.ico">'
        )
        expected = '<link rel="shortcut icon" href="/source/local/view/czi/pbmc3k.h5ad/static/assets/favicon.ico">'
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
