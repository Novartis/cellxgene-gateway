import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.extra_scripts import get_extra_scripts


class TestExtraScripts(unittest.TestCase):
    @patch("cellxgene_gateway.env.extra_scripts", new='["abc","def"]')
    def test_GIVEN_two_scripts_THEN_returns_two_strings(self):
        self.assertEqual(get_extra_scripts(), ["abc", "def"])

    @patch("cellxgene_gateway.env.extra_scripts", new='["abc", "def"]')
    def test_GIVEN_two_scripts_space_THEN_returns_two_strings(self):
        self.assertEqual(get_extra_scripts(), ["abc", "def"])

    @patch("cellxgene_gateway.env.extra_scripts", new=None)
    def test_GIVEN_none_THEN_returns_empty_array(self):
        self.assertEqual(get_extra_scripts(), [])

    @patch("cellxgene_gateway.env.extra_scripts", new="[]")
    def test_GIVEN_empty_string_THEN_returns_empty_array(self):
        self.assertEqual(get_extra_scripts(), [])

    @patch("cellxgene_gateway.env.extra_scripts", new="'asdf'")
    def test_GIVEN_bare_string_THEN_throws_Exception(self):
        with self.assertRaises(Exception) as context:
            self.assertEqual(get_extra_scripts(), [])
        self.assertEqual(
            'Error parsing GATEWAY_EXTRA_SCRIPTS, expected JSON array e.g. ["https://example.com/path/to/script.js"]',
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
