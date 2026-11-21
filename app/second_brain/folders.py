"""Move whole managed folders to trash, including empty folders/unregistered files."""

from pathlib import Path
import os
import uuid
from .storage import contained
from .locking import serialized_write


class Folders:
    def __init__(self, catalog, storage, lifecycle):
        self.catalog, self.storage, self.lifecycle = catalog, storage, lifecycle
        with catalog.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS folder_trash (id TEXT PRIMARY KEY, original TEXT NOT NULL, stored TEXT NOT NULL, state TEXT NOT NULL)"
            )

    @serialized_write
    def trash(self, relative):
        source = contained(self.storage.root / relative, self.storage.root)
        if not source.is_dir():
            raise ValueError("Không tìm thấy thư mục")
        for parent, dirs, files in os.walk(source, followlinks=False):
            for name in dirs + files:
                contained(Path(parent) / name, self.storage.root)
        identifier = str(uuid.uuid4())
        bucket = self.lifecycle.trash_dir / identifier
        bucket.mkdir()
        target = bucket / source.name
        with self.catalog.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute(
                "SELECT 1 FROM folder_trash WHERE state='pending'"
            ).fetchone():
                raise ValueError("Có thao tác thư mục cần phục hồi trước khi tiếp tục")
            docs = [
                dict(r)
                for r in db.execute("SELECT * FROM documents")
                if Path(r["path"]).resolve().is_relative_to(source)
            ]
            for doc in docs:
                if db.execute(
                    "SELECT 1 FROM file_operations WHERE document_id=?", (doc["id"],)
                ).fetchone():
                    raise ValueError("Tài liệu đang có thao tác gián đoạn")
            docs = [
                d
                for d in docs
                if not db.execute(
                    "SELECT 1 FROM trash_entries WHERE document_id=?", (d["id"],)
                ).fetchone()
            ]
            db.execute(
                "INSERT INTO folder_trash VALUES (?,?,?,?)",
                (identifier, str(source), str(target), "pending"),
            )
            for doc in docs:
                db.execute(
                    "INSERT INTO file_operations VALUES (?,?,?,?,NULL)",
                    (
                        doc["id"],
                        "folder_trash",
                        doc["path"],
                        str(target / Path(doc["path"]).relative_to(source)),
                    ),
                )
        # Same data directory/filesystem. Do not fall back to recursive deletion.
        source.rename(target)
        with self.catalog.connect() as db:
            for doc in docs:
                db.execute(
                    "INSERT INTO trash_entries VALUES (?,?)",
                    (doc["id"], str(target / Path(doc["path"]).relative_to(source))),
                )
                db.execute(
                    "DELETE FROM file_operations WHERE document_id=?", (doc["id"],)
                )
            db.execute(
                "UPDATE folder_trash SET state='ready' WHERE id=?", (identifier,)
            )

    @serialized_write
    def restore(self, identifier):
        with self.catalog.connect() as db:
            row = db.execute(
                "SELECT * FROM folder_trash WHERE id=? AND state='ready'", (identifier,)
            ).fetchone()
            if not row:
                raise ValueError("Không tìm thấy thư mục trash sẵn sàng")
            source = contained(Path(row["stored"]), self.lifecycle.trash_dir)
            target = contained(Path(row["original"]), self.storage.root)
            if target.exists() or not target.parent.is_dir():
                raise ValueError(
                    "restore_conflict: Thư mục đích tồn tại hoặc thư mục cha không còn"
                )
            entries = [
                dict(r)
                for r in db.execute("SELECT * FROM trash_entries")
                if Path(r["stored_path"]).is_relative_to(source)
            ]
            db.execute(
                "UPDATE folder_trash SET state='pending' WHERE id=?", (identifier,)
            )
        source.rename(target)
        with self.catalog.connect() as db:
            for entry in entries:
                db.execute(
                    "DELETE FROM trash_entries WHERE document_id=?",
                    (entry["document_id"],),
                )
            db.execute("DELETE FROM folder_trash WHERE id=?", (identifier,))

    def entries(self):
        with self.catalog.connect() as db:
            return [dict(r) for r in db.execute("SELECT * FROM folder_trash")]
