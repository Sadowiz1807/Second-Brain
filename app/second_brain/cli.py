import argparse
import json
import sys
from pathlib import Path
from .configuration import load_settings
from .catalog import Catalog


def main():
    parser = argparse.ArgumentParser(
        prog="sb", description="Second Brain local workspace"
    )
    parser.add_argument("--config", help="Đường dẫn config.yaml")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run", help="Mở cửa sổ Second Brain")
    sub.add_parser("doctor", help="Kiểm tra cấu hình và runtime, không mở UI")
    args = parser.parse_args()
    try:
        settings = load_settings(args.config)
        if args.command == "doctor":
            import importlib.metadata

            print(
                json.dumps(
                    {
                        "config": str(settings.config_path),
                        "data_dir": str(settings.data_dir),
                        "python": sys.executable,
                        "pywebview": importlib.metadata.version("pywebview"),
                        "stage": "catalog-ui; MCP/RAG/trash not implemented",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        launch(settings)
        return 0
    except (ValueError, OSError, ImportError) as exc:
        print(f"SB: {exc}", file=sys.stderr)
        return 1


def launch(settings):
    import webview

    catalog = Catalog(settings.data_dir)
    from .lifecycle import Lifecycle

    lifecycle = Lifecycle(catalog)
    from .storage import Storage, contained

    storage = Storage(catalog)
    from .import_picker import ImportPicker

    picker = ImportPicker(storage)
    from .folders import Folders

    folders = Folders(catalog, storage, lifecycle)

    class Bridge:
        def browse_import(self, location=None):
            try:
                return {"ok": True, "data": picker.browse(location)}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

        def import_selection(self, directory, names, destination=""):
            try:
                return {
                    "ok": True,
                    "results": picker.import_selection(directory, names, destination),
                }
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

        def get_state(self):
            try:
                data = catalog.snapshot()
                data["folders"] = storage.folders()
                data["storage_root"] = str(storage.root)
                data["folder_trash"] = folders.entries()
                return {"ok": True, "data": data}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

        def preview(self, identifier):
            from .preview import preview

            try:
                return {"ok": True, "data": preview(catalog, identifier)}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

        def restore_folder(self, identifier):
            try:
                folders.restore(identifier)
                return {"ok": True}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

        def delete_folder(self, relative):
            try:
                target = contained(storage.root / relative, storage.root)
                confirmation_message = (
                    str(target)
                    + "\nBao gồm tất cả nội dung bên trong. File nguồn import không bị tác động."
                )
                confirmed = window.create_confirmation_dialog(
                    "Đưa cả thư mục vào thùng rác?", confirmation_message
                )
                if not confirmed:
                    return {"ok": True, "cancelled": True}
                folders.trash(relative)
                return {"ok": True}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

        def create_folder(self, relative):
            try:
                return {"ok": True, "folder": storage.create_folder(relative)}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

        def choose_folder(self, relative=""):
            try:
                paths = window.create_file_dialog(webview.FileDialog.FOLDER)
                return storage.import_folder(paths[0], relative) if paths else []
            except Exception as exc:
                return [{"ok": False, "error": str(exc)}]

        def choose_files(self, relative=""):
            paths = window.create_file_dialog(
                webview.FileDialog.OPEN, allow_multiple=True
            )
            results = []
            for path in paths or []:
                try:
                    imported_document = storage.import_file(path, relative)
                    result = {"path": path, "ok": True, **imported_document}
                    results.append(result)
                except (ValueError, OSError) as exc:
                    results.append({"path": path, "ok": False, "error": str(exc)})
            return results

        def action(self, identifier, action):
            import os
            import subprocess

            try:
                doc = lifecycle.document(identifier)
                contained(Path(doc["path"]), storage.root)
                if action in ("trash", "purge", "unregister"):
                    labels = {
                        "trash": "Di chuyển bản sao trong storage vào thùng rác",
                        "purge": "Xóa vĩnh viễn, không thể hoàn tác",
                        "unregister": "Bỏ quản lý và tag; giữ nguyên file gốc",
                    }
                    if not window.create_confirmation_dialog(
                        labels[action], doc["path"]
                    ):
                        return {"ok": True, "cancelled": True}
                if action == "unregister":
                    lifecycle.unregister(identifier)
                elif action == "relink":
                    paths = window.create_file_dialog(
                        webview.FileDialog.OPEN, allow_multiple=False
                    )
                    if paths and window.create_confirmation_dialog(
                        "Cập nhật vị trí, giữ ID và tag?", paths[0]
                    ):
                        lifecycle.relink(identifier, paths[0])
                elif action == "restore_as":
                    path = window.create_file_dialog(
                        webview.FileDialog.SAVE, save_filename=doc["name"]
                    )
                    if path:
                        destination = path if isinstance(path, str) else path[0]
                        lifecycle.perform(identifier, "restore", destination)
                elif action in ("trash", "restore", "purge"):
                    lifecycle.perform(identifier, action)
                elif action == "open":
                    with catalog.connect() as db:
                        lifecycle._active(db, identifier)
                    if not Path(doc["path"]).is_file():
                        raise ValueError("Không tìm thấy file")
                    if sys.platform == "win32":
                        os.startfile(doc["path"])
                    else:
                        subprocess.Popen(["xdg-open", doc["path"]])
                else:
                    raise ValueError("Thao tác không hợp lệ")
                return {"ok": True}
            except Exception as exc:
                return {"ok": False, "error": str(exc)}

        def set_tags(self, identifier, tags):
            try:
                catalog.set_tags(identifier, tags)
                return {"ok": True}
            except (ValueError, OSError) as exc:
                return {"ok": False, "error": str(exc)}

    page = Path(__file__).parent / "desktop" / "index.html"
    window = webview.create_window(
        "Second Brain",
        str(page),
        js_api=Bridge(),
        width=1280,
        height=800,
        min_size=(960, 640),
        background_color="#070b18",
    )
    webview.start(debug=False)


if __name__ == "__main__":
    raise SystemExit(main())
