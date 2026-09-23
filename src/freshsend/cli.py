"""Command-line interface for FreshSend."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .core import FreshnessReport, FreshSendError, inspect_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="freshsend",
        description="Stop sending yesterday's file by checking for a newer same-name copy.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="check one explicit file before sending it")
    check.add_argument("file", help="the exact file you plan to send")
    check.add_argument(
        "--against",
        required=True,
        help="directory to inspect recursively for same-name files",
    )
    check.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
        help="output format (default: text)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = inspect_file(args.file, args.against)
    except FreshSendError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.output_format == "json":
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 1 if report.status == "stale" else 0


def render_text(report: FreshnessReport) -> str:
    """Render a short human-readable pre-send decision."""

    if report.status == "fresh":
        return (
            f"FRESH: no newer copy named {report.candidate.path.name!r} was found.\n"
            f"candidate: {report.candidate.path}\n"
            f"checked same-name files: {report.same_name_count}"
        )

    lines = [
        f"STALE: a newer copy named {report.candidate.path.name!r} exists.",
        f"candidate: {report.candidate.path}",
        "newer copies:",
    ]
    lines.extend(f"- {snapshot.path} ({snapshot.mtime_iso})" for snapshot in report.newer)
    lines.append("action: inspect the newer path before sending this file")
    return "\n".join(lines)
