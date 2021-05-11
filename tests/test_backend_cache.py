import unittest
from unittest.mock import MagicMock, patch

from cellxgene_gateway.backend_cache import is_port_in_use


class TestIsPortInUse(unittest.TestCase):
    @patch("socket.socket")
    def test_GIVEN_free_port_THEN_returns_true(self, socketMock):
        connectMock = socketMock()
        connectMock.connect_ex.return_value = 0
        connectMock.__enter__.return_value = connectMock
        self.assertEqual(is_port_in_use(123), True)
        self.assertTrue(connectMock.__enter__.calledOnce)
        self.assertTrue(connectMock.__exit__.calledOnce)
        self.assertTrue(connectMock.connect_ex.calledOnceWith("a"))
        self.assertTrue(socketMock.calledOnceWith("a"))

    @patch("socket.socket")
    def test_GIVEN_used_port_THEN_returns_false(self, socketMock):
        connectMock = socketMock()
        connectMock.__enter__.return_value = connectMock
        connectMock.connect_ex.return_value = 1
        self.assertTrue(connectMock.__enter__.calledOnce)
        self.assertTrue(connectMock.__exit__.calledOnce)
        self.assertTrue(connectMock.connect_ex.calledOnceWith("a"))
        self.assertTrue(socketMock.calledOnceWith("a"))
        self.assertEqual(is_port_in_use(123), False)
