from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "paper_postprocess.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location("paper_postprocess", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


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
        "--name-prefix",
        "Benchmark",
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
    assert payload["name_prefix"] == "Benchmark"
    assert payload["final_name"] == "Benchmark_A-B- Test- Paper-.pdf"
    assert payload["identifier"] == "10.1234/example.paper"
    assert payload["pdf_verified"] is True
    metadata_path = target_dir / "_metadata" / saved_path.with_suffix(".metadata.json").name
    assert payload["metadata"] == str(metadata_path)
    assert saved_path.parent == target_dir
    assert saved_path.exists()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["raw_type"] == "paper"
    assert metadata["title"] == 'A/B: Test? Paper*'
    assert metadata["doi"] == "10.1234/example.paper"
    assert metadata["pdf_filename"] == saved_path.name
    assert not source.exists()


def test_arxiv_identifier_preferred_over_doi(tmp_path: Path) -> None:
    source = tmp_path / "download.pdf"
    target_dir = tmp_path / "research"
    write_pdf(source)

    result = run_postprocess(
        "--pdf",
        str(source),
        "--target-dir",
        str(target_dir),
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
    assert payload["metadata"] is None
    assert source.exists()
    assert not target_dir.exists()


def test_name_prefix_is_separate_from_field_folder(tmp_path: Path) -> None:
    source = tmp_path / "download.pdf"
    target_dir = tmp_path / "research"
    write_pdf(source)

    result = run_postprocess(
        "--pdf",
        str(source),
        "--target-dir",
        str(target_dir),
        "--title",
        "Direct Preference Optimization",
        "--field",
        "RL",
        "--name-prefix",
        "DPO",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    saved_path = Path(payload["saved_path"])
    metadata = json.loads(Path(payload["metadata"]).read_text(encoding="utf-8"))

    assert payload["field"] == "RL"
    assert payload["name_prefix"] == "DPO"
    assert payload["final_name"] == "DPO_Direct Preference Optimization.pdf"
    assert saved_path.parent == target_dir
    assert metadata["field"] == "RL"
    assert metadata["pdf_filename"] == "DPO_Direct Preference Optimization.pdf"


def test_ppo_name_prefix_matches_arxiv_example_contract(tmp_path: Path) -> None:
    source = tmp_path / "download.pdf"
    target_dir = tmp_path / "research" / "02.PostTraining" / "RL"
    write_pdf(source)

    result = run_postprocess(
        "--pdf",
        str(source),
        "--target-dir",
        str(target_dir),
        "--title",
        "Proximal Policy Optimization Algorithms",
        "--field",
        "RL",
        "--name-prefix",
        "PPO",
        "--arxiv-id",
        "1707.06347",
        "--zotero",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    saved_path = Path(payload["saved_path"])

    assert payload["field"] == "RL"
    assert payload["name_prefix"] == "PPO"
    assert payload["final_name"] == "PPO_Proximal Policy Optimization Algorithms.pdf"
    assert payload["identifier"] == "1707.06347"
    assert saved_path.parent == target_dir
    assert saved_path.exists()


def test_move_pdf_uses_shutil_move_for_cross_volume_safety(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_script_module()
    source = tmp_path / "download.pdf"
    target = tmp_path / "research" / "Paper.pdf"
    write_pdf(source)
    calls = []

    def fake_move(src: str, dst: str) -> str:
        calls.append((src, dst))
        destination = Path(dst)
        destination.write_bytes(Path(src).read_bytes())
        Path(src).unlink()
        return dst

    monkeypatch.setattr(module.shutil, "move", fake_move)

    moved = module.move_pdf(source, target)

    assert calls == [(str(source), str(target))]
    assert moved == target
    assert moved.read_bytes().startswith(b"%PDF-")
    assert not source.exists()


def test_default_target_dir_is_local_raw_research_field_folder(tmp_path: Path) -> None:
    source = tmp_path / "download.pdf"
    write_pdf(source)

    result = run_postprocess(
        "--pdf",
        str(source),
        "--title",
        "Default Target Paper",
        "--field",
        "RAG",
        "--dry-run",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert Path(payload["saved_path"]).parent == Path(r"E:\LLM_wiki\LLM_wiki\raw\08.Research\01.RAG")
    assert source.exists()


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
    target_dir = tmp_path / "research"
    write_pdf(first)
    write_pdf(second)

    first_result = run_postprocess("--pdf", str(first), "--target-dir", str(target_dir), "--title", "Same Title", "--field", "SFT")
    second_result = run_postprocess("--pdf", str(second), "--target-dir", str(target_dir), "--title", "Same Title", "--field", "SFT")

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    second_payload = json.loads(second_result.stdout)
    assert second_payload["final_name"] == "SFT_Same Title (2).pdf"
