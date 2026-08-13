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
        "execution-incomplete · 0/12 evaluated": "current P0 state",
        "31.0/40 inactive": "current reference-relative candidate boundary",
        "source G0 | execution-incomplete · exact contract closed": (
            "current source G0 boundary"
        ),
        "730 case를 730 독립 환자로 세지 않습니다": (
            "AneuG independent-unit boundary"
        ),
        "2015 CFD Challenge | 5 anatomy": "Challenge anatomy boundary",
        "current panel activation 영구 금지": "non-reactivation boundary",
        "GNN을 포함한 어떤 모델도 current method가 아님": (
            "no-selected-architecture boundary"
        ),
        "superseded protocol은 삭제하거나 성공으로 relabel하지 않습니다": (
            "history routing boundary"
        ),
    }
    for marker, label in required_readme_markers.items():
        if marker not in readme:
            errors.append(f"README.md: missing {label} marker {marker!r}")
    forbidden_readme_markers = {
        "/home/introai9/": "private server path",
        "Real P0 remains 0/11": "stale P0 state presented in current overview",
        "Real P0 is still 0/11": "stale P0 state presented in current overview",
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
        "processed-v4 D1 attempt 1/3 transport-incomplete under 60 GB": (
            "current processed-v4 acquisition stage"
        ),
        "33,377,372,101-byte peak below a 60 GB selected-asset cap": (
            "storage-bound acquisition boundary"
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
