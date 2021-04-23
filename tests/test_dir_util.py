import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.dir_util import ensure_dir_exists, make_annotations, make_h5ad


class TestMakeH5ad(unittest.TestCase):
    def test_GIVEN_annotation_dir_THEN_returns_h5ad(self):
        self.assertEqual(make_h5ad("pbmc_annotations"), "pbmc.h5ad")


class TestMakeAnnotations(unittest.TestCase):
    def test_GIVEN_h5ad_THEN_returns_annotations(self):
        self.assertEqual(make_annotations("pbmc.h5ad"), "pbmc_annotations")


class TestMakeAnnotations(unittest.TestCase):
    def test_GIVEN_h5ad_THEN_returns_annotations(self):
        self.assertEqual(make_annotations("pbmc.h5ad"), "pbmc_annotations")


class TestEnsureDirExists(unittest.TestCase):
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_GIVEN_existing_THEN_does_not_call_makedir(self, makedirsMock, existsMock):
        existsMock.return_value = True
        ensure_dir_exists("/foo")
        makedirsMock.assert_not_called()

    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_GIVEN_not_existing_THEN_calls_makedir(self, makedirsMock, existsMock):
        existsMock.return_value = False
        ensure_dir_exists("/foo")
        makedirsMock.assert_called_once_with("/foo")
