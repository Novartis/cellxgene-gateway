import unittest
import pytest
from http import HTTPStatus
from unittest.mock import MagicMock, Mock, patch, call
from freezegun import freeze_time

from cellxgene_gateway.backend_cache import BackendCache, is_port_in_use
from cellxgene_gateway.cache_entry import CacheEntry, CacheEntryStatus
from cellxgene_gateway.cache_key import CacheKey
from cellxgene_gateway.cellxgene_exception import CellxgeneException


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


class TestBackendCacheInit(unittest.TestCase):
    def test_GIVEN_new_backend_cache_THEN_entry_list_is_empty(self):
        """BackendCache should initialize with an empty entry list."""
        cache = BackendCache()
        self.assertEqual(cache.entry_list, [])


class TestBackendCacheGetPorts(unittest.TestCase):
    def test_GIVEN_empty_cache_THEN_get_ports_returns_empty_list(self):
        """get_ports should return empty list when no entries exist."""
        cache = BackendCache()
        ports = cache.get_ports()
        self.assertEqual(ports, [])

    def test_GIVEN_cache_with_entries_THEN_get_ports_returns_all_ports(self):
        """get_ports should return list of all ports from entries."""
        cache = BackendCache()

        # Create mock entries with different ports
        entry1 = Mock()
        entry1.port = 8000
        entry2 = Mock()
        entry2.port = 8001
        entry3 = Mock()
        entry3.port = 8002

        cache.entry_list = [entry1, entry2, entry3]

        ports = cache.get_ports()
        self.assertEqual(ports, [8000, 8001, 8002])

    def test_GIVEN_single_entry_THEN_get_ports_returns_single_port(self):
        """get_ports should correctly handle a single entry."""
        cache = BackendCache()
        entry = Mock()
        entry.port = 9000

        cache.entry_list = [entry]

        ports = cache.get_ports()
        self.assertEqual(ports, [9000])


class TestBackendCacheCheckPath(unittest.TestCase):
    def setUp(self):
        self.cache = BackendCache()

    def test_GIVEN_no_matching_path_THEN_check_path_returns_none(self):
        """check_path should return None when no entries match the path."""
        source = Mock()
        source.name = "test_source"

        cache_entry = Mock()
        cache_entry.status = CacheEntryStatus.loaded
        cache_entry.key = Mock()
        cache_entry.key.source.name = "other_source"
        cache_entry.key.descriptor = "/some/path"

        self.cache.entry_list = [cache_entry]

        result = self.cache.check_path(source, "/test/path")
        self.assertIsNone(result)

    def test_GIVEN_terminated_entry_THEN_check_path_ignores_it(self):
        """check_path should ignore entries with terminated status."""
        source = Mock()
        source.name = "test_source"

        cache_entry = Mock()
        cache_entry.status = CacheEntryStatus.terminated
        cache_entry.key = Mock()
        cache_entry.key.source.name = "test_source"
        cache_entry.key.descriptor = "/data"

        self.cache.entry_list = [cache_entry]

        result = self.cache.check_path(source, "/data/file.txt")
        self.assertIsNone(result)

    def test_GIVEN_single_matching_entry_THEN_check_path_returns_it(self):
        """check_path should return the matching entry when exactly one matches."""
        source = Mock()
        source.name = "test_source"

        cache_entry = Mock()
        cache_entry.status = CacheEntryStatus.loaded
        cache_entry.key = Mock()
        cache_entry.key.source.name = "test_source"
        cache_entry.key.descriptor = "/data"

        self.cache.entry_list = [cache_entry]

        result = self.cache.check_path(source, "/data/file.txt")
        self.assertIs(result, cache_entry)

    def test_GIVEN_path_that_does_not_start_with_descriptor_THEN_check_path_returns_none(
        self,
    ):
        """check_path should return None if path doesn't start with descriptor."""
        source = Mock()
        source.name = "test_source"

        cache_entry = Mock()
        cache_entry.status = CacheEntryStatus.loaded
        cache_entry.key = Mock()
        cache_entry.key.source.name = "test_source"
        cache_entry.key.descriptor = "/data"

        self.cache.entry_list = [cache_entry]

        result = self.cache.check_path(source, "/other/file.txt")
        self.assertIsNone(result)

    def test_GIVEN_multiple_matching_entries_THEN_check_path_raises_exception(self):
        """check_path should raise exception when multiple entries match."""
        source = Mock()
        source.name = "test_source"

        cache_entry1 = Mock()
        cache_entry1.status = CacheEntryStatus.loaded
        cache_entry1.key = Mock()
        cache_entry1.key.source.name = "test_source"
        cache_entry1.key.descriptor = "/data"

        cache_entry2 = Mock()
        cache_entry2.status = CacheEntryStatus.loaded
        cache_entry2.key = Mock()
        cache_entry2.key.source.name = "test_source"
        cache_entry2.key.descriptor = "/data"

        self.cache.entry_list = [cache_entry1, cache_entry2]

        with self.assertRaises(CellxgeneException) as context:
            self.cache.check_path(source, "/data/file.txt")

        # The CellxgeneException is raised with HTTPStatus as first arg and message as second
        self.assertEqual(context.exception.message, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn("Found 2", context.exception.http_status)

    def test_GIVEN_mixed_entries_THEN_check_path_returns_only_matching_active_entry(
        self,
    ):
        """check_path should correctly filter by source, path, and status."""
        source = Mock()
        source.name = "target_source"

        # Terminated entry - should be ignored
        terminated_entry = Mock()
        terminated_entry.status = CacheEntryStatus.terminated
        terminated_entry.key = Mock()
        terminated_entry.key.source.name = "target_source"
        terminated_entry.key.descriptor = "/data"

        # Different source - should be ignored
        other_source_entry = Mock()
        other_source_entry.status = CacheEntryStatus.loaded
        other_source_entry.key = Mock()
        other_source_entry.key.source.name = "other_source"
        other_source_entry.key.descriptor = "/data"

        # Matching entry - should be returned
        matching_entry = Mock()
        matching_entry.status = CacheEntryStatus.loaded
        matching_entry.key = Mock()
        matching_entry.key.source.name = "target_source"
        matching_entry.key.descriptor = "/data"

        self.cache.entry_list = [terminated_entry, other_source_entry, matching_entry]

        result = self.cache.check_path(source, "/data/file.txt")
        self.assertIs(result, matching_entry)


class TestBackendCacheCheckEntry(unittest.TestCase):
    def setUp(self):
        self.cache = BackendCache()

    def test_GIVEN_no_matching_entry_THEN_check_entry_returns_none(self):
        """check_entry should return None when no entries match the key."""
        key = Mock()

        cache_entry = Mock()
        cache_entry.status = CacheEntryStatus.loaded
        cache_entry.key = Mock()
        cache_entry.key.equals.return_value = False

        self.cache.entry_list = [cache_entry]

        result = self.cache.check_entry(key)
        self.assertIsNone(result)

    def test_GIVEN_terminated_entry_THEN_check_entry_ignores_it(self):
        """check_entry should ignore entries with terminated status."""
        key = Mock()

        cache_entry = Mock()
        cache_entry.status = CacheEntryStatus.terminated
        cache_entry.key = Mock()
        cache_entry.key.equals.return_value = True

        self.cache.entry_list = [cache_entry]

        result = self.cache.check_entry(key)
        self.assertIsNone(result)

    def test_GIVEN_single_matching_entry_THEN_check_entry_returns_it(self):
        """check_entry should return the matching entry when exactly one matches."""
        key = Mock()

        cache_entry = Mock()
        cache_entry.status = CacheEntryStatus.loaded
        cache_entry.key = Mock()
        cache_entry.key.equals.return_value = True

        self.cache.entry_list = [cache_entry]

        result = self.cache.check_entry(key)
        self.assertIs(result, cache_entry)

    def test_GIVEN_multiple_matching_entries_THEN_check_entry_raises_exception(self):
        """check_entry should raise exception when multiple entries match."""
        key = Mock()
        key.dataset = "test_dataset"

        cache_entry1 = Mock()
        cache_entry1.status = CacheEntryStatus.loaded
        cache_entry1.key = Mock()
        cache_entry1.key.equals.return_value = True

        cache_entry2 = Mock()
        cache_entry2.status = CacheEntryStatus.loaded
        cache_entry2.key = Mock()
        cache_entry2.key.equals.return_value = True

        self.cache.entry_list = [cache_entry1, cache_entry2]

        with self.assertRaises(CellxgeneException) as context:
            self.cache.check_entry(key)

        # The CellxgeneException is raised with HTTPStatus as first arg and message as second
        self.assertEqual(context.exception.message, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn("Found 2", context.exception.http_status)

    def test_GIVEN_mixed_entries_THEN_check_entry_returns_only_matching_active_entry(
        self,
    ):
        """check_entry should correctly filter by key equality and status."""
        key = Mock()

        # Terminated entry - should be ignored
        terminated_entry = Mock()
        terminated_entry.status = CacheEntryStatus.terminated
        terminated_entry.key = Mock()
        terminated_entry.key.equals.return_value = True

        # Non-matching entry - should be ignored
        non_matching_entry = Mock()
        non_matching_entry.status = CacheEntryStatus.loaded
        non_matching_entry.key = Mock()
        non_matching_entry.key.equals.return_value = False

        # Matching entry - should be returned
        matching_entry = Mock()
        matching_entry.status = CacheEntryStatus.loaded
        matching_entry.key = Mock()
        matching_entry.key.equals.return_value = True

        self.cache.entry_list = [terminated_entry, non_matching_entry, matching_entry]

        result = self.cache.check_entry(key)
        self.assertIs(result, matching_entry)


class TestBackendCachePrune(unittest.TestCase):
    def test_GIVEN_entry_in_cache_THEN_prune_removes_it(self):
        """prune should remove the entry from the cache."""
        cache = BackendCache()

        entry_mock = Mock()
        cache.entry_list = [entry_mock]

        cache.prune(entry_mock)

        self.assertEqual(len(cache.entry_list), 0)
        self.assertNotIn(entry_mock, cache.entry_list)

    def test_GIVEN_entry_in_cache_THEN_prune_terminates_it(self):
        """prune should call terminate on the entry."""
        cache = BackendCache()

        entry_mock = Mock()
        cache.entry_list = [entry_mock]

        cache.prune(entry_mock)

        entry_mock.terminate.assert_called_once()

    def test_GIVEN_multiple_entries_THEN_prune_removes_only_target_entry(self):
        """prune should only remove the specified entry, not others."""
        cache = BackendCache()

        entry1 = Mock()
        entry2 = Mock()
        entry3 = Mock()

        cache.entry_list = [entry1, entry2, entry3]

        cache.prune(entry2)

        self.assertEqual(len(cache.entry_list), 2)
        self.assertIn(entry1, cache.entry_list)
        self.assertNotIn(entry2, cache.entry_list)
        self.assertIn(entry3, cache.entry_list)

        # Verify only entry2 was terminated
        entry1.terminate.assert_not_called()
        entry2.terminate.assert_called_once()
        entry3.terminate.assert_not_called()

    def test_GIVEN_empty_cache_THEN_prune_raises_value_error(self):
        """prune should raise ValueError if entry is not in cache."""
        cache = BackendCache()

        entry_mock = Mock()

        with self.assertRaises(ValueError):
            cache.prune(entry_mock)


@pytest.fixture(autouse=True)
def connect_mock():
    with patch("socket.socket") as socketMock:
        connectMock = socketMock()
        connectMock.__enter__.return_value = connectMock
        connectMock.connect_ex.return_value = 1  # Port not in use by default
        yield connectMock


@pytest.fixture(autouse=True)
def process_backend_mock():
    with patch("cellxgene_gateway.backend_cache.process_backend") as mock:
        yield mock


@pytest.fixture(autouse=True)
def sleep_mock():
    from time import sleep

    with patch("cellxgene_gateway.backend_cache.time.sleep") as mock:
        mock.side_effect = lambda x: sleep(0.01)  # short sleep
        yield mock


@freeze_time("2025-12-01 10:00:00")
def test_GIVEN_empty_cache_THEN_create_entry_uses_starting_port(process_backend_mock):
    """create_entry should use port 8000 when cache is empty and port is free."""
    key = Mock()
    scripts = ["script1", "script2"]

    cache = BackendCache()
    result = cache.create_entry(key, scripts)

    # Verify port 8000 was used
    assert result.port == 8000

    # Verify entry was added to list
    assert result in cache.entry_list
    # Verify thread was started
    process_backend_mock.launch.assert_called_once()

    # Verify CacheEntry was created with correct key
    assert result.key is key
    assert result.status == CacheEntryStatus.loading


@freeze_time("2025-12-01 10:00:00")
def test_GIVEN_port_in_use_THEN_create_entry_finds_next_available_port(connect_mock):
    """create_entry should increment port until finding one that's free."""
    # Ports 8000 and 8001 are in use, 8002 is free
    connect_mock.connect_ex.side_effect = [0, 0, 1]

    key = Mock()
    scripts = []

    cache = BackendCache()
    result = cache.create_entry(key, scripts)

    # Verify port 8002 was used (after skipping 8000 and 8001)
    assert result.port == 8002


@freeze_time("2025-12-01 10:00:00")
def test_GIVEN_port_exists_in_cache_THEN_create_entry_skips_it():
    """create_entry should skip ports already in the cache."""
    key = Mock()
    scripts = []

    # Pre-populate cache with port 8000
    existing_entry = Mock()
    existing_entry.port = 8000

    cache = BackendCache()
    cache.entry_list = [existing_entry]

    result = cache.create_entry(key, scripts)

    # Verify port 8001 was used (skipping the existing 8000)
    assert result.port == 8001


@freeze_time("2025-12-01 10:00:00")
def test_GIVEN_create_entry_THEN_background_thread_is_started(process_backend_mock):
    """create_entry should start a background thread with correct args."""
    key = Mock()
    scripts = ["script1"]

    with patch("cellxgene_gateway.backend_cache.env") as env_mock:
        env_mock.cellxgene_location = "/path/to/cellxgene"

        cache = BackendCache()
        result = cache.create_entry(key, scripts)

    # Verify Thread was created with correct target and args
    process_backend_mock.launch.assert_called_once()
    call_kwargs = process_backend_mock.launch.call_args[0]
    assert call_kwargs == ("/path/to/cellxgene", ["script1"], result)


@freeze_time("2025-12-01 10:00:00")
def test_GIVEN_create_entry_THEN_entry_is_added_to_cache():
    """create_entry should add the created entry to the cache list."""
    key = Mock()
    scripts = []

    cache = BackendCache()
    initial_count = len(cache.entry_list)

    result = cache.create_entry(key, scripts)

    # Verify entry was added
    assert len(cache.entry_list) == initial_count + 1
    assert result in cache.entry_list


@freeze_time("2025-12-01 10:00:00")
def test_GIVEN_create_entry_THEN_returns_created_entry():
    """create_entry should return the created entry."""
    key = Mock()
    scripts = []

    cache = BackendCache()
    result = cache.create_entry(key, scripts)

    # Verify the result is a CacheEntry instance
    assert isinstance(result, CacheEntry)
    assert result.status == CacheEntryStatus.loading
