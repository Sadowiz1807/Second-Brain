"""One reentrant process/thread-safe lock per data directory for SB operations.

Only cooperating SB processes honor this lock; external filesystem writers do not.
"""

from functools import wraps
from pathlib import Path
from threading import Lock

from filelock import FileLock, Timeout

_LOCKS = {}
_REGISTRY_LOCK = Lock()


def data_lock(directory):
    key = str(Path(directory).resolve())
    with _REGISTRY_LOCK:
        if key not in _LOCKS:
            Path(key).mkdir(parents=True, exist_ok=True)
            _LOCKS[key] = FileLock(str(Path(key) / ".sb-operation.lock"), timeout=10)
        return _LOCKS[key]


def require_clean_journal(catalog):
    with catalog.connect() as database:
        tables = {
            row[0]
            for row in database.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        if "file_operations" in tables:
            if database.execute("SELECT 1 FROM file_operations LIMIT 1").fetchone():
                raise ValueError(
                    "RECOVERY_REQUIRED: file operation journal is pending; no further mutations allowed"
                )
        if "folder_trash" in tables:
            if database.execute(
                "SELECT 1 FROM folder_trash WHERE state='pending' LIMIT 1"
            ).fetchone():
                raise ValueError(
                    "RECOVERY_REQUIRED: folder operation journal is pending; no further mutations allowed"
                )


def serialized_write(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        catalog = getattr(self, "catalog", self)
        try:
            with data_lock(catalog.database.parent):
                require_clean_journal(catalog)
                return method(self, *args, **kwargs)
        except Timeout as exc:
            raise ValueError(
                "STORE_BUSY: another SB operation holds the data lock"
            ) from exc

    return wrapped
