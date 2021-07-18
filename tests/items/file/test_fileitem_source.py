import tempfile
import unittest
from unittest.mock import patch

from cellxgene_gateway.items.file.fileitem_source import FileItemSource


def stub_join(path):
    path.join = lambda x, y: x + "/" + y


class TestFileItemSource(unittest.TestCase):
    @patch("os.path")
    @patch("os.listdir")
    def test_list_items_GIVEN_no_subpath_THEN_checks_dir(self, listdir, path):
        stub_join(path)
        source = FileItemSource("/tmp/unittest", "local")
        source.list_items()
        path.exists.assert_called_once_with("/tmp/unittest/")

    @patch("os.path")
    @patch("os.listdir")
    def test_list_items_GIVEN_subpath_THEN_checks_subpath(self, listdir, path):
        stub_join(path)
        source = FileItemSource("/tmp/unittest", "local")
        source.list_items("foo")
        path.exists.assert_called_once_with("/tmp/unittest/foo")

    def test_make_fileitem_from_path_GIVEN_annotation_file_THEN_name_lacks_csv(
        self,
    ):
        source = FileItemSource(tempfile.gettempdir(), "local")
        item = source.make_fileitem_from_path(
            "customanno.csv", "someh5ad_annotations", True
        )
        self.assertEqual(item.name, "customanno")
        self.assertEqual(item.descriptor, "someh5ad_annotations/customanno.csv")

    def test_make_fileitem_from_path_GIVEN_h5ad_file_THEN_returns_name(self):
        source = FileItemSource(tempfile.gettempdir(), "local")
        item = source.make_fileitem_from_path("someanalysis.h5ad", "studydir")
        self.assertEqual(item.name, "someanalysis.h5ad")
        self.assertEqual(item.descriptor, "studydir/someanalysis.h5ad")
