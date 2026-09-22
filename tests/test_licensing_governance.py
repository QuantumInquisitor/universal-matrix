from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_licensing_documents_exist():
    required = [
        "LICENSE",
        "NOTICE",
        "COMMERCIAL_LICENSE.md",
        "COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md",
        "CLA.md",
        "CONTRIBUTING.md",
    ]
    for relative in required:
        assert (ROOT / relative).is_file(), relative


def test_public_license_does_not_prohibit_commercial_use():
    text = (ROOT / "LICENSE").read_text(encoding="utf-8").lower()

    prohibited_phrases = [
        "commercial exclusion",
        "commercial use is prohibited",
        "commercial products are prohibited",
        "corporate entities must execute",
        "for individuals, independent academic researchers",
    ]
    for phrase in prohibited_phrases:
        assert phrase not in text


def test_license_declares_agpl_spdx_identifier():
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "AGPL-3.0-or-later" in text


def test_contributing_does_not_claim_nonexistent_cla_bot():
    text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8").lower()
    assert "uses a cla tracking assistant" not in text
    assert "automated cla bot" in text


def test_commercial_template_is_not_self_executing():
    text = (ROOT / "COMMERCIAL_LICENSE_AGREEMENT_TEMPLATE.md").read_text(
        encoding="utf-8"
    ).lower()
    assert "not effective until" in text
    assert "signatures" in text
