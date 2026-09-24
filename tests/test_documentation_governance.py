from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CURRENT_AUTHORITY = [
    "README.md",
    "ARCHITECTURE.md",
    "white_paper.md",
    "docs/DOCUMENTATION_STATUS.md",
    "docs/HOW_TO_USE.md",
    "docs/CURRENT_REPOSITORY_MANIFEST.md",
    "docs/canonical_spec_v0.4.md",
    "docs/physics_stack_status_2026-09.md",
    "docs/omniverse_design_questions_v0.1.md",
    "docs/COMMERCIAL_PRODUCT_SURFACES.md",
    "docs/ROBOTICS_XR_PRODUCT_ARCHITECTURE.md",
]

HISTORICAL_DOCS = [
    "docs/FEATURE_HISTORY.md",
    "docs/REPOSITORY_MANIFEST.md",
    "docs/repository_audit_2026-09.md",
]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8", errors="replace")


def test_current_authority_documents_exist():
    for relative in CURRENT_AUTHORITY:
        assert (ROOT / relative).is_file(), relative


def test_removed_duplicate_white_papers_stay_removed():
    for relative in (
        "docs/white_paper.md",
        "docs/white_paper_old.md",
        "white_paper_v6.md",
    ):
        assert not (ROOT / relative).exists(), relative


def test_current_authority_uses_current_license_model():
    for relative in CURRENT_AUTHORITY:
        text = _read(relative).lower()
        assert "gnu affero" not in text, relative
        assert "agpl" not in text, relative


def test_current_authority_does_not_reference_deleted_white_papers():
    deleted_paths = (
        "docs/white_paper.md",
        "docs/white_paper_old.md",
        "white_paper_v6.md",
    )
    for relative in CURRENT_AUTHORITY:
        text = _read(relative)
        for deleted in deleted_paths:
            assert deleted not in text, (relative, deleted)


def test_historical_documents_are_explicitly_labeled():
    acceptable_markers = (
        "historical / provenance document",
        "point-in-time audit / historical snapshot",
    )
    for relative in HISTORICAL_DOCS:
        head = _read(relative)[:1400].lower()
        assert any(marker in head for marker in acceptable_markers), relative


def test_current_readme_identifies_noncommercial_source_available_model():
    text = _read("README.md")
    assert "PolyForm Noncommercial License 1.0.0" in text
    assert "source-available" in text
    assert "source-available, not OSI open source" in text


def test_readme_has_renderable_canonical_math():
    text = _read("README.md")
    assert "\\mathcal A=\\mathbb Z_{108}\\sqcup B_6" in text
    assert "\\pi(n)=7n\\bmod 64" in text
    assert "[\nmathcal A=" not in text


def test_current_white_paper_version_matches_readme():
    readme = _read("README.md")
    paper = _read("white_paper.md")
    assert "White paper:** Version 0.6" in readme
    assert "Version 0.6" in paper


def test_current_authority_markdown_math_integrity():
    forbidden_controls = ("\t", "\r", "\f", "\b", "\v")
    for relative in CURRENT_AUTHORITY:
        text = _read(relative)
        assert not any(char in text for char in forbidden_controls), relative
        assert "\\[" not in text, relative
        assert "\\]" not in text, relative
        assert "\\(" not in text, relative
        assert "\\)" not in text, relative
        assert "\\`" not in text, relative
        assert not any(
            line.strip() in {"[", "]", "$"} for line in text.splitlines()
        ), relative

def test_architecture_section_order_is_coherent():
    text = _read("ARCHITECTURE.md")
    assert (
        text.index("## 1. Canonical finite layer")
        < text.index("### 1.1 Derived mod-9 quotient and interface-phase audit")
        < text.index("## 2. Primitive ontology layer")
    )
    assert (
        text.index("## 4F. Multidimensional Sri Yantra fibre")
        < text.index("## 4G. Higher-dimensional regular families and E8 bridge")
        < text.index("## 4T. Toroidal circulation and connected field geometry")
        < text.index("## 5. Open discrete-exterior-calculus layer")
    )
    for heading in (
        "### 7.1 Polarization-induced source",
        "### 7.2 Free electric source",
        "### 7.3 Six-gate boundary exchange",
        "### 7.4 Topological magnetic source",
    ):
        assert heading in text
    assert "### 6.1 Polarization-induced source" not in text

