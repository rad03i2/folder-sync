from pathlib import Path

import pytest

from folder_sync.core import apply, plan


def test_copy_update_and_idempotence(tmp_path: Path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    (src / "a.txt").write_text("new")
    (src / "nested").mkdir(); (src / "nested" / "b.txt").write_text("B")
    (dst / "a.txt").write_text("old")
    actions = plan(src, dst)
    assert [(a.kind, a.relative_path) for a in actions] == [("update", "a.txt"), ("copy", "nested/b.txt")]
    apply(src, dst, actions)
    assert (dst / "a.txt").read_text() == "new"
    assert (dst / "nested" / "b.txt").read_text() == "B"
    assert plan(src, dst) == []


def test_delete_is_opt_in_and_protected(tmp_path: Path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.mkdir(); dst.mkdir()
    extra = dst / "extra.txt"; extra.write_text("keep")
    assert plan(src, dst) == []
    actions = plan(src, dst, delete=True)
    assert actions[0].kind == "delete"
    extra.write_text("changed after preview")
    with pytest.raises(RuntimeError, match="changed since preview"):
        apply(src, dst, actions)


def test_source_change_after_preview_is_rejected(tmp_path: Path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.mkdir()
    file = src / "a.txt"; file.write_text("one")
    actions = plan(src, dst)
    file.write_text("two")
    with pytest.raises(RuntimeError, match="changed since preview"):
        apply(src, dst, actions)


def test_nested_roots_refused(tmp_path: Path):
    src = tmp_path / "src"; src.mkdir()
    with pytest.raises(ValueError, match="Nested"):
        plan(src, src / "backup")


def test_hidden_files_default_to_excluded(tmp_path: Path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.mkdir(); (src / ".secret").write_text("x")
    assert plan(src, dst) == []
    assert plan(src, dst, include_hidden=True)[0].relative_path == ".secret"


def test_manifest_written(tmp_path: Path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.mkdir(); (src / "a.txt").write_text("x")
    manifest = tmp_path / "manifest.json"
    apply(src, dst, plan(src, dst), manifest=manifest)
    text = manifest.read_text()
    assert '"relative_path": "a.txt"' in text
    assert '"verified": true' in text
