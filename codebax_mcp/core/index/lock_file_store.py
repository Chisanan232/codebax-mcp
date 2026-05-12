"""Lock file persistence for symbol index."""

import hashlib
import json
import os
import tempfile
from typing import Any


class LockFileStore:
    """Persist symbol index to lock file with atomic writes and checksum verification."""

    def __init__(self, lock_file_path: str = ".codebax_index.lock"):
        self.lock_file_path = lock_file_path

    def save(self, index_data: dict[str, Any]) -> bool:
        """Save index to lock file with atomic write."""
        try:
            # Create temporary file in same directory for atomic rename
            lock_dir = os.path.dirname(self.lock_file_path) or "."
            with tempfile.NamedTemporaryFile(mode="w", dir=lock_dir, delete=False, suffix=".tmp") as tmp_file:
                tmp_path = tmp_file.name

                # Add checksum to data
                data_str = json.dumps(index_data, default=str)
                checksum = hashlib.sha256(data_str.encode()).hexdigest()

                payload = {"version": "1.0", "checksum": checksum, "data": index_data}

                json.dump(payload, tmp_file, default=str, indent=2)

            # Atomic rename
            if os.path.exists(self.lock_file_path):
                os.remove(self.lock_file_path)
            os.rename(tmp_path, self.lock_file_path)

            return True
        except Exception as e:
            print(f"Error saving lock file: {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return False

    def load(self) -> dict[str, Any] | None:
        """Load index from lock file with checksum verification."""
        if not os.path.exists(self.lock_file_path):
            return None

        try:
            with open(self.lock_file_path) as f:
                payload = json.load(f)

            # Verify checksum
            stored_checksum = payload.get("checksum")
            data = payload.get("data", {})

            data_str = json.dumps(data, default=str)
            computed_checksum = hashlib.sha256(data_str.encode()).hexdigest()

            if stored_checksum != computed_checksum:
                print("Checksum mismatch - index may be corrupted")
                return None

            return data
        except Exception as e:
            print(f"Error loading lock file: {e}")
            return None

    def exists(self) -> bool:
        """Check if lock file exists."""
        return os.path.exists(self.lock_file_path)

    def delete(self) -> bool:
        """Delete lock file."""
        try:
            if os.path.exists(self.lock_file_path):
                os.remove(self.lock_file_path)
            return True
        except Exception as e:
            print(f"Error deleting lock file: {e}")
            return False
