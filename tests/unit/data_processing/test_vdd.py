import zipfile
from io import BytesIO

from assistant_mes_droits.data_processing.parse import parse_xml, parse_zip_content

SAMPLE_XML = """
<Publication ID="F78" spUrl="https://example.com">
    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Test Title</dc:title>
    <Paragraphe>First paragraph</Paragraphe>
    <Liste><Item><Paragraphe>Item 1</Paragraphe></Item></Liste>
</Publication>
"""


def test_basic_parsing():
    pub = parse_xml(SAMPLE_XML)
    assert pub.id == "F78"
    assert pub.paragraphs == ["First paragraph", "Item 1"]


def test_zip_parsing():
    # Create in-memory zip
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("file1.xml", SAMPLE_XML)

    pubs = parse_zip_content(zip_buffer.getvalue())
    assert len(pubs) == 1
    assert pubs[0].title == "Test Title"
