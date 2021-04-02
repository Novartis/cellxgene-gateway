import tempfile
import unittest

from cellxgene_gateway.items.file.fileitem_source import FileItemSource


class TestFileItemSource(unittest.TestCase):
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
