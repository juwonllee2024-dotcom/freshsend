"""Read-only freshness checks for explicitly selected files."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

FreshnessStatus = Literal["fresh", "stale"]


class FreshSendError(ValueError):
    """A safe, user-actionable input or filesystem error."""


@dataclass(frozen=True)
class FileSnapshot:
    """The observable metadata captured for one regular file."""

    path: Path
    size: int
    mtime_ns: int
    sha256: str

    @property
    def mtime_iso(self) -> str:
        """Return the modification time in a stable UTC representation."""

        return datetime.fromtimestamp(self.mtime_ns / 1_000_000_000, tz=timezone.utc).isoformat()

    def as_dict(self) -> dict[str, object]:
        """Return JSON-safe snapshot data."""

        return {
            "path": str(self.path),
            "size": self.size,
            "mtime_ns": self.mtime_ns,
            "mtime_utc": self.mtime_iso,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class FreshnessReport:
    """The result of comparing a candidate to same-named files."""

    candidate: FileSnapshot
    against: Path
    status: FreshnessStatus
    same_name_count: int
    newer: tuple[FileSnapshot, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a stable machine-readable report."""

        return {
            "status": self.status,
            "candidate": self.candidate.as_dict(),
            "against": str(self.against),
            "same_name_count": self.same_name_count,
            "newer": [snapshot.as_dict() for snapshot in self.newer],
        }


def inspect_file(candidate: Path | str, against: Path | str) -> FreshnessReport:
    """Check whether an explicit file is older than a same-named file.

    The function only reads metadata and file contents for SHA-256 calculation. It
    never writes, uploads, follows symlinks, launches processes, or contacts a
    network service.
    """

    candidate_path = _regular_file(candidate, label="candidate")
    against_path = _directory(against)
    candidate_snapshot = _snapshot(candidate_path)
    matches = tuple(_same_name_files(against_path, candidate_path.name, candidate_path))
    snapshots = tuple(_snapshot(path) for path in matches)
    newer = tuple(
        sorted(
            (snapshot for snapshot in snapshots if snapshot.mtime_ns > candidate_snapshot.mtime_ns),
            key=lambda snapshot: (snapshot.mtime_ns, str(snapshot.path)),
            reverse=True,
        )
    )
    status: FreshnessStatus = "stale" if newer else "fresh"
    return FreshnessReport(
        candidate=candidate_snapshot,
        against=against_path,
        status=status,
        same_name_count=len(snapshots),
        newer=newer,
    )


def _regular_file(path_value: Path | str, *, label: str) -> Path:
    path = Path(path_value).expanduser()
    if path.is_symlink():
        raise FreshSendError(f"{label} must not be a symlink: {path}")
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise FreshSendError(f"cannot resolve {label}: {path} ({error})") from error
    if not resolved.is_file():
        raise FreshSendError(f"{label} is not a regular file: {path}")
    return resolved


def _directory(path_value: Path | str) -> Path:
    path = Path(path_value).expanduser()
    if path.is_symlink():
        raise FreshSendError(f"comparison directory must not be a symlink: {path}")
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise FreshSendError(f"cannot resolve comparison directory: {path} ({error})") from error
    if not resolved.is_dir():
        raise FreshSendError(f"comparison path is not a directory: {path}")
    return resolved


def _same_name_files(directory: Path, filename: str, candidate: Path) -> list[Path]:
    matches: list[Path] = []

    def on_walk_error(error: OSError) -> None:
        raise FreshSendError(f"cannot inspect {directory}: {error}") from error

    for root, dirs, files in os.walk(
        directory, topdown=True, followlinks=False, onerror=on_walk_error
    ):
        root_path = Path(root)
        dirs[:] = [name for name in dirs if not (root_path / name).is_symlink()]
        for name in files:
            if name != filename:
                continue
            path = root_path / name
            if path.is_symlink():
                continue
            try:
                resolved = path.resolve(strict=True)
            except OSError as error:
                raise FreshSendError(f"cannot inspect matching file: {path} ({error})") from error
            if resolved == candidate:
                continue
            if resolved.is_file():
                matches.append(resolved)
    return matches


def _snapshot(path: Path) -> FileSnapshot:
    try:
        stat = path.stat()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise FreshSendError(f"cannot read file: {path} ({error})") from error
    return FileSnapshot(
        path=path,
        size=stat.st_size,
        mtime_ns=stat.st_mtime_ns,
        sha256=digest.hexdigest(),
    )
