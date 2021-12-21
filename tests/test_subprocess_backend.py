import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.backend_cache import BackendCache
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
