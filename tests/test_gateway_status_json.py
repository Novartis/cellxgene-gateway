import json
import unittest
from types import SimpleNamespace

from cellxgene_gateway.gateway import do_GET_status_json, app, cache
from cellxgene_gateway.cache_entry import CacheEntry, CacheEntryStatus


class TestGatewayStatusJson(unittest.TestCase):
    def test_do_GET_status_json_returns_expected_structure(self):
        # Create a minimal fake key with required attributes
        h5ad_item = SimpleNamespace(descriptor="somedir/dataset.h5ad")
        key = SimpleNamespace(
            h5ad_item=h5ad_item,
            annotation_descriptor="somedir/dataset_annotations/foo.csv",
        )

        # Create a CacheEntry with known launchtime/timestamp/status
        entry = CacheEntry(
            None,
            key,
            8000,
            111,
            222,
            CacheEntryStatus.loaded,
            None,
            None,
            None,
            None,
        )

        # Install into the gateway cache and set app launchtime
        cache.entry_list = [entry]
        app.extensions.setdefault("cellxgene_gateway", {})["launchtime"] = "LAUNCH_TIME"

        rv = do_GET_status_json()

        data = json.loads(rv)
        # top-level launchtime comes from app.extensions
        self.assertEqual("LAUNCH_TIME", data["launchtime"])

        self.assertIn("entry_list", data)
        self.assertEqual(1, len(data["entry_list"]))

        e = data["entry_list"][0]
        self.assertEqual("somedir/dataset.h5ad", e["dataset"])
        self.assertEqual("somedir/dataset_annotations/foo.csv", e["annotation_file"])
        self.assertEqual("loaded", e["status"])
        self.assertEqual(111, e["launchtime"])
        self.assertEqual(222, e["last_access"])


if __name__ == "__main__":
    unittest.main()
