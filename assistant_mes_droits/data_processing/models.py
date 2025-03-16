from typing import List, Optional

from pydantic import BaseModel


class PublicationModel(BaseModel):
    # Core identification
    id: Optional[str] = None
    sp_url: Optional[str] = None
    title: Optional[str] = None

    # Content structure
    paragraphs: List[str] = []
    lists: List[List[str]] = []
    links: List[dict] = []

    # Taxonomy
    breadcrumbs: List[dict] = []
    last_modified: Optional[str] = None

    def to_markdown(self) -> str:
        """Convert publication data to formatted Markdown"""
        md = []

        # Title and metadata
        if self.title:
            md.append(f"# {self.title}\n")
            md.append(f"**ID**: `{self.id}`  \n")
            md.append(f"**URL**: [{self.sp_url}]({self.sp_url})\n")

        # Content paragraphs
        if self.paragraphs:
            md.append("## Content\n")
            for p in self.paragraphs:
                cleaned = p.replace("\xa0", " ").strip()
                md.append(f"{cleaned}\n\n")

        # Lists
        if self.lists:
            md.append("## Key Points\n")
            for lst in self.lists:
                md.append("\n".join([f"- {item}" for item in lst]))
                md.append("\n")

        # Links
        if self.links:
            md.append("## Related Links\n")
            for link in self.links:
                text = link.get("text", "Link")
                target = link.get("target", "#")
                md.append(f"- [{text}]({target})\n")

        # Breadcrumbs
        if self.breadcrumbs:
            crumbs = " > ".join([b.get("label", "") for b in self.breadcrumbs])
            md.append(f"**Path**: {crumbs}\n")

        return "\n".join(md).strip()
