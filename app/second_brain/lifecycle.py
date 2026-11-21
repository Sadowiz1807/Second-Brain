"""File lifecycle: journal before I/O, exclusive destinations, no overwrite.

An interrupted operation remains blocked for explicit recovery. Startup never
silently deletes either copy. DB write transactions serialize catalog writers.
"""

from pathlib import Path
import hashlib
import os
import shutil
import uuid
from .locking import serialized_write


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def move_exclusive(source, target):
    source, target = Path(source), Path(target)
    if source.is_symlink() or not source.is_file():
        raise ValueError("Nguồn không phải file thường hoặc đã thay đổi")
    before = source.stat()
    checksum = digest(source)
    # Exclusive create also protects against a destination appearing after preflight.
    with target.open("xb") as output:
        with source.open("rb") as stream:
            shutil.copyfileobj(stream, output)
        output.flush()
        os.fsync(output.fileno())
    after = source.stat()
    if (
        (before.st_size, before.st_mtime_ns, before.st_ino)
        != (after.st_size, after.st_mtime_ns, after.st_ino)
        or digest(source) != checksum
        or digest(target) != checksum
    ):
        raise ValueError("File đổi trong khi di chuyển; giữ cả hai bản để kiểm tra")
    source.unlink()


class Lifecycle:
    def __init__(self, catalog):
        self.catalog = catalog
        self.trash_dir = catalog.database.parent / "trash"
        self.trash_dir.mkdir(exist_ok=True)
        with catalog.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS trash_entries (
                    document_id TEXT PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
                    stored_path TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS file_operations (
                    document_id TEXT PRIMARY KEY, action TEXT NOT NULL,
                    source TEXT NOT NULL, target TEXT, error TEXT
                );
            """)

    def document(self, identifier):
        with self.catalog.connect() as db:
            row = db.execute(
                "SELECT * FROM documents WHERE id=?", (identifier,)
            ).fetchone()
        if not row:
            raise ValueError("Không tìm thấy tài liệu")
        return dict(row)

    @serialized_write
    def perform(self, identifier, action, destination=None):
        if action not in ("trash", "restore", "purge"):
            raise ValueError("Thao tác không hợp lệ")
        doc = self.document(identifier)
        from .storage import contained

        storage = self.catalog.database.parent / "storage"
        contained(Path(doc["path"]), storage)
        with self.catalog.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute(
                "SELECT 1 FROM file_operations WHERE document_id=?", (identifier,)
            ).fetchone():
                raise ValueError(
                    "Tài liệu có thao tác gián đoạn cần kiểm tra; không tự xóa bản còn lại"
                )
            entry = db.execute(
                "SELECT stored_path FROM trash_entries WHERE document_id=?",
                (identifier,),
            ).fetchone()
            if action == "trash":
                if entry:
                    raise ValueError("Tài liệu đã ở thùng rác")
                source = Path(doc["path"])
                bucket = self.trash_dir / str(uuid.uuid4())
                bucket.mkdir()
                target = bucket / doc["name"]
            else:
                if not entry:
                    raise ValueError("Tài liệu không ở thùng rác")
                source = contained(Path(entry["stored_path"]), self.trash_dir)
                target = (
                    Path(destination or doc["path"]).expanduser().resolve()
                    if action == "restore"
                    else None
                )
                if target:
                    target = contained(target, storage)
                    if target.exists() or not target.parent.is_dir():
                        raise ValueError(
                            "restore_conflict: Đích đã tồn tại hoặc thư mục không còn; chọn vị trí khác"
                        )
                    if target.suffix.lower() != doc["extension"]:
                        raise ValueError("Giữ nguyên phần mở rộng khi khôi phục")
                    duplicate = db.execute(
                        "SELECT id FROM documents WHERE path_key=? AND id<>?",
                        (os.path.normcase(str(target)), identifier),
                    ).fetchone()
                    if duplicate:
                        raise ValueError("Đích thuộc tài liệu khác")
            if not source.is_file() or source.is_symlink():
                raise ValueError("Không tìm thấy file nguồn hợp lệ")
            db.execute(
                "INSERT INTO file_operations VALUES (?,?,?,?,NULL)",
                (identifier, action, str(source), str(target) if target else None),
            )
        try:
            if action == "purge":
                source.unlink()
            else:
                move_exclusive(source, target)
            with self.catalog.connect() as db:
                if action == "trash":
                    db.execute(
                        "INSERT INTO trash_entries VALUES (?,?)",
                        (identifier, str(target)),
                    )
                elif action == "restore":
                    db.execute(
                        "DELETE FROM trash_entries WHERE document_id=?", (identifier,)
                    )
                    db.execute(
                        "UPDATE documents SET path=?,path_key=?,name=? WHERE id=?",
                        (
                            str(target),
                            os.path.normcase(str(target)),
                            target.name,
                            identifier,
                        ),
                    )
                else:
                    db.execute("DELETE FROM documents WHERE id=?", (identifier,))
                db.execute(
                    "DELETE FROM file_operations WHERE document_id=?", (identifier,)
                )
        except Exception as exc:
            with self.catalog.connect() as db:
                db.execute(
                    "UPDATE file_operations SET error=? WHERE document_id=?",
                    (str(exc), identifier),
                )
            raise

    def unregister(self, identifier):
        self.perform(identifier, "trash")

    @serialized_write
    def relink(self, identifier, path):
        from .catalog import SUPPORTED
        from .storage import contained

        target = contained(
            Path(path).expanduser(), self.catalog.database.parent / "storage"
        )
        contained(
            Path(self.document(identifier)["path"]),
            self.catalog.database.parent / "storage",
        )
        if not target.is_file() or target.suffix.lower() not in SUPPORTED:
            raise ValueError("File không được hỗ trợ")
        with target.open("rb") as stream:
            stream.read(1)
        with self.catalog.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._active(db, identifier)
            key = os.path.normcase(str(target))
            if db.execute(
                "SELECT 1 FROM documents WHERE path_key=? AND id<>?", (key, identifier)
            ).fetchone():
                raise ValueError("File đã thuộc tài liệu khác")
            db.execute(
                "UPDATE documents SET path=?,path_key=?,name=?,extension=? WHERE id=?",
                (str(target), key, target.name, target.suffix.lower(), identifier),
            )

    @staticmethod
    def _active(db, identifier):
        if not db.execute(
            "SELECT 1 FROM documents WHERE id=?", (identifier,)
        ).fetchone():
            raise ValueError("Không tìm thấy tài liệu")
        if (
            db.execute(
                "SELECT 1 FROM trash_entries WHERE document_id=?", (identifier,)
            ).fetchone()
            or db.execute(
                "SELECT 1 FROM file_operations WHERE document_id=?", (identifier,)
            ).fetchone()
        ):
            raise ValueError("Tài liệu ở thùng rác hoặc cần phục hồi thao tác")
