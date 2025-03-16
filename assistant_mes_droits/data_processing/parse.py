import xml.etree.ElementTree as ET
import zipfile
from io import BytesIO
from typing import List

from assistant_mes_droits.data_processing.models import PublicationModel


# Clean text with \xa0 removal
def clean_text(text: str) -> str:
    return text.replace("\xa0", " ").strip()


def parse_xml(content: str) -> PublicationModel:
    """Parse single XML file into flattened model"""
    root = ET.fromstring(content)
    pub = PublicationModel(
        id=root.get("ID"),
        sp_url=root.get("spUrl"),
        title=root.findtext(".//{http://purl.org/dc/elements/1.1/}title"),
    )

    # Extract paragraphs
    pub.paragraphs = [
        clean_text(p.text) for p in root.findall(".//Paragraphe") if p.text
    ]

    # Extract lists
    pub.lists = [
        [clean_text(i.text) for i in list_elem.findall("Item") if i.text]
        for list_elem in root.findall(".//Liste")
    ]

    return pub


def parse_zip_content(zip_data: bytes) -> List[PublicationModel]:
    """Process zip file containing multiple XMLs, skipping files >0.5MB"""
    with zipfile.ZipFile(BytesIO(zip_data)) as zf:
        return [
            parse_xml(zf.read(f).decode("utf-8"))
            for f in zf.namelist()
            if f.endswith(".xml") and zf.getinfo(f).file_size <= 0.5 * 1024 * 1024
        ]
