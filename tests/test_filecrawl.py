import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.filecrawl import (
    render_item,
    render_item_source,
    render_item_tree,
)
from cellxgene_gateway.items.file.fileitem import FileItem
from cellxgene_gateway.items.file.fileitem_source import FileItemSource
from cellxgene_gateway.items.item import ItemTree, ItemType

source = FileItemSource("/tmp")


def make_entry(subpath="somepath", annotations=None):
    return FileItem(
        subpath=subpath,
        name="entry",
        ext=".h5ad",
        type=ItemType.h5ad,
        annotations=annotations,
    )


class TestRenderEntry(unittest.TestCase):
    def test_GIVEN_path_both_slash_THEN_view_has_single_slash(self):
        entry = make_entry(subpath="/somepath/")
        rendered = render_item(entry, source)
        self.assertIn("view/somepath/entry.h5ad/'", rendered)

    def test_GIVEN_path_starts_slash_THEN_view_has_single_slash(self):
        entry = make_entry(subpath="/somepath")
        rendered = render_item(entry, source)
        self.assertIn("view/somepath/entry.h5ad/'", rendered)

    def test_GIVEN_path_ends_slash_THEN_view_has_single_slash(self):
        entry = make_entry(subpath="somepath/")
        rendered = render_item(entry, source)
        self.assertIn("view/somepath/entry.h5ad/'", rendered)

    def test_GIVEN_path_no_slash_THEN_view_has_single_slash(self):
        entry = make_entry(subpath="somepath")
        rendered = render_item(entry, source)
        self.assertIn("view/somepath/entry.h5ad/'", rendered)


class TestRenderAnnotation(unittest.TestCase):
    def test_GIVEN_no_annotation_THEN_new_alone(self):
        entry = make_entry(annotations=None)
        rendered = render_item(entry, source)
        self.assertIn(
            "> | annotations: <a class='new' href='/source/Files:/tmp/view/somepath/entry_annotations'>new</a></li>",
            rendered,
        )

    def test_GIVEN_annotation_THEN_new_before(self):
        annotation = FileItem(
            subpath="somepath/entry_annotations",
            name="annot",
            ext=".csv",
            type=ItemType.annotation,
        )
        entry = make_entry(annotations=[annotation])
        rendered = render_item(entry, source)
        self.assertIn(
            "> | annotations: <a class='new' href='/source/Files:/tmp/view/somepath/entry_annotations'>new</a>,"
            " <a href='/source/Files:/tmp/view/somepath/entry_annotations/annot.csv/'>annot</a></li>",
            rendered,
        )

    def test_GIVEN_annotation_THEN_escaped(self):
        annotation = FileItem(
            subpath="somepath/entry_annotations",
            name="hot&cold",
            ext=".csv",
            type=ItemType.annotation,
        )
        entry = make_entry(annotations=[annotation])
        rendered = render_item(entry, source)
        self.assertIn(
            "> | annotations: <a class='new' href='/source/Files:/tmp/view/somepath/entry_annotations'>new</a>,"
            " <a href='/source/Files:/tmp/view/somepath/entry_annotations/hot%26cold.csv/'>hot&amp;cold</a></li>",
            rendered,
        )


class TestRenderItemSource(unittest.TestCase):
    @patch("cellxgene_gateway.items.file.fileitem_source.FileItemSource")
    def test_GIVEN_some_filter_THEN_includes_filterpart_in_heading(self, item_source):
        item_source.name = "FakeSource"
        item_source.list_items.return_value = ItemTree("rootdir", [], [])
        rendered = render_item_source(item_source, "some_filter")
        self.assertEqual(
            rendered,
            "<h6><a href='/filecrawl.html?source=FakeSource'>FakeSource</a>:some_filter</h6><li><a href='/filecrawl/rootdir?source=FakeSource'>rootdir</a><ul></ul></li>",
        )


class TestRenderItemTree(unittest.TestCase):
    @patch("cellxgene_gateway.items.file.fileitem_source.FileItemSource")
    def test_GIVEN_deep_nested_dirs_THEN_includes_dirs_in_output(self, item_source):
        item_source.name = "FakeSource"
        item_tree = ItemTree("foo/bar/baz", [], [])
        rendered = render_item_tree(item_tree, item_source)
        self.assertEqual(
            rendered,
            "<li><a href='/filecrawl/foo/bar/baz?source=FakeSource'>baz</a><ul></ul></li>",
        )
