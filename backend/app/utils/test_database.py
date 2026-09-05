
import pytest
from unittest.mock import patch, MagicMock
import pymongo.errors

from app.utils.database import (
    Database,
    DatabaseConnectionError,
    DataInsertionError,
    DataRetrievalError,
    CollectionAccessError
)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """
    Automatically-applied fixture to mock environment variables before each test runs.
    Ensures a controlled and isolated test environment for DB connection logic.
    """
    monkeypatch.setenv("DB_STRING", "mongodb://example.invalid:27017/")
    monkeypatch.setenv("DB_NAME", "mockdb")
    monkeypatch.setenv("DB_PASSWORD", "mockpass")


def test_successful_connection():
    """Simulate a successful DB connection by mocking MongoClient.ping."""
    with patch("pymongo.MongoClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.admin.command.return_value = {"ok": 1}
        mock_client.return_value = mock_instance

        db = Database()
        assert db.db is not None

def test_failed_authentication():
    """Simulate authentication failure using OperationFailure and expect custom exception."""
    with patch("pymongo.MongoClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.admin.command.side_effect = pymongo.errors.OperationFailure("Auth failed")
        mock_client.return_value = mock_instance

        with pytest.raises(DatabaseConnectionError):
            Database()

def test_add_record_success():
    """Test that a document is successfully inserted and the correct ID is returned."""
    with patch("pymongo.MongoClient") as mock_client:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.insert_one.return_value.inserted_id = "1234"

        mock_db.__getitem__.return_value = mock_collection
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_client.return_value.admin.command.return_value = {"ok": 1}

        db = Database()
        result = db.add_record("users", {"name": "Amutheshwar"})
        assert result == "1234"

def test_get_record_not_found():
    """Check that get_record returns None when no match is found (no crash)."""
    with patch("pymongo.MongoClient") as mock_client:
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        mock_db.__getitem__.return_value = mock_collection
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_client.return_value.admin.command.return_value = {"ok": 1}

        db = Database()
        result = db.get_record("users", {"username": "ghost"})
        assert result is None

def test_add_records_with_batching():
    """Ensure batched inserts are performed and all returned IDs are combined."""
    with patch("pymongo.MongoClient") as mock_client:
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_collection.insert_many.side_effect = [
            MagicMock(inserted_ids=["a"]),
            MagicMock(inserted_ids=["b"])
        ]

        mock_db.__getitem__.return_value = mock_collection
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_client.return_value.admin.command.return_value = {"ok": 1}

        db = Database()
        docs = [{"n": 1}, {"n": 2}]
        result = db.add_records("batch", docs, batch_size=1)
        assert result == ["a", "b"]

def test_get_records_with_limit_sort():
    """Simulate use of sort + limit and verify results are returned in order."""
    with patch("pymongo.MongoClient") as mock_client:
        mock_cursor = MagicMock()

        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter([{"x": 1}, {"x": 2}])

        mock_collection = MagicMock()
        mock_collection.find.return_value = mock_cursor

        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection

        mock_client.return_value.__getitem__.return_value = mock_db
        mock_client.return_value.admin.command.return_value = {"ok": 1}

        db = Database()
        result = db.get_records("logs", query={}, limit=2, sort={"x": 1})
        assert result == [{"x": 1}, {"x": 2}]

def test_server_selection_timeout():
    """Raise ServerSelectionTimeoutError and ensure custom exception is triggered."""
    with patch("pymongo.MongoClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.admin.command.side_effect = pymongo.errors.ServerSelectionTimeoutError("Timeout")
        mock_client.return_value = mock_instance

        with pytest.raises(DatabaseConnectionError):
            Database()

def test_logging_warning_on_missing_db(caplog):
    """Check that a warning is logged if get_database is called when not connected."""
    with patch("pymongo.MongoClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.admin.command.return_value = {"ok": 1}
        mock_client.return_value = mock_instance

        db = Database()
        db.db = None

        _ = db.get_database()
        assert "Database not connected" in caplog.text

def test_close_connection():
    """Ensure close_connection properly shuts down the client and resets internal state."""
    with patch("pymongo.MongoClient") as mock_client:
        mock_instance = MagicMock()
        mock_instance.admin.command.return_value = {"ok": 1}
        mock_client.return_value = mock_instance

        db = Database()
        db.close_connection()

        assert db.client is None
        assert db.db is None

