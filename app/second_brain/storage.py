"""Managed copies. Never delete or modify import sources."""

from pathlib import Path
import os
import shutil
import hashlib


def contained(path, root):
    path, root = Path(path), Path(root).resolve()
    resolved = path.resolve()
    if resolved == root or not resolved.is_relative_to(root):
        raise ValueError("Đường dẫn phải nằm trong kho SB")
    current = path.absolute()
    while current != current.parent:
        if current.is_symlink() or (
            hasattr(current, "is_junction") and current.is_junction()
        ):
            raise ValueError("Không chấp nhận symlink/junction trong đường dẫn kho")
        if current == root:
            break
        current = current.parent
    return resolved


class Storage:
    def __init__(self, catalog):
        self.catalog = catalog
        self.root = catalog.database.parent / "storage"
        self.root.mkdir(exist_ok=True)
        if self.root.is_symlink() or (
            hasattr(self.root, "is_junction") and self.root.is_junction()
        ):
            raise ValueError("storage không được là symlink/junction")

    def folder(self, relative=""):
        if (
            not isinstance(relative, str)
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
        ):
            raise ValueError("Thư mục đích không hợp lệ")
        target = (
            self.root if not relative else contained(self.root / relative, self.root)
        )
        if not target.is_dir():
            raise ValueError("Thư mục đích không tồn tại")
        return target

    def folders(self):
        result = [""]
        for parent, dirs, _ in os.walk(self.root, followlinks=False):
            safe_directories = []
            for name in dirs:
                child = Path(parent) / name
                is_junction = hasattr(child, "is_junction") and child.is_junction()
                if not child.is_symlink() and not is_junction:
                    safe_directories.append(name)

            dirs[:] = safe_directories
            result.extend(
                str((Path(parent) / name).relative_to(self.root)) for name in dirs
            )
        return sorted(result)

    def create_folder(self, relative):
        target = contained(self.root / relative, self.root)
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("Tên thư mục không hợp lệ")
        target.mkdir(parents=True, exist_ok=False)
        return str(target.relative_to(self.root))

    def import_file(self, source, relative=""):
        from .catalog import SUPPORTED

        source = Path(source)
        if source.is_symlink() or not source.is_file():
            raise ValueError("Nguồn không phải file thường hoặc là symlink")
        if source.suffix.lower() not in SUPPORTED:
            raise ValueError("Định dạng chưa được hỗ trợ")
        source = source.resolve()
        if source.is_relative_to(self.catalog.database.parent.resolve()):
            raise ValueError("Không nhập lại file trong data directory của SB")
        target = contained(self.folder(relative) / source.name, self.root)
        if target.exists():
            raise ValueError(f"Xung đột tên, không lưu: {target.name}")
        before = source.stat()
        created = False
        try:
            with target.open("xb") as output:
                created = True
                with source.open("rb") as stream:
                    shutil.copyfileobj(stream, output)
                output.flush()
                os.fsync(output.fileno())
            after = source.stat()
            with source.open("rb") as source_stream, target.open("rb") as target_stream:
                source_digest = hashlib.file_digest(source_stream, "sha256").digest()
                target_digest = hashlib.file_digest(target_stream, "sha256").digest()

            content_matches = source_digest == target_digest
            original_metadata = (before.st_size, before.st_mtime_ns)
            current_metadata = (after.st_size, after.st_mtime_ns)
            source_changed = original_metadata != current_metadata

            if not content_matches or source_changed:
                raise ValueError("Nguồn thay đổi trong lúc copy; không lưu")
            return self.catalog.register(str(target))
        except Exception:
            if created:
                target.unlink(missing_ok=True)
            raise

    def import_folder(self, source, relative=""):
        source = Path(source)
        if source.is_symlink() or not source.is_dir():
            raise ValueError("Nguồn phải là thư mục thường")
        source = source.resolve()
        data = self.catalog.database.parent.resolve()
        if source.is_relative_to(data) or data.is_relative_to(source):
            raise ValueError(
                "Không nhập cây thư mục chứa hoặc nằm trong data directory"
            )
        base = contained(self.folder(relative) / source.name, self.root)
        results = []

        def walk_error(exc):
            results.append({"path": str(exc.filename), "ok": False, "error": str(exc)})

        for parent, dirs, files in os.walk(
            source, followlinks=False, onerror=walk_error
        ):
            for name in dirs[:]:
                child = Path(parent) / name
                if child.is_symlink() or (
                    hasattr(child, "is_junction") and child.is_junction()
                ):
                    dirs.remove(name)
                    results.append(
                        {
                            "path": str(child),
                            "ok": False,
                            "error": "Bỏ qua symlink/junction",
                        }
                    )
            target_dir = base / Path(parent).relative_to(source)
            try:
                contained(target_dir, self.root).mkdir(parents=True, exist_ok=True)
            except (OSError, ValueError) as exc:
                results.append({"path": str(parent), "ok": False, "error": str(exc)})
                dirs[:] = []
                continue
            for name in files:
                path = Path(parent) / name
                try:
                    result = self.import_file(
                        path, str(target_dir.relative_to(self.root))
                    )
                    results.append({"path": str(path), "ok": True, **result})
                except (OSError, ValueError) as exc:
                    results.append({"path": str(path), "ok": False, "error": str(exc)})
        return results
