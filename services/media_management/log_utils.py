# services/media_management/log_utils.py
from __future__ import annotations
import os, json, time
from pathlib import Path
from typing import Any, Dict

DEFAULT_LOG_DIR = Path("services/media_management/datasets/logs")

def ensure_log_dir(log_dir: str | os.PathLike | None = None) -> Path:
    p = Path(log_dir or DEFAULT_LOG_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p

def jsonl_append(path: str | os.PathLike, row: Dict[str, Any]) -> None:
    """Append one JSON object per line, create dirs if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # inject timestamp if missing
    row.setdefault("timestamp", int(time.time()))
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
