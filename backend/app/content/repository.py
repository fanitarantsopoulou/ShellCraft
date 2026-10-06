"""In-memory access to the loaded content bundle.

The site currently serves content straight from the content/ tree (no database). The bundle
is loaded once and reloaded automatically when a file under content/ changes.
"""

import threading
from pathlib import Path

from app.content.loader import ContentBundle, load_content
from app.core.config import get_settings

_lock = threading.Lock()
_cache: tuple[float, ContentBundle] | None = None


def _latest_mtime(root: Path) -> float:
    return max((p.stat().st_mtime for p in root.rglob("*") if p.is_file()), default=0.0)


def get_bundle() -> ContentBundle:
    global _cache
    root = Path(get_settings().content_dir)
    mtime = _latest_mtime(root)
    with _lock:
        if _cache is None or _cache[0] != mtime:
            _cache = (mtime, load_content(root))
        return _cache[1]
