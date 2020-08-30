import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.filecrawl import render_entry


class TestRenderEntry(unittest.TestCase):
    def test_GIVEN_path_both_slash_THEN_view_has_single_slash(self):
        entry = {
            "path": "/somepath/",
            "name": "entry",
            "type": "file",
            "annotations": [],
        }
        rendered = render_entry(entry)
        self.assertIn("view/somepath", rendered)

    def test_GIVEN_path_starts_slash_THEN_view_has_single_slash(self):
        entry = {
            "path": "/somepath",
            "name": "entry",
            "type": "file",
            "annotations": [],
        }
        rendered = render_entry(entry)
        self.assertIn("view/somepath", rendered)

    def test_GIVEN_path_ends_slash_THEN_view_has_single_slash(self):
        entry = {
            "path": "somepath/",
            "name": "entry",
            "type": "file",
            "annotations": [],
        }
        rendered = render_entry(entry)
        self.assertIn("view/somepath", rendered)

    def test_GIVEN_path_no_slash_THEN_view_has_single_slash(self):
        entry = {
            "path": "somepath",
            "name": "entry",
            "type": "file",
            "annotations": [],
        }
        rendered = render_entry(entry)
        self.assertIn("view/somepath", rendered)
