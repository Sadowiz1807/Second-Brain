"""Persist one validated background copy without touching the source image."""

import base64
import io
import os
import uuid

from PIL import Image

from .locking import data_lock
from .storage import contained


class Background:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.directory = data_dir / "appearance"
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = contained(self.directory / "background.png", data_dir)

    def current(self):
        with data_lock(self.data_dir):
            contained(self.path, self.data_dir)
            if not self.path.exists():
                return None
            return "data:image/png;base64," + base64.b64encode(
                self.path.read_bytes()
            ).decode("ascii")

    def replace(self, source):
        if source.suffix.lower() not in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
            ".gif",
        }:
            raise ValueError("Chỉ hỗ trợ PNG, JPG, JPEG, WebP, BMP, GIF")
        if source.stat().st_size > 25 * 1024 * 1024:
            raise ValueError("Ảnh background tối đa 25 MB")
        with Image.open(source) as image:
            if image.width * image.height > 20_000_000:
                raise ValueError("Ảnh background tối đa 20 triệu pixel")
            image.seek(0)
            output = io.BytesIO()
            image.convert("RGB").save(output, format="PNG")
        content = output.getvalue()
        with data_lock(self.data_dir):
            contained(self.path, self.data_dir)
            temporary = contained(self.directory / f"{uuid.uuid4()}.tmp", self.data_dir)
            try:
                with temporary.open("xb") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, self.path)
            finally:
                temporary.unlink(missing_ok=True)
        return self.current()
