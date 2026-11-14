"""Non-destructive document registration and tag graph use cases."""

from pathlib import Path
import os
import sqlite3
import unicodedata
import uuid

SUPPORTED = {
    ".txt",
    ".md",
    ".docx",
    ".doc",
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
}


def normalize_tags(tags):
    if not isinstance(tags, list) or len(tags) > 100:
        raise ValueError("tags cần là danh sách tối đa 100 tag")
    result = {}
    for value in tags:
        if not isinstance(value, str):
            raise ValueError("Tag phải là chuỗi")
        label = unicodedata.normalize("NFC", value).strip()
        if len(label) > 100:
            raise ValueError("Tag tối đa 100 ký tự")
        if label:
            result.setdefault(label.casefold(), label)
    return result


class Catalog:
    def __init__(self, data_dir: Path):
        data_dir.mkdir(parents=True, exist_ok=True)
        self.database = data_dir / "metadata.sqlite3"
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise ValueError(f"Database schema không được hỗ trợ: {version}")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY, path TEXT NOT NULL, path_key TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL, extension TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tags (key TEXT PRIMARY KEY, label TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS document_tags (
                    document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
                    tag_key TEXT REFERENCES tags(key), PRIMARY KEY(document_id, tag_key)
                );
                PRAGMA user_version=1;
            """)

    def connect(self):
        db = sqlite3.connect(self.database, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def register(self, path: str):
        source = Path(path).expanduser().resolve(strict=True)
        if not source.is_file():
            raise ValueError("Chỉ nhận file tài liệu")
        if source.suffix.lower() not in SUPPORTED:
            raise ValueError(f"Chưa hỗ trợ định dạng {source.suffix}")
        # Verify access without modifying or copying the source.
        with source.open("rb") as stream:
            stream.read(1)
        key = os.path.normcase(str(source))
        with self.connect() as db:
            previous = db.execute(
                "SELECT id FROM documents WHERE path_key=?", (key,)
            ).fetchone()
            if previous:
                return {"id": previous["id"], "duplicate": True}
            identifier = str(uuid.uuid4())
            db.execute(
                "INSERT INTO documents VALUES (?,?,?,?,?)",
                (identifier, str(source), key, source.name, source.suffix.lower()),
            )
        return {"id": identifier, "duplicate": False}

    def set_tags(self, identifier: str, tags: list[str]):
        normalized = normalize_tags(tags)
        with self.connect() as db:
            if not db.execute(
                "SELECT 1 FROM documents WHERE id=?", (identifier,)
            ).fetchone():
                raise ValueError("Không tìm thấy tài liệu")
            db.execute("DELETE FROM document_tags WHERE document_id=?", (identifier,))
            for key, label in normalized.items():
                db.execute("INSERT OR IGNORE INTO tags VALUES (?,?)", (key, label))
                db.execute("INSERT INTO document_tags VALUES (?,?)", (identifier, key))

    def snapshot(self):
        with self.connect() as db:
            documents = [
                dict(row)
                for row in db.execute(
                    "SELECT id,path,name,extension FROM documents ORDER BY name,id"
                )
            ]
            tags = [
                dict(row)
                for row in db.execute("SELECT key,label FROM tags ORDER BY label")
            ]
            relations = list(
                db.execute("SELECT document_id,tag_key FROM document_tags")
            )
            edges = [dict(row) for row in db.execute("""
                SELECT DISTINCT a.document_id AS source,b.document_id AS target
                FROM document_tags a JOIN document_tags b ON a.tag_key=b.tag_key
                WHERE a.document_id < b.document_id
            """)]
        lookup = {tag["key"]: tag["label"] for tag in tags}
        for doc in documents:
            doc["tags"] = [
                lookup[row["tag_key"]]
                for row in relations
                if row["document_id"] == doc["id"]
            ]
            try:
                with Path(doc["path"]).open("rb") as stream:
                    stream.read(1)
                doc["status"] = "available"
            except FileNotFoundError:
                doc["status"] = "missing"
            except OSError:
                doc["status"] = "unreadable"
            doc["index_status"] = "not_implemented"
        with self.connect() as db:
            exists = db.execute(
                "SELECT 1 FROM sqlite_master WHERE name='trash_entries'"
            ).fetchone()
            trash_ids = (
                {row[0] for row in db.execute("SELECT document_id FROM trash_entries")}
                if exists
                else set()
            )
            operations = (
                [dict(row) for row in db.execute("SELECT * FROM file_operations")]
                if exists
                else []
            )
        blocked = {row["document_id"] for row in operations}
        active = [doc for doc in documents if doc["id"] not in trash_ids | blocked]
        trash = [
            doc
            for doc in documents
            if doc["id"] in trash_ids and doc["id"] not in blocked
        ]
        active_ids = {doc["id"] for doc in active}
        return {
            "documents": active,
            "trash": trash,
            "operations": operations,
            "tags": tags,
            "edges": [
                edge
                for edge in edges
                if edge["source"] in active_ids and edge["target"] in active_ids
            ],
        }
