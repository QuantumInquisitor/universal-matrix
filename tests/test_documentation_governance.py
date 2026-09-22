from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def markdown_files():
    return [
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
    ]


def test_authoritative_documents_exist():
    required = [
        "README.md",
        "white_paper.md",
        "ARCHITECTURE.md",
        "docs/DOCUMENTATION_STATUS.md",
        "docs/HOW_TO_USE.md",
        "docs/canonical_spec_v0.4.md",
        "docs/physics_stack_status_2026-09.md",
        "docs/omniverse_design_questions_v0.1.md",
    ]
    for relative in required:
        assert (ROOT / relative).is_file(), relative


def test_removed_duplicate_readme_stays_removed():
    assert not (ROOT / "README2.md").exists()


def test_markdown_has_no_retired_authority_references():
    prohibited = {
        "docs/white_paper.md",
        "white_paper_v6.md",
        "canonical-kernel-v0.3",
        "v93.0.0",
        "GNU Affero General Public License",
        "AGPL-3.0",
        "public open-source option",
    }

    failures = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for phrase in prohibited:
            if phrase in text:
                failures.append(f"{path.relative_to(ROOT)}: {phrase}")

    assert not failures, "\n".join(failures)


def test_current_readme_identifies_noncommercial_source_available_model():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "PolyForm Noncommercial License 1.0.0" in text
    assert "source-available" in text
    assert "not OSI open-source software" in text


def test_current_white_paper_version_matches_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    paper = (ROOT / "white_paper.md").read_text(encoding="utf-8")
    assert "White paper:** Version 0.6" in readme
    assert "Version 0.6" in paper
