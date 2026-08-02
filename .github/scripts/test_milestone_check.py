"""
Behavioral tests for milestone_check.py.
Run with: pytest .github/scripts/test_milestone_check.py -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from milestone_check import (
    checks_m0,
    checks_m1,
    checks_m2,
    checks_m3,
    checks_m4,
    checks_m5,
    checks_m6,
    dir_has_real_files,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def all_passed(results):
    return all(c["passed"] for c in results)

def failed_names(results):
    return [c["name"] for c in results if not c["passed"]]


# ---------------------------------------------------------------------------
# M0
# ---------------------------------------------------------------------------

def test_m0_passes_with_readme_and_content(tmp_path):
    (tmp_path / "README.md").write_text("x" * 100)
    assert all_passed(checks_m0(tmp_path))


def test_m0_fails_when_readme_missing(tmp_path):
    results = checks_m0(tmp_path)
    assert not all_passed(results)
    assert any("README.md exists" in n for n in failed_names(results))


def test_m0_fails_when_readme_too_short(tmp_path):
    (tmp_path / "README.md").write_text("too short")
    results = checks_m0(tmp_path)
    assert not all_passed(results)
    assert any("meaningful content" in n for n in failed_names(results))


# ---------------------------------------------------------------------------
# dir_has_real_files
# ---------------------------------------------------------------------------

def test_dir_has_real_files_ignores_gitkeep(tmp_path):
    d = tmp_path / "data" / "raw"
    d.mkdir(parents=True)
    (d / ".gitkeep").write_text("")
    assert not dir_has_real_files(tmp_path, "data", "raw")


def test_dir_has_real_files_returns_true_with_real_file(tmp_path):
    d = tmp_path / "data" / "raw"
    d.mkdir(parents=True)
    (d / "data.csv").write_text("col1,col2\n1,2")
    assert dir_has_real_files(tmp_path, "data", "raw")


def test_dir_has_real_files_returns_false_when_dir_missing(tmp_path):
    assert not dir_has_real_files(tmp_path, "data", "raw")


def test_dir_has_real_files_finds_nested_file(tmp_path):
    # Regression test for #170: builders group raw files into subdirectories.
    d = tmp_path / "data" / "raw" / "psa" / "2026"
    d.mkdir(parents=True)
    (d / "data.csv").write_text("col1,col2\n1,2")
    assert dir_has_real_files(tmp_path, "data", "raw")


def test_dir_has_real_files_ignores_nested_gitkeep(tmp_path):
    d = tmp_path / "data" / "raw" / "source_a"
    d.mkdir(parents=True)
    (d / ".gitkeep").write_text("")
    assert not dir_has_real_files(tmp_path, "data", "raw")


# ---------------------------------------------------------------------------
# M1
# ---------------------------------------------------------------------------

def test_m1_passes_when_all_structure_present(tmp_path):
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "requirements.txt").write_text("pandas")
    (tmp_path / "README.md").write_text("x" * 100)
    assert all_passed(checks_m1(tmp_path))


def test_m1_fails_when_requirements_missing(tmp_path):
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "README.md").write_text("x" * 100)
    results = checks_m1(tmp_path)
    assert any("requirements.txt" in n for n in failed_names(results))


# ---------------------------------------------------------------------------
# M2
# ---------------------------------------------------------------------------

def test_m2_passes_with_ingest_script_and_raw_data(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "ingest.py").write_text("# ingest")
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "data.csv").write_text("a,b\n1,2")
    (tmp_path / "requirements.txt").write_text("requests")
    assert all_passed(checks_m2(tmp_path))


def test_m2_fails_when_raw_data_only_has_gitkeep(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "ingest.py").write_text("# ingest")
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / ".gitkeep").write_text("")
    (tmp_path / "requirements.txt").write_text("requests")
    results = checks_m2(tmp_path)
    assert any("data/raw" in n for n in failed_names(results))


# ---------------------------------------------------------------------------
# M3
# ---------------------------------------------------------------------------

def test_m3_passes_with_transform_script_and_processed_data(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "transform.py").write_text("# transform")
    processed = tmp_path / "data" / "processed"
    processed.mkdir(parents=True)
    (processed / "clean.csv").write_text("a,b\n1,2")
    (tmp_path / "requirements.txt").write_text("pandas")
    assert all_passed(checks_m3(tmp_path))


def test_m3_fails_when_transform_script_missing(tmp_path):
    processed = tmp_path / "data" / "processed"
    processed.mkdir(parents=True)
    (processed / "clean.csv").write_text("a,b\n1,2")
    (tmp_path / "requirements.txt").write_text("pandas")
    results = checks_m3(tmp_path)
    assert any("transform.py" in n for n in failed_names(results))


# ---------------------------------------------------------------------------
# M4
# ---------------------------------------------------------------------------

def test_m4_passes_with_notebook_present(tmp_path):
    notebooks = tmp_path / "notebooks"
    notebooks.mkdir()
    (notebooks / "analysis.ipynb").write_text("{}")
    (tmp_path / "requirements.txt").write_text("jupyter")
    assert all_passed(checks_m4(tmp_path))


def test_m4_fails_when_no_notebook(tmp_path):
    (tmp_path / "notebooks").mkdir()
    (tmp_path / "requirements.txt").write_text("jupyter")
    results = checks_m4(tmp_path)
    assert any(".ipynb" in n for n in failed_names(results))


# ---------------------------------------------------------------------------
# M5
# ---------------------------------------------------------------------------

def test_m5_fails_when_requirements_empty(tmp_path):
    (tmp_path / "requirements.txt").write_text("   ")
    notebooks = tmp_path / "notebooks"
    notebooks.mkdir()
    (notebooks / "model.ipynb").write_text("{}")
    processed = tmp_path / "data" / "processed"
    processed.mkdir(parents=True)
    (processed / "output.csv").write_text("a\n1")
    results = checks_m5(tmp_path)
    assert any("requirements.txt" in n for n in failed_names(results))


# ---------------------------------------------------------------------------
# M6
# ---------------------------------------------------------------------------

def test_m6_passes_with_dashboard_and_readme(tmp_path):
    dashboard = tmp_path / "dashboard"
    dashboard.mkdir()
    (dashboard / "index.html").write_text("<html></html>")
    (tmp_path / "requirements.txt").write_text("pandas")
    (tmp_path / "README.md").write_text("x" * 100)
    assert all_passed(checks_m6(tmp_path))


def test_m6_fails_when_dashboard_missing(tmp_path):
    (tmp_path / "requirements.txt").write_text("pandas")
    (tmp_path / "README.md").write_text("x" * 100)
    results = checks_m6(tmp_path)
    assert any("dashboard/index.html" in n for n in failed_names(results))