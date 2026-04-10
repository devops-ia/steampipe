#!/usr/bin/env python3
"""Compare two CLI snapshots and generate a semantic diff.

Usage:
    python3 scripts/compare-snapshots.py old.json new.json [--output-md diff.md] [--output-json diff.json]

Outputs:
    - JSON diff to stdout (or --output-json)
    - Markdown summary to --output-md (optional)

Exit codes:
    0 — no behavioral changes
    1 — behavioral changes detected
    2 — error
"""

import argparse
import json
import sys
from pathlib import Path


def diff_lists(old: list, new: list) -> dict:
    """Compare two sorted lists, return added/removed."""
    old_set = set(old)
    new_set = set(new)
    added = sorted(new_set - old_set)
    removed = sorted(old_set - new_set)
    return {"added": added, "removed": removed}


_SKIP_KEYS = {"version", "snapshot_date"}
_HASH_SUFFIX = "_hash"


def _array_keys(snapshot: dict) -> list[str]:
    """Return all keys whose values are lists (skip metadata/hash keys)."""
    return sorted(
        k for k, v in snapshot.items()
        if isinstance(v, list) and k not in _SKIP_KEYS
    )


def _hash_keys(snapshot: dict) -> list[str]:
    """Return all keys that are hash fields."""
    return sorted(
        k for k, v in snapshot.items()
        if isinstance(v, str) and k.endswith(_HASH_SUFFIX)
    )


def compare(old: dict, new: dict) -> dict:
    """Generate semantic diff between two snapshots (generic, works for any CLI)."""
    # Collect all array keys from both snapshots
    all_array_keys = sorted(set(_array_keys(old)) | set(_array_keys(new)))
    all_hash_keys = sorted(set(_hash_keys(old)) | set(_hash_keys(new)))

    result: dict = {
        "has_changes": False,
        "version_change": f"{old.get('version', '?')} → {new.get('version', '?')}",
        "categories": {},
        "hash_changes": [],
    }

    for key in all_array_keys:
        d = diff_lists(old.get(key, []), new.get(key, []))
        result["categories"][key] = d
        if d["added"] or d["removed"]:
            result["has_changes"] = True

    for key in all_hash_keys:
        if old.get(key) != new.get(key):
            result["hash_changes"].append(key.removesuffix(_HASH_SUFFIX).replace("_", " "))

    return result


def render_diff_table(label: str, diff: dict) -> str:
    """Render a single section's added/removed as markdown."""
    lines = []
    if diff["added"] or diff["removed"]:
        lines.append(f"\n### {label}")
        lines.append("| Change | Item |")
        lines.append("|--------|------|")
        for item in diff["removed"]:
            lines.append(f"| ❌ Removed | `{item}` |")
        for item in diff["added"]:
            lines.append(f"| ➕ Added | `{item}` |")
    return "\n".join(lines)


def render_markdown(diff: dict) -> str:
    """Render full markdown summary."""
    lines = [f"## 🔍 CLI Behavioral Changes: {diff['version_change']}\n"]

    if not diff["has_changes"] and not diff["hash_changes"]:
        lines.append("✅ **No behavioral changes detected.**")
        lines.append(
            "\nThe new version has the same CLI flags, env vars, and subcommands."
        )
        return "\n".join(lines)

    for key, section_diff in diff["categories"].items():
        label = key.replace("_", " ").title()
        table = render_diff_table(label, section_diff)
        if table:
            lines.append(table)

    if diff["hash_changes"]:
        lines.append(f"\n### Help text changes")
        lines.append(
            f"Help text changed for: {', '.join(diff['hash_changes'])}. "
            "Review `--help` output for wording/description updates."
        )

    if diff["has_changes"]:
        lines.append("\n---")
        lines.append("### ⚠️ Action needed")
        lines.append(
            "These changes may require updates to `README.md` and `Dockerfile` ENV.\n"
        )
        lines.append("@copilot Please review the behavioral changes above and:")
        lines.append("1. Update `README.md` flag and env var tables")
        lines.append("2. Update `Dockerfile` ENV section if defaults changed")
        lines.append("3. Ensure documented behavior matches the current CLI")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compare CLI snapshots")
    parser.add_argument("old", help="Path to old cli-snapshot.json")
    parser.add_argument("new", help="Path to new cli-snapshot.json")
    parser.add_argument("--output-md", help="Write markdown summary to file")
    parser.add_argument("--output-json", help="Write JSON diff to file")
    args = parser.parse_args()

    try:
        old = json.loads(Path(args.old).read_text())
        new = json.loads(Path(args.new).read_text())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    diff = compare(old, new)

    # Output JSON (flatten categories for backward compat)
    output = {k: v for k, v in diff.items() if k != "categories"}
    output.update(diff["categories"])
    diff_json = json.dumps(output, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(diff_json + "\n")
    else:
        print(diff_json)

    # Output markdown
    if args.output_md:
        md = render_markdown(diff)
        Path(args.output_md).write_text(md + "\n")

    # Exit code: 1 if behavioral changes, 0 if none
    sys.exit(1 if diff["has_changes"] else 0)


if __name__ == "__main__":
    main()
