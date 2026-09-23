from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from freshsend.cli import main
from freshsend.core import FreshSendError, inspect_file


def write_at(path: Path, content: str, mtime_ns: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    os.utime(path, ns=(mtime_ns, mtime_ns))
    return path


def test_fresh_file_has_no_newer_same_name_copy(tmp_path: Path) -> None:
    candidate = write_at(tmp_path / "selected" / "report.txt", "today", 2_000_000_000)

    report = inspect_file(candidate, tmp_path / "selected")

    assert report.status == "fresh"
    assert report.newer == ()
    assert report.same_name_count == 0


def test_stale_file_names_newer_same_name_copy(tmp_path: Path) -> None:
    candidate = write_at(tmp_path / "outgoing" / "report.txt", "old", 2_000_000_000)
    newer = write_at(tmp_path / "workspace" / "report.txt", "new", 3_000_000_000)

    report = inspect_file(candidate, tmp_path)

    assert report.status == "stale"
    assert report.newer[0].path == newer.resolve()
    assert report.same_name_count == 1


def test_symlinked_matches_are_ignored(tmp_path: Path) -> None:
    candidate = write_at(tmp_path / "outgoing" / "report.txt", "old", 2_000_000_000)
    target = write_at(tmp_path / "outside" / "report.txt", "new", 3_000_000_000)
    link = tmp_path / "workspace" / "report.txt"
    link.parent.mkdir()
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"symlink creation is unavailable: {error}")

    report = inspect_file(candidate, tmp_path)

    assert report.status == "fresh"
    assert report.same_name_count == 0


def test_symlink_candidate_is_rejected(tmp_path: Path) -> None:
    target = write_at(tmp_path / "target.txt", "content", 2_000_000_000)
    link = tmp_path / "selected.txt"
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"symlink creation is unavailable: {error}")

    with pytest.raises(FreshSendError, match="symlink"):
        inspect_file(link, tmp_path)


def test_cli_json_returns_nonzero_for_stale_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    candidate = write_at(tmp_path / "outgoing" / "report.txt", "old", 2_000_000_000)
    write_at(tmp_path / "workspace" / "report.txt", "new", 3_000_000_000)

    exit_code = main(["check", str(candidate), "--against", str(tmp_path), "--format", "json"])

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert payload["status"] == "stale"
    assert payload["newer"][0]["sha256"]
