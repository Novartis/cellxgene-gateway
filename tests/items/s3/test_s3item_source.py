import unittest
from unittest.mock import MagicMock, Mock, patch

from cellxgene_gateway.items.item import ItemType
from cellxgene_gateway.items.s3.s3item import S3Item
from cellxgene_gateway.items.s3.s3item_source import S3ItemSource


class TestScanDirectory(unittest.TestCase):
    @patch("s3fs.S3FileSystem")
    def test_GIVEN_invalid_bucket_THEN_throws_error(self, s3func):
        class S3Mock:
            def exists(path):
                if path in ["s3://my-bucket/"]:
                    return False

        s3func.return_value = S3Mock
        source = S3ItemSource("my-bucket")
        with self.assertRaises(Exception) as context:
            source.scan_directory()
        self.assertEqual(
            "S3 url 's3://my-bucket/' does not exist.",
            str(context.exception),
        )

    @patch("s3fs.S3FileSystem")
    def test__GIVEN_multilevel_bucket_THEN_properly_recurses_suburls(self, s3func):
        class S3Mock:
            def exists(path):
                if path in [
                    "s3://my-bucket/",
                    "s3://my-bucket/pbmc3k.h5ad",
                    "s3://my-bucket/lvl1",
                    "s3://my-bucket/lvl1/pbmc3k_l1.h5ad",
                    "s3://my-bucket/lvl1/lvl2",
                    "s3://my-bucket/lvl1/lvl2/pbmc3k_l2.h5ad",
                ]:
                    return True
                raise Exception("exists called with " + path)

            def ls(path):
                if path == "s3://my-bucket/":
                    return [
                        "my-bucket/lvl1",
                        "my-bucket/pbmc3k.h5ad",
                        "my-bucket/pbmc3k_annotations",
                    ]
                elif path == "s3://my-bucket/pbmc3k_annotations":
                    return ["my-bucket/pbmc3k_annotations/annot.csv"]
                elif path == "s3://my-bucket/lvl1":
                    return ["my-bucket/lvl1/lvl2", "my-bucket/lvl1/pbmc3k_l1.h5ad"]
                elif path == "s3://my-bucket/lvl1/lvl2":
                    return ["my-bucket/lvl1/lvl2/pbmc3k_l2.h5ad"]

                raise Exception("ls called with " + path)

            def isdir(path):
                if path in [
                    "s3://my-bucket/lvl1",
                    "s3://my-bucket/pbmc3k_annotations",
                    "s3://my-bucket/lvl1/lvl2",
                ]:
                    return True
                if path in [
                    "s3://my-bucket/pbmc3k.h5ad",
                    "s3://my-bucket/lvl1/pbmc3k_l1.h5ad",
                    "s3://my-bucket/lvl1/pbmc3k_l1_annotations",
                    "s3://my-bucket/lvl1/lvl2/pbmc3k_l2.h5ad",
                    "s3://my-bucket/lvl1/lvl2/pbmc3k_l2_annotations",
                ]:
                    return False
                raise Exception("isdir called with " + path)

            def isfile(path):
                if path in ["s3://my-bucket/pbmc3k_annotations/annot.csv"]:
                    return True
                if path in ["s3://my-bucket/pbmc3k_annotations"]:
                    return False
                raise Exception("isfile called with " + path)

        s3func.return_value = S3Mock
        source = S3ItemSource("my-bucket")
        tree = source.scan_directory()

        def s3item_compare(i1, i2, msg=""):
            self.assertEqual(i1.name, i2.name, "name equals")
            self.assertEqual(i1.type, i2.type, "type equals")
            self.assertEqual(i1.s3key, i2.s3key, "s3key equals")
            if i1.annotations is None:
                self.assertEqual(i1.annotations, i2.annotations, "annotations equals")
            else:
                self.assertEqual(
                    len(i1.annotations),
                    len(i2.annotations),
                    "annotations length equals",
                )
                for a1, a2 in zip(i1.annotations, i2.annotations):
                    self.assertEqual(a1, a2)
            return True

        self.addTypeEqualityFunc(S3Item, s3item_compare)

        def assertTree(t, descriptor, items):
            self.assertEqual(t.descriptor, descriptor)
            self.assertEqual(len(t.items), len(items))
            for i1, i2 in zip(t.items, items):
                self.assertEqual(i1, i2)

        assertTree(
            tree,
            "",
            [
                S3Item(
                    "pbmc3k.h5ad",
                    name="pbmc3k.h5ad",
                    type=ItemType.h5ad,
                    annotations=[
                        S3Item(
                            "pbmc3k_annotations/annot.csv",
                            name="annot.csv",
                            type=ItemType.annotation,
                        )
                    ],
                )
            ],
        )
        self.assertEqual(len(tree.branches), 1)
        lvl1 = tree.branches[0]
        assertTree(
            lvl1,
            "lvl1",
            [
                S3Item(
                    "lvl1/pbmc3k_l1.h5ad",
                    name="pbmc3k_l1.h5ad",
                    type=ItemType.h5ad,
                    annotations=None,
                )
            ],
        )
        self.assertEqual(len(lvl1.branches), 1)
        lvl2 = lvl1.branches[0]
        assertTree(
            lvl2,
            "lvl1/lvl2",
            [
                S3Item(
                    "lvl1/lvl2/pbmc3k_l2.h5ad",
                    name="pbmc3k_l2.h5ad",
                    type=ItemType.h5ad,
                    annotations=None,
                )
            ],
        )
        self.assertEqual(lvl2.branches, None)


class TestListItems(unittest.TestCase):
    def test_GIVEN_filter_THEN_pass_filter_into_scan_directory(self):
        source = S3ItemSource("my-bucket")
        source.scan_directory = MagicMock()
        tree = source.list_items("some-filter")
        source.scan_directory.assert_called_once_with("some-filter")

    def test_GIVEN_no_filter_THEN_pass_empty_string_into_scan_directory(self):
        source = S3ItemSource("my-bucket")
        source.scan_directory = MagicMock()
        tree = source.list_items()
        source.scan_directory.assert_called_once_with("")
