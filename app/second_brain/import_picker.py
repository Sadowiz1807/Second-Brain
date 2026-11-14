"""Directory browser for the local desktop import dialog."""

from pathlib import Path
import os
from .catalog import SUPPORTED


class ImportPicker:
    def __init__(self, storage):
        self.storage = storage

    def browse(self, location=None):
        directory = Path(location or Path.home()).expanduser().resolve(strict=True)
        if not directory.is_dir():
            raise ValueError("Đường dẫn không phải thư mục")
        entries = []
        with os.scandir(directory) as iterator:
            for item in iterator:
                path = Path(item.path)
                if item.is_symlink() or (
                    hasattr(path, "is_junction") and path.is_junction()
                ):
                    continue
                if item.is_dir(follow_symlinks=False):
                    entries.append({"name": item.name, "directory": True})
                elif (
                    item.is_file(follow_symlinks=False)
                    and path.suffix.lower() in SUPPORTED
                ):
                    entries.append({"name": item.name, "directory": False})
        entries.sort(key=lambda item: (not item["directory"], item["name"].casefold()))
        return {
            "path": str(directory),
            "parent": str(directory.parent),
            "entries": entries,
        }

    def import_selection(self, directory, names, destination):
        root = Path(directory).resolve(strict=True)
        if not isinstance(names, list) or any(
            not isinstance(n, str) or Path(n).name != n or n in (".", "..")
            for n in names
        ):
            raise ValueError("Lựa chọn file không hợp lệ")
        if not names:
            return self.storage.import_folder(root, destination)
        results = []
        for name in dict.fromkeys(names):
            path = root / name
            try:
                results.append(
                    {
                        "path": str(path),
                        "ok": True,
                        **self.storage.import_file(path, destination),
                    }
                )
            except (ValueError, OSError) as exc:
                results.append({"path": str(path), "ok": False, "error": str(exc)})
        return results
