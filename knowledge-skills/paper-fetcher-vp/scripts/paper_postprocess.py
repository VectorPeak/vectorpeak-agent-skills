#!/usr/bin/env python3
"""Post-process downloaded research PDFs for the paper-fetcher-vp skill."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ILLEGAL = re.compile(r'[<>:"/\\|?*]')
SPACE = re.compile(r"\s+")
VALID_FIELDS = ("RAG", "Agent", "SFT", "RL", "DL_Frameworks", "Other")


def safe_title(title: str) -> str:
    cleaned = ILLEGAL.sub("-", title)
    cleaned = SPACE.sub(" ", cleaned).strip(" .")
    return cleaned or "paper"


def safe_field(field: str) -> str:
    if field not in VALID_FIELDS:
        raise SystemExit(f"Invalid field prefix: {field}. Expected one of: {', '.join(VALID_FIELDS)}")
    return field


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    index = 2
    while True:
        candidate = parent / f"{stem} ({index}){suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def verify_pdf(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"PDF does not exist: {path}")
    if path.stat().st_size <= 0:
        raise SystemExit(f"PDF is empty: {path}")
    with path.open("rb") as f:
        header = f.read(5)
    if header != b"%PDF-":
        raise SystemExit(f"File is not a valid PDF header: {path}")


def bib_key(title: str, year: str | None) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    base = "".join(words[:4]) or "paper"
    return f"{base}{year or ''}"


def write_bib(path: Path, title: str, authors: str | None, year: str | None, arxiv_id: str | None, source_url: str | None) -> Path:
    key = bib_key(title, year)
    fields = [f"  title = {{{title}}}"]
    if authors:
        fields.append(f"  author = {{{authors}}}")
    if year:
        fields.append(f"  year = {{{year}}}")
    if arxiv_id:
        fields.append(f"  eprint = {{{arxiv_id}}}")
        fields.append("  archivePrefix = {arXiv}")
    if source_url:
        fields.append(f"  url = {{{source_url}}}")
    bib = "@misc{" + key + ",\n" + ",\n".join(fields) + "\n}\n"
    bib_path = path.with_suffix(".bib")
    bib_path.write_text(bib, encoding="utf-8")
    return bib_path


def select_identifier(arxiv_id: str | None, doi: str | None, source_url: str | None) -> str | None:
    if arxiv_id:
        return arxiv_id
    if doi:
        return doi
    if source_url:
        doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", source_url)
        if doi_match:
            return doi_match.group(0)
    return None


def zotero_identifier_status(arxiv_id: str | None, doi: str | None, source_url: str | None) -> dict[str, object]:
    identifier = select_identifier(arxiv_id, doi, source_url)
    if identifier:
        return {
            "attempted": False,
            "status": "identifier_available",
            "identifier": identifier,
            "recommended_action": "Use Zotero Add Item by Identifier or a Zotero MCP/local connector that invokes identifier import. Do not create manual Web API metadata for this paper.",
        }
    return {
        "attempted": False,
        "status": "skipped",
        "reason": "No arXiv/DOI/PMID/ISBN/ADS identifier was supplied.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--field", required=True, choices=VALID_FIELDS, help="Research-field filename prefix.")
    parser.add_argument("--target-dir", help="Directory where the verified and renamed PDF should be saved. Defaults to the input PDF directory.")
    parser.add_argument("--authors")
    parser.add_argument("--year")
    parser.add_argument("--arxiv-id")
    parser.add_argument("--doi")
    parser.add_argument("--source-url")
    parser.add_argument("--bib", action="store_true", help="Optional legacy mode: create a BibTeX sidecar. Off by default.")
    parser.add_argument("--zotero", action="store_true", help="Report Zotero identifier-import status. Does not create files or manual Web API items.")
    parser.add_argument("--dry-run", action="store_true", help="Report the planned output path without moving or writing files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output. Present for explicit agent/CLI use; JSON is also the default output.")
    args = parser.parse_args()

    pdf = Path(args.pdf)
    verify_pdf(pdf)

    target_dir = Path(args.target_dir) if args.target_dir else pdf.parent
    filename = f"{safe_field(args.field)}_{safe_title(args.title)}.pdf"
    target = target_dir / filename
    if not args.dry_run and pdf.resolve() != target.resolve():
        target.parent.mkdir(parents=True, exist_ok=True)
        target = unique_path(target)
        pdf.rename(target)
    elif target.exists():
        target = unique_path(target)

    if not args.dry_run:
        verify_pdf(target)

    bib_path = None
    if args.bib and not args.dry_run:
        bib_path = write_bib(target, args.title, args.authors, args.year, args.arxiv_id, args.source_url)

    if args.zotero:
        zotero_status = zotero_identifier_status(args.arxiv_id, args.doi, args.source_url)
    else:
        zotero_status = {"attempted": False, "status": "skipped", "reason": "Run with --zotero to report identifier-import status."}

    result = {
        "field": args.field,
        "final_name": target.name,
        "saved_path": str(target),
        "pdf": str(target),
        "size_mb": None if args.dry_run else round(target.stat().st_size / 1024 / 1024, 2),
        "pdf_verified": not args.dry_run,
        "dry_run": args.dry_run,
        "identifier": select_identifier(args.arxiv_id, args.doi, args.source_url),
        "bib": str(bib_path) if bib_path else None,
        "zotero_status": zotero_status,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
