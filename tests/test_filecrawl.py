import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.filecrawl import render_item
from cellxgene_gateway.items.file.fileitem import FileItem
from cellxgene_gateway.items.file.fileitem_source import FileItemSource
from cellxgene_gateway.items.item import ItemType

source = FileItemSource("/tmp")


class TestRenderEntry(unittest.TestCase):
    def test_GIVEN_path_both_slash_THEN_view_has_single_slash(self):
        entry = FileItem(subpath="/somepath/", name="entry", type=ItemType.h5ad)
        rendered = render_item(entry, source)
        self.assertIn("view/somepath/entry/'", rendered)

    def test_GIVEN_path_starts_slash_THEN_view_has_single_slash(self):
        entry = FileItem(subpath="/somepath", name="entry", type=ItemType.h5ad)
        rendered = render_item(entry, source)
        self.assertIn("view/somepath/entry/'", rendered)

    def test_GIVEN_path_ends_slash_THEN_view_has_single_slash(self):
        entry = FileItem(subpath="somepath/", name="entry", type=ItemType.h5ad)
        rendered = render_item(entry, source)
        self.assertIn("view/somepath/entry/'", rendered)

    def test_GIVEN_path_no_slash_THEN_view_has_single_slash(self):
        entry = FileItem(subpath="somepath", name="entry", type=ItemType.h5ad)
        rendered = render_item(entry, source)
        self.assertIn("view/somepath/entry/'", rendered)
