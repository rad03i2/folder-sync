from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Action:
    kind: str
    relative_path: str
    size: int = 0
    sha256: str | None = None


def sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _files(root: Path, include_hidden: bool) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        base_path = Path(base)
        dirs[:] = [d for d in dirs if not (base_path / d).is_symlink() and (include_hidden or not d.startswith("."))]
        for name in files:
            path = base_path / name
            if path.is_symlink() or (not include_hidden and any(p.startswith(".") for p in path.relative_to(root).parts)):
                continue
            result[path.relative_to(root).as_posix()] = path
    return result


def validate_roots(source: Path, destination: Path) -> tuple[Path, Path]:
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    if not source.is_dir():
        raise ValueError(f"Source is not a directory: {source}")
    if source == destination:
        raise ValueError("Source and destination must be different")
    if source in destination.parents or destination in source.parents:
        raise ValueError("Nested source/destination paths are refused to prevent recursive sync")
    return source, destination


def plan(source: Path, destination: Path, *, delete: bool = False, include_hidden: bool = False) -> list[Action]:
    source, destination = validate_roots(source, destination)
    source_files = _files(source, include_hidden)
    destination_files = _files(destination, include_hidden) if destination.exists() else {}
    actions: list[Action] = []
    for rel, src in sorted(source_files.items()):
        dst = destination_files.get(rel)
        src_hash = sha256(src)
        if dst is None:
            actions.append(Action("copy", rel, src.stat().st_size, src_hash))
        elif src.stat().st_size != dst.stat().st_size or src_hash != sha256(dst):
            actions.append(Action("update", rel, src.stat().st_size, src_hash))
    if delete:
        for rel in sorted(destination_files.keys() - source_files.keys()):
            actions.append(Action("delete", rel, destination_files[rel].stat().st_size, sha256(destination_files[rel])))
    return actions


def _atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    os.close(fd)
    temp = Path(temp_name)
    try:
        shutil.copy2(source, temp)
        os.replace(temp, destination)
    finally:
        temp.unlink(missing_ok=True)


def apply(source: Path, destination: Path, actions: list[Action], *, verify: bool = True, manifest: Path | None = None) -> dict:
    source, destination = validate_roots(source, destination)
    destination.mkdir(parents=True, exist_ok=True)
    completed: list[dict] = []
    for action in actions:
        rel = Path(action.relative_path)
        src, dst = source / rel, destination / rel
        if action.kind in {"copy", "update"}:
            if not src.is_file() or src.is_symlink():
                raise RuntimeError(f"Source changed or is unsafe: {rel}")
            current = sha256(src)
            if action.sha256 and current != action.sha256:
                raise RuntimeError(f"Source changed since preview: {rel}")
            _atomic_copy(src, dst)
            if verify and sha256(dst) != current:
                raise RuntimeError(f"Verification failed: {rel}")
        elif action.kind == "delete":
            if dst.exists():
                if action.sha256 and sha256(dst) != action.sha256:
                    raise RuntimeError(f"Destination changed since preview: {rel}")
                dst.unlink()
        else:
            raise ValueError(f"Unknown action: {action.kind}")
        completed.append(asdict(action))
    payload = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "destination": str(destination),
        "verified": verify,
        "actions": completed,
    }
    if manifest:
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload
