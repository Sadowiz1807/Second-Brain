"""Resolve workspace configuration independently of the caller's cwd."""

from dataclasses import dataclass
from pathlib import Path
import os
import yaml


@dataclass(frozen=True)
class Settings:
    config_path: Path
    data_dir: Path


def load_settings(path: str | Path | None = None) -> Settings:
    source = path or os.environ.get("SB_CONFIG")
    config = (
        Path(source).expanduser().resolve()
        if source
        else Path(__file__).resolve().parents[2] / "config.yaml"
    )
    if not config.is_file():
        raise ValueError(
            f"Không tìm thấy config: {config}. Dùng --config hoặc SB_CONFIG."
        )
    try:
        raw = yaml.safe_load(config.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML không hợp lệ: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("schema_version") != 1:
        raise ValueError("config cần schema_version: 1")
    if not isinstance(raw.get("agents", {}), dict):
        raise ValueError("agents phải là mapping")
    data = raw.get("data_dir", ".sb-data")
    if not isinstance(data, str) or not data.strip():
        raise ValueError("data_dir phải là đường dẫn không rỗng")
    target = Path(data).expanduser()
    if not target.is_absolute():
        target = config.parent / target
    return Settings(config, target.resolve())
