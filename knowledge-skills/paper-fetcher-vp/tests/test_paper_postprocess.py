from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "paper_postprocess.py"


def write_pdf(path: Path) -> None:
    path.write_bytes(b"%PDF-1.4\n% test pdf\n")


def run_postprocess(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_target_dir_doi_and_other_field(tmp_path: Path) -> None:
    source = tmp_path / "download.pdf"
    target_dir = tmp_path / "research"
    write_pdf(source)

    result = run_postprocess(
        "--pdf",
        str(source),
        "--target-dir",
        str(target_dir),
        "--title",
        'A/B: Test? Paper*',
        "--field",
        "Other",
        "--doi",
        "10.1234/example.paper",
        "--source-url",
        "https://publisher.example/paper",
        "--zotero",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    saved_path = Path(payload["saved_path"])

    assert payload["field"] == "Other"
    assert payload["final_name"] == "Other_A-B- Test- Paper-.pdf"
    assert payload["identifier"] == "10.1234/example.paper"
    assert payload["pdf_verified"] is True
    assert saved_path.parent == target_dir
    assert saved_path.exists()
    assert not source.exists()


def test_arxiv_identifier_preferred_over_doi(tmp_path: Path) -> None:
    source = tmp_path / "download.pdf"
    write_pdf(source)

    result = run_postprocess(
        "--pdf",
        str(source),
        "--title",
        "Preference Optimization",
        "--field",
        "RL",
        "--arxiv-id",
        "2401.00001",
        "--doi",
        "10.1234/example.paper",
        "--zotero",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["identifier"] == "2401.00001"
    assert payload["zotero_status"]["identifier"] == "2401.00001"


def test_dry_run_does_not_move_file(tmp_path: Path) -> None:
    source = tmp_path / "download.pdf"
    target_dir = tmp_path / "research"
    write_pdf(source)

    result = run_postprocess(
        "--pdf",
        str(source),
        "--target-dir",
        str(target_dir),
        "--title",
        "Dry Run Paper",
        "--field",
        "Agent",
        "--dry-run",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["dry_run"] is True
    assert payload["saved_path"].endswith("Agent_Dry Run Paper.pdf")
    assert source.exists()
    assert not target_dir.exists()


def test_invalid_pdf_fails(tmp_path: Path) -> None:
    source = tmp_path / "not-pdf.pdf"
    source.write_text("<html>not a pdf</html>", encoding="utf-8")

    result = run_postprocess(
        "--pdf",
        str(source),
        "--title",
        "Not PDF",
        "--field",
        "RAG",
    )

    assert result.returncode != 0
    assert "valid PDF header" in result.stderr


def test_duplicate_filename_gets_suffix(tmp_path: Path) -> None:
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    write_pdf(first)
    write_pdf(second)

    first_result = run_postprocess("--pdf", str(first), "--title", "Same Title", "--field", "SFT")
    second_result = run_postprocess("--pdf", str(second), "--title", "Same Title", "--field", "SFT")

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    second_payload = json.loads(second_result.stdout)
    assert second_payload["final_name"] == "SFT_Same Title (2).pdf"
