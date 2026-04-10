"""Unit tests for scripts/compare-snapshots.py."""

import json
import sys
from pathlib import Path

import pytest

from compare_snapshots import compare, diff_lists, render_markdown


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def steampipe_snapshot_v1():
    return {
        "version": "2.4.1",
        "snapshot_date": "2026-01-01",
        "subcommands": ["completion", "login", "plugin", "query", "service"],
        "service_start_flags": ["--database-listen", "--database-port", "--foreground", "--help", "--show-password"],
        "query_flags": ["--export", "--help", "--output", "--search-path", "--timing"],
        "plugin_flags": ["--help", "--progress"],
        "env_vars": ["STEAMPIPE_CACHE", "STEAMPIPE_TELEMETRY", "STEAMPIPE_UPDATE_CHECK"],
        "help_text_hash": "abc123",
        "service_help_hash": "def456",
        "query_help_hash": "ghi789",
    }


@pytest.fixture
def steampipe_snapshot_v2_no_changes(steampipe_snapshot_v1):
    """Same content, just different version label."""
    return {**steampipe_snapshot_v1, "version": "2.5.0"}


@pytest.fixture
def steampipe_snapshot_v2_with_changes():
    return {
        "version": "2.5.0",
        "snapshot_date": "2026-02-01",
        "subcommands": ["completion", "login", "plugin", "query", "service", "workspace"],
        "service_start_flags": ["--database-listen", "--database-port", "--foreground", "--help"],
        "query_flags": ["--export", "--help", "--output", "--search-path", "--timing", "--var"],
        "plugin_flags": ["--help", "--progress"],
        "env_vars": ["STEAMPIPE_CACHE", "STEAMPIPE_NEW_VAR", "STEAMPIPE_UPDATE_CHECK"],
        "help_text_hash": "changed_hash",
        "service_help_hash": "def456",
        "query_help_hash": "ghi789",
    }


@pytest.fixture
def powerpipe_snapshot_v1():
    """Powerpipe uses different key names — tests the dynamic detection."""
    return {
        "version": "1.5.1",
        "snapshot_date": "2026-01-01",
        "subcommands": ["benchmark", "completion", "mod", "server"],
        "server_flags": ["--help", "--listen", "--port"],
        "benchmark_run_flags": ["--dry-run", "--export", "--help", "--output"],
        "mod_flags": ["--help"],
        "env_vars": ["POWERPIPE_LISTEN", "POWERPIPE_PORT"],
        "help_text_hash": "pp_abc",
        "server_help_hash": "pp_def",
        "benchmark_help_hash": "pp_ghi",
    }


# ---------------------------------------------------------------------------
# diff_lists
# ---------------------------------------------------------------------------

class TestDiffLists:
    def test_added_items(self):
        d = diff_lists(["a", "b"], ["a", "b", "c"])
        assert d["added"] == ["c"]
        assert d["removed"] == []

    def test_removed_items(self):
        d = diff_lists(["a", "b", "c"], ["a", "b"])
        assert d["added"] == []
        assert d["removed"] == ["c"]

    def test_both_added_and_removed(self):
        d = diff_lists(["a", "b"], ["b", "c"])
        assert d["added"] == ["c"]
        assert d["removed"] == ["a"]

    def test_no_changes(self):
        d = diff_lists(["a", "b"], ["a", "b"])
        assert d["added"] == []
        assert d["removed"] == []

    def test_empty_lists(self):
        d = diff_lists([], [])
        assert d["added"] == []
        assert d["removed"] == []

    def test_result_is_sorted(self):
        d = diff_lists(["z", "a"], ["z", "b", "c"])
        assert d["added"] == ["b", "c"]
        assert d["removed"] == ["a"]


# ---------------------------------------------------------------------------
# compare — no changes
# ---------------------------------------------------------------------------

class TestCompareNoChanges:
    def test_identical_snapshots_has_no_changes(self, steampipe_snapshot_v1):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v1)
        assert result["has_changes"] is False

    def test_version_label_only_has_no_changes(self, steampipe_snapshot_v1, steampipe_snapshot_v2_no_changes):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_no_changes)
        assert result["has_changes"] is False

    def test_version_change_is_reported(self, steampipe_snapshot_v1, steampipe_snapshot_v2_no_changes):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_no_changes)
        assert "2.4.1" in result["version_change"]
        assert "2.5.0" in result["version_change"]

    def test_no_hash_changes_when_identical(self, steampipe_snapshot_v1):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v1)
        assert result["hash_changes"] == []


# ---------------------------------------------------------------------------
# compare — with behavioral changes
# ---------------------------------------------------------------------------

class TestCompareWithChanges:
    def test_has_changes_true(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        assert result["has_changes"] is True

    def test_added_subcommand_detected(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        assert "workspace" in result["categories"]["subcommands"]["added"]

    def test_removed_flag_detected(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        assert "--show-password" in result["categories"]["service_start_flags"]["removed"]

    def test_added_flag_detected(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        assert "--var" in result["categories"]["query_flags"]["added"]

    def test_added_env_var_detected(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        assert "STEAMPIPE_NEW_VAR" in result["categories"]["env_vars"]["added"]

    def test_removed_env_var_detected(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        assert "STEAMPIPE_TELEMETRY" in result["categories"]["env_vars"]["removed"]

    def test_hash_change_detected(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        result = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        assert len(result["hash_changes"]) > 0


# ---------------------------------------------------------------------------
# compare — dynamic key detection (powerpipe)
# ---------------------------------------------------------------------------

class TestCompareDynamicKeys:
    def test_powerpipe_keys_detected(self, powerpipe_snapshot_v1):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v1)
        assert "server_flags" in result["categories"]
        assert "benchmark_run_flags" in result["categories"]
        assert "mod_flags" in result["categories"]

    def test_no_hardcoded_steampipe_keys_required(self, powerpipe_snapshot_v1):
        """compare() must work with powerpipe keys, not just steampipe keys."""
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v1)
        assert result["has_changes"] is False
        # steampipe-specific keys should NOT appear if not in snapshot
        assert "service_start_flags" not in result["categories"]
        assert "query_flags" not in result["categories"]

    def test_keys_only_in_new_snapshot_are_detected(self, powerpipe_snapshot_v1):
        old = {**powerpipe_snapshot_v1}
        new = {**powerpipe_snapshot_v1, "new_category": ["item-a", "item-b"]}
        result = compare(old, new)
        assert "new_category" in result["categories"]
        assert result["categories"]["new_category"]["added"] == ["item-a", "item-b"]
        assert result["has_changes"] is True


# ---------------------------------------------------------------------------
# render_markdown
# ---------------------------------------------------------------------------

class TestRenderMarkdown:
    def test_no_changes_message(self, steampipe_snapshot_v1):
        diff = compare(steampipe_snapshot_v1, steampipe_snapshot_v1)
        md = render_markdown(diff)
        assert "No behavioral changes detected" in md
        assert "Action needed" not in md

    def test_changes_include_tables(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        diff = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        md = render_markdown(diff)
        assert "❌ Removed" in md
        assert "➕ Added" in md

    def test_changes_include_copilot_mention(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        diff = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        md = render_markdown(diff)
        assert "@copilot" in md

    def test_hash_change_section_present(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        diff = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        md = render_markdown(diff)
        assert "Help text changes" in md

    def test_version_in_header(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes):
        diff = compare(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes)
        md = render_markdown(diff)
        assert "2.4.1" in md
        assert "2.5.0" in md


class TestMain:
    """Test main() in-process via mocking to get coverage tracking."""

    def test_main_no_changes_exits_0(self, steampipe_snapshot_v1, tmp_path, monkeypatch):
        import compare_snapshots as cs
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        old_file.write_text(json.dumps(steampipe_snapshot_v1))
        new_file.write_text(json.dumps(steampipe_snapshot_v1))

        monkeypatch.setattr(sys, "argv", ["compare_snapshots.py", str(old_file), str(new_file)])
        with pytest.raises(SystemExit) as exc:
            cs.main()
        assert exc.value.code == 0

    def test_main_with_changes_exits_1(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes, tmp_path, monkeypatch):
        import compare_snapshots as cs
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        old_file.write_text(json.dumps(steampipe_snapshot_v1))
        new_file.write_text(json.dumps(steampipe_snapshot_v2_with_changes))

        monkeypatch.setattr(sys, "argv", ["compare_snapshots.py", str(old_file), str(new_file)])
        with pytest.raises(SystemExit) as exc:
            cs.main()
        assert exc.value.code == 1

    def test_main_bad_json_exits_2(self, tmp_path, monkeypatch):
        import compare_snapshots as cs
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid {{{")
        good_file = tmp_path / "good.json"
        good_file.write_text("{}")

        monkeypatch.setattr(sys, "argv", ["compare_snapshots.py", str(bad_file), str(good_file)])
        with pytest.raises(SystemExit) as exc:
            cs.main()
        assert exc.value.code == 2

    def test_main_writes_output_files(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes, tmp_path, monkeypatch):
        import compare_snapshots as cs
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        out_json = tmp_path / "diff.json"
        out_md = tmp_path / "diff.md"
        old_file.write_text(json.dumps(steampipe_snapshot_v1))
        new_file.write_text(json.dumps(steampipe_snapshot_v2_with_changes))

        monkeypatch.setattr(sys, "argv", [
            "compare_snapshots.py", str(old_file), str(new_file),
            "--output-json", str(out_json),
            "--output-md", str(out_md),
        ])
        with pytest.raises(SystemExit):
            cs.main()

        assert out_json.exists()
        assert out_md.exists()
        data = json.loads(out_json.read_text())
        assert data["has_changes"] is True
        assert "CLI Behavioral Changes" in out_md.read_text()


# ---------------------------------------------------------------------------
# CLI invocation via subprocess (exit codes)
# ---------------------------------------------------------------------------

class TestExitCodes:
    def _run(self, old_data, new_data, tmp_path):
        import subprocess
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        old_file.write_text(json.dumps(old_data))
        new_file.write_text(json.dumps(new_data))
        script = Path(__file__).parent.parent / "scripts" / "compare_snapshots.py"
        result = subprocess.run(
            [sys.executable, str(script), str(old_file), str(new_file)],
            capture_output=True,
        )
        return result

    def test_exit_0_when_no_changes(self, steampipe_snapshot_v1, tmp_path):
        result = self._run(steampipe_snapshot_v1, steampipe_snapshot_v1, tmp_path)
        assert result.returncode == 0

    def test_exit_1_when_changes(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes, tmp_path):
        result = self._run(steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes, tmp_path)
        assert result.returncode == 1

    def test_exit_2_on_missing_file(self, tmp_path):
        import subprocess
        missing = tmp_path / "missing.json"
        good_file = tmp_path / "good.json"
        good_file.write_text("{}")
        script = Path(__file__).parent.parent / "scripts" / "compare_snapshots.py"
        result = subprocess.run(
            [sys.executable, str(script), str(missing), str(good_file)],
            capture_output=True,
        )
        assert result.returncode == 2

    def test_output_json_file_written(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes, tmp_path):
        import subprocess
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        out_json = tmp_path / "diff.json"
        old_file.write_text(json.dumps(steampipe_snapshot_v1))
        new_file.write_text(json.dumps(steampipe_snapshot_v2_with_changes))
        script = Path(__file__).parent.parent / "scripts" / "compare_snapshots.py"
        subprocess.run(
            [sys.executable, str(script), str(old_file), str(new_file), "--output-json", str(out_json)],
            capture_output=True,
        )
        assert out_json.exists()
        data = json.loads(out_json.read_text())
        assert data["has_changes"] is True

    def test_output_md_file_written(self, steampipe_snapshot_v1, steampipe_snapshot_v2_with_changes, tmp_path):
        import subprocess
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        out_md = tmp_path / "diff.md"
        old_file.write_text(json.dumps(steampipe_snapshot_v1))
        new_file.write_text(json.dumps(steampipe_snapshot_v2_with_changes))
        script = Path(__file__).parent.parent / "scripts" / "compare_snapshots.py"
        subprocess.run(
            [sys.executable, str(script), str(old_file), str(new_file), "--output-md", str(out_md)],
            capture_output=True,
        )
        assert out_md.exists()
        assert "CLI Behavioral Changes" in out_md.read_text()
