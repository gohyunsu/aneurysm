#!/usr/bin/env python3
"""Check local HTML links, assets, anchors, and AURORA app mount points."""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[tuple[str, str]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(str(attributes["id"]))
        if tag in {"a", "link"} and attributes.get("href"):
            self.links.append(("href", str(attributes["href"])))
        if tag in {"script", "img", "source"} and attributes.get("src"):
            self.links.append(("src", str(attributes["src"])))


def parse_document(path: Path) -> DocumentParser:
    parser = DocumentParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def resolve_local_target(document: Path, reference: str) -> tuple[Path, str]:
    split = urlsplit(reference)
    target = (document.parent / unquote(split.path)).resolve() if split.path else document
    if target.is_dir():
        target = target / "index.html"
    return target, split.fragment


def check_site(root: Path) -> list[str]:
    errors: list[str] = []
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    readme_lines = readme.splitlines()
    if len(readme_lines) > 260:
        errors.append(
            "README.md: current-facing overview exceeds 260 lines; move dated "
            "provenance to CHANGELOG.md or the filterable site history"
        )
    required_readme_markers = {
        "584 / 73 / 73 train/validation/test": "active split",
        "730개를 환자 730명으로 해석하지 않음": "independent-unit boundary",
        "13,985 rows": "matched steady-information scope",
        "Sheng/RHSIA": "closest direct comparator",
        "LinearNO": "general-operator comparator",
        "새 아키텍처의 우수성은 아직 검증되지 않았습니다": "new-result boundary",
        "기존 test는 원래 T 대 separated T+S 비교에서 이미 개방되었습니다": (
            "opened-test history"
        ),
        "Proposal-only steady": "matched-information fairness boundary",
        "공개 사이트는 유지보수하지 않습니다": "site-scope boundary",
        "같은 scientific cell의 동시 중복 제출": "nonduplicate-execution boundary",
    }
    for marker, label in required_readme_markers.items():
        if marker not in readme:
            errors.append(f"README.md: missing {label} marker {marker!r}")
    forbidden_readme_markers = {
        "/home/introai9/": "private server path",
        "active paper identity는 없습니다": "superseded no-paper state",
        "reference-relative structural fidelity": "superseded research identity",
        "GNN을 포함한 어떤 모델도 current method가 아님": (
            "superseded no-model state"
        ),
        "Real P0 remains 0/11": "stale P0 state presented in current overview",
        "Real P0 is still 0/11": "stale P0 state presented in current overview",
        "모든 논문 성능 cell은 pending": "superseded all-results-pending state",
        "locked test 73 cases와 processed-only extras 79 cases 미개방": (
            "incorrect never-opened test claim"
        ),
        "## 2026-": "dated changelog section duplicated in current overview",
    }
    for marker, label in forbidden_readme_markers.items():
        if marker in readme:
            errors.append(f"README.md: contains {label}")
    for reference in re.findall(r"\[[^\]]+\]\(([^)]+)\)", readme):
        split = urlsplit(reference)
        if split.scheme in {"http", "https", "mailto", "tel", "data"}:
            continue
        target = (root / unquote(split.path)).resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            errors.append(f"README.md: missing local link target {reference}")

    documents = sorted({root / "index.html", *root.glob("site/**/*.html")})
    parsed = {document.resolve(): parse_document(document) for document in documents}

    for document in documents:
        parser = parsed[document.resolve()]
        for kind, reference in parser.links:
            split = urlsplit(reference)
            if split.scheme in {"http", "https", "mailto", "tel", "data"}:
                continue
            target, fragment = resolve_local_target(document, reference)
            if not target.exists():
                errors.append(
                    f"{document.relative_to(root)}: missing {kind} target {reference}"
                )
                continue
            if fragment and target.suffix.lower() == ".html":
                target_parser = parsed.get(target.resolve())
                if target_parser is None:
                    target_parser = parse_document(target)
                    parsed[target.resolve()] = target_parser
                if fragment not in target_parser.ids:
                    errors.append(
                        f"{document.relative_to(root)}: missing anchor "
                        f"{reference}"
                    )

    app = parsed[(root / "site" / "index.html").resolve()]
    required_mounts = {
        "lineage-list",
        "competition-body",
        "gate-list",
        "dataset-list",
        "change-list",
    }
    missing_mounts = required_mounts - app.ids
    if missing_mounts:
        errors.append(f"site/index.html: missing app mounts {sorted(missing_mounts)}")
    if "transient-release" not in app.ids:
        errors.append("site/index.html: missing current transient-release decision panel")

    guide = parsed[(root / "site" / "learn.html").resolve()]
    required_guide_panels = {
        "foundation",
        "graph",
        "gnn",
        "architecture",
        "uncertainty",
        "temporal",
        "functionals",
        "datasets",
        "evidence",
        "experiments",
        "provenance",
        "glossary",
    }
    missing_guide_panels = required_guide_panels - guide.ids
    if missing_guide_panels:
        errors.append(
            f"site/learn.html: missing guide panels {sorted(missing_guide_panels)}"
        )
    if "aneumo-transient-release" not in guide.ids:
        errors.append(
            "site/learn.html: missing zero-assumption Aneumo transient-release panel"
        )
    if "reference-relative-wss" not in guide.ids:
        errors.append(
            "site/learn.html: missing beginner reference-relative WSS panel"
        )

    research_data_path = root / "site" / "assets" / "research-data.js"
    research_data = research_data_path.read_text(encoding="utf-8")
    required_current_markers = {
        "AneuG reference-relative transient WSS 31.0/40 inactive": (
            "current reference-relative candidate boundary"
        ),
        "D3 acquired the exact 23,744,862,051-byte processed transient": (
            "current processed-v4 D3 closure"
        ),
        "object-acquisition pass plus cohort-admission fail": (
            "D3 object-versus-cohort boundary"
        ),
        "Exact count and downstream linkage were not recorded and are not backfilled post hoc": (
            "D3 no-post-hoc-backfill boundary"
        ),
        "730 filename-complete raw directories but fewer than 700 processed cases": (
            "processed/raw cardinality boundary"
        ),
        "The 1k is a resolution tag, not a case-count promise": (
            "processed filename semantics boundary"
        ),
        "D4 closed complete 1/1": (
            "D4 final closure boundary"
        ),
        "578 unique nonblank cases": (
            "D4 exact processed count boundary"
        ),
        "Only 168/578 IDs directly link to the current geometry root": (
            "D4 geometry-linkage boundary"
        ),
        "Human rescore remains inactive 31.0/40": (
            "D4 human-rescore boundary"
        ),
        "Official builder exact case keys and mesh hierarchy are statically corroborated": (
            "D4 official-schema corroboration boundary"
        ),
        "730 cases are not 730 independent patients": (
            "AneuG independent-unit boundary"
        ),
        "five-anatomy within-anatomy inter-solver structure-variability floor": (
            "Challenge auxiliary role"
        ),
        "AneuX is geometry-only OOD support": "AneuX geometry-only boundary",
        "Aneumo is optional only after mapping and licence resolution": (
            "Aneumo optional-source boundary"
        ),
        "Closed response-fidelity P0 v3 remains execution-incomplete with 0/12 scientific checks evaluated": (
            "closed P0 result count"
        ),
        "The current inactive v3 preserves unexecuted v1 and v2": (
            "current confirmation version"
        ),
        "Non-authoritative v3 · v1/v2 metadata/field/prediction 0": (
            "current confirmation evidence state"
        ),
        "AneuG reference-relative structural fidelity": (
            "current reference-relative decision"
        ),
        "966/1,000 cases contain the complete 4.01–5.00 cycle": (
            "current transient release-completeness boundary"
        ),
        "All 40 base families retain a usable complete case": (
            "current transient independent-unit boundary"
        ),
        "concurrent conference/workshop/journal review": (
            "conservative ISBI originality boundary"
        ),
        "Organizer-linked legacy layout": (
            "non-2027-specific template provenance boundary"
        ),
        "uses unsrt": (
            "pre-evidence bibliography-format boundary"
        ),
        "Hodge Spectral Duality": "current topology-operator prior boundary",
        "FaCTz": "latest critical-point-preservation collision boundary",
        "neither source feasibility nor science has a verdict": (
            "G0 no-verdict boundary"
        ),
        "source-watch v22": "current source-authority watch",
        "35/35 live match means no new correction": (
            "current source-authority live refresh"
        ),
    }
    for marker, label in required_current_markers.items():
        if marker not in research_data:
            errors.append(
                f"site/assets/research-data.js: missing {label} marker {marker!r}"
            )
    stale_current_markers = {
        "The current inactive v2 preserves unexecuted v1": (
            "confirmation v2 presented as current"
        ),
        "Non-authoritative v2 · v1 metadata/field/prediction 0": (
            "confirmation v2 state presented as current"
        ),
    }
    for marker, label in stale_current_markers.items():
        if marker in research_data:
            errors.append(f"site/assets/research-data.js: stale {label}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    errors = check_site(root)
    if errors:
        print("Site check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Site check passed · local links, anchors, assets, and app mounts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
