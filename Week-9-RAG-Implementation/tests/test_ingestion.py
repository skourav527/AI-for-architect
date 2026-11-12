import pytest

from src.ingestion.document_loader import load_documents
from src.ingestion.models import DocumentMetadata
from src.ingestion.parser import ParsedSection, parse_document


def test_loader_hashes_content_and_requires_acl_metadata(tmp_path):
    (tmp_path / "guide.md").write_text("# Operations\n\nRestart service.", encoding="utf-8")

    def provider(_source):
        return DocumentMetadata(tenant_id="tenant-a", is_public=True)

    first = load_documents(tmp_path, provider)
    second = load_documents(tmp_path, provider)

    assert first[0].version == second[0].version
    assert first[0].source_uri == "guide.md"
    assert first[0].metadata.is_public


def test_loader_rejects_missing_trusted_metadata(tmp_path):
    (tmp_path / "guide.md").write_text("Private content.", encoding="utf-8")

    with pytest.raises(TypeError):
        load_documents(tmp_path, lambda _source: None)


def test_parser_preserves_markdown_heading_hierarchy():
    sections = parse_document("# Platform\n\nIntro.\n\n## Recovery\n\nRestore steps.")

    assert [(item.heading, item.text) for item in sections] == [
        ("Platform", "Intro."),
        ("Platform > Recovery", "Restore steps."),
    ]


def test_parser_returns_plain_text_as_a_single_section():
    assert parse_document("Plain text.") == [
        ParsedSection(heading="", text="Plain text.")
    ]

