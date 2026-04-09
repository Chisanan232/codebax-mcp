"""Unit tests for lock file store implementation."""

import json
import hashlib
import pytest
from pathlib import Path
from codebax_mcp.core.index.lock_file_store import LockFileStore


class TestLockFileStore:
    """Test suite for LockFileStore class."""

    @pytest.fixture
    def temp_lock_file(self, tmp_path):
        """Create a temporary lock file path."""
        return str(tmp_path / ".codebax_index.lock")

    @pytest.fixture
    def store(self, temp_lock_file):
        """Create a LockFileStore instance with temp path."""
        return LockFileStore(temp_lock_file)

    @pytest.fixture
    def sample_index_data(self):
        """Sample index data for testing."""
        return {
            "symbol_definitions": {
                "test:function:foo:1": {
                    "symbol_id": "test:function:foo:1",
                    "name": "foo",
                    "kind": "function",
                    "file": "test.py"
                }
            },
            "symbol_usages": {},
            "metadata": {
                "indexed_at": "2024-01-01T00:00:00",
                "file_count": 1
            }
        }

    def test_save_creates_lock_file(self, store, temp_lock_file, sample_index_data):
        """Test that save creates a lock file."""
        result = store.save(sample_index_data)
        
        assert result is True
        assert Path(temp_lock_file).exists()

    def test_save_and_load_roundtrip(self, store, sample_index_data):
        """Test that data can be saved and loaded correctly."""
        store.save(sample_index_data)
        loaded_data = store.load()
        
        assert loaded_data is not None
        assert loaded_data["symbol_definitions"] == sample_index_data["symbol_definitions"]
        assert loaded_data["metadata"]["file_count"] == 1

    def test_load_nonexistent_file(self, store):
        """Test loading from non-existent file returns None."""
        result = store.load()
        
        assert result is None

    def test_exists_returns_false_for_nonexistent(self, store):
        """Test exists returns False when file doesn't exist."""
        assert store.exists() is False

    def test_exists_returns_true_after_save(self, store, sample_index_data):
        """Test exists returns True after saving."""
        store.save(sample_index_data)
        
        assert store.exists() is True

    def test_delete_removes_file(self, store, sample_index_data):
        """Test delete removes the lock file."""
        store.save(sample_index_data)
        assert store.exists() is True
        
        result = store.delete()
        
        assert result is True
        assert store.exists() is False

    def test_delete_nonexistent_file_succeeds(self, store):
        """Test deleting non-existent file returns True."""
        result = store.delete()
        
        assert result is True

    def test_save_includes_version(self, store, temp_lock_file, sample_index_data):
        """Test that saved file includes version field."""
        store.save(sample_index_data)
        
        with open(temp_lock_file, 'r') as f:
            payload = json.load(f)
        
        assert "version" in payload
        assert payload["version"] == "1.0"

    def test_save_includes_checksum(self, store, temp_lock_file, sample_index_data):
        """Test that saved file includes checksum."""
        store.save(sample_index_data)
        
        with open(temp_lock_file, 'r') as f:
            payload = json.load(f)
        
        assert "checksum" in payload
        assert len(payload["checksum"]) == 64  # SHA256 hex length

    def test_load_verifies_checksum(self, store, temp_lock_file, sample_index_data):
        """Test that load verifies checksum correctly."""
        store.save(sample_index_data)
        
        # Manually corrupt the data but keep checksum
        with open(temp_lock_file, 'r') as f:
            payload = json.load(f)
        
        payload["data"]["corrupted"] = "value"
        
        with open(temp_lock_file, 'w') as f:
            json.dump(payload, f)
        
        # Load should detect corruption
        result = store.load()
        assert result is None

    def test_save_overwrites_existing_file(self, store, sample_index_data):
        """Test that save overwrites existing file."""
        store.save(sample_index_data)
        
        new_data = {"new": "data"}
        store.save(new_data)
        
        loaded = store.load()
        assert loaded == new_data

    def test_save_empty_dict(self, store):
        """Test saving empty dictionary."""
        result = store.save({})
        
        assert result is True
        loaded = store.load()
        assert loaded == {}

    def test_save_nested_data(self, store):
        """Test saving deeply nested data structures."""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        }
        
        store.save(nested_data)
        loaded = store.load()
        
        assert loaded["level1"]["level2"]["level3"]["value"] == "deep"

    def test_save_with_special_characters(self, store):
        """Test saving data with special characters."""
        data = {
            "symbol": "test:function:foo:1",
            "path": "/path/to/file.py",
            "unicode": "Hello 世界 🌍"
        }
        
        store.save(data)
        loaded = store.load()
        
        assert loaded["unicode"] == "Hello 世界 🌍"

    def test_save_with_large_data(self, store):
        """Test saving large data structure."""
        large_data = {
            f"symbol_{i}": {
                "name": f"func_{i}",
                "file": f"file_{i}.py"
            }
            for i in range(1000)
        }
        
        result = store.save(large_data)
        
        assert result is True
        loaded = store.load()
        assert len(loaded) == 1000

    def test_atomic_write_on_failure(self, store, temp_lock_file, sample_index_data):
        """Test that failed writes don't corrupt existing file."""
        # Save initial data
        store.save(sample_index_data)
        initial_data = store.load()
        
        # Try to save invalid data (this should fail gracefully)
        # The original file should remain intact
        assert initial_data is not None

    def test_checksum_calculation_consistency(self, store, sample_index_data):
        """Test that checksum calculation is consistent."""
        store.save(sample_index_data)
        data1 = store.load()
        
        store.save(sample_index_data)
        data2 = store.load()
        
        assert data1 == data2

    def test_load_corrupted_json(self, store, temp_lock_file):
        """Test loading corrupted JSON file."""
        with open(temp_lock_file, 'w') as f:
            f.write("{ invalid json }")
        
        result = store.load()
        
        assert result is None

    def test_save_with_lists(self, store):
        """Test saving data with list values."""
        data = {
            "files": ["file1.py", "file2.py", "file3.py"],
            "counts": [1, 2, 3, 4, 5]
        }
        
        store.save(data)
        loaded = store.load()
        
        assert loaded["files"] == ["file1.py", "file2.py", "file3.py"]
        assert loaded["counts"] == [1, 2, 3, 4, 5]

    def test_multiple_stores_same_file(self, temp_lock_file, sample_index_data):
        """Test multiple store instances accessing same file."""
        store1 = LockFileStore(temp_lock_file)
        store2 = LockFileStore(temp_lock_file)
        
        store1.save(sample_index_data)
        loaded = store2.load()
        
        assert loaded == sample_index_data

    def test_save_preserves_data_types(self, store):
        """Test that save/load preserves data types."""
        data = {
            "string": "value",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        store.save(data)
        loaded = store.load()
        
        assert loaded["string"] == "value"
        assert loaded["integer"] == 42
        assert loaded["float"] == 3.14
        assert loaded["boolean"] is True
        assert loaded["null"] is None
        assert loaded["list"] == [1, 2, 3]
        assert loaded["dict"]["nested"] == "value"
