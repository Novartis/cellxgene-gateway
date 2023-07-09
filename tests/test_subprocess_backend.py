import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.cache_entry import CacheEntry
from cellxgene_gateway.cache_key import CacheKey
from cellxgene_gateway.items.file.fileitem import FileItem
from cellxgene_gateway.items.file.fileitem_source import FileItemSource
from cellxgene_gateway.items.item import ItemType
from cellxgene_gateway.process_exception import ProcessException


class TestSubprocessBackend(unittest.TestCase):
    @patch("subprocess.Popen")
    def test_launch_GIVEN_no_stdout_THEN_throw_ProcessException(self, popen):
        subprocess = MagicMock()
        subprocess.stdout.readline().decode.return_value = ""
        subprocess.stderr.read().decode.return_value = "An unexpected error"
        popen.return_value = subprocess

        key = CacheKey(
            FileItem("/czi/", name="pbmc3k.h5ad", type=ItemType.h5ad),
            FileItemSource("/tmp", "local"),
        )
        entry = CacheEntry.for_key(key, 8000)
        from cellxgene_gateway.subprocess_backend import SubprocessBackend

        backend = SubprocessBackend()
        cellxgene_loc = "/some/cellxgene"
        scripts = ["http://example.com/script.js", "http://example.com/script2.js"]

        with self.assertRaises(ProcessException) as context:
            backend.launch(cellxgene_loc, scripts, entry)
        popen.assert_called_once_with(
            [
                "yes | /some/cellxgene launch /tmp/czi/pbmc3k.h5ad --port 8000 --host 127.0.0.1 --disable-annotations --disable-gene-sets-save --scripts http://example.com/script.js --scripts http://example.com/script2.js"
            ],
            shell=True,
            stderr=-1,
            stdout=-1,
        )
        self.assertEqual("An unexpected error", context.exception.stderr)

    @patch("subprocess.Popen")
    def test_launch_GIVEN_annotations_enabled_THEN_set_flags(self, popen):
        subprocess = MagicMock()
        subprocess.stdout.readline().decode.return_value = (
            "[cellxgene] Type CTRL-C at any time to exit.\n"
        )
        subprocess.stderr.read().decode.return_value = ""
        popen.return_value = subprocess

        key = CacheKey(
            FileItem("/czi/", name="pbmc3k.h5ad", type=ItemType.h5ad),
            FileItemSource("/tmp", "local"),
            FileItem(
                "/czi/pbmc3k_annotations/", name="foo.csv", type=ItemType.annotation
            ),
        )
        entry = CacheEntry.for_key(key, 8000)
        import cellxgene_gateway.subprocess_backend

        cellxgene_gateway.subprocess_backend.enable_annotations = True
        try:
            backend = cellxgene_gateway.subprocess_backend.SubprocessBackend()
            cellxgene_loc = "/some/cellxgene"

            backend.launch(cellxgene_loc, [], entry)
        finally:
            cellxgene_gateway.subprocess_backend.enable_annotations = False
        popen.assert_called_once_with(
            [
                "yes | /some/cellxgene launch /tmp/czi/pbmc3k.h5ad --port 8000 --host 127.0.0.1 --annotations-file /tmp/czi/pbmc3k_annotations/foo.csv --gene-sets-file /tmp/czi/pbmc3k_annotations/foo_gene_sets.csv"
            ],
            shell=True,
            stderr=-1,
            stdout=-1,
        )
