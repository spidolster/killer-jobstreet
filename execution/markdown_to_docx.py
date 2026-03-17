import logging
import re
import zipfile
from datetime import datetime, timezone
from xml.sax.saxutils import escape


def _clean_inline_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    return text.strip()


def _paragraph_xml(text: str, style: str = "Normal") -> str:
    if not text:
        return "<w:p/>"
    safe = escape(text)
    return (
        "<w:p>"
        f"<w:pPr><w:pStyle w:val=\"{style}\"/></w:pPr>"
        f"<w:r><w:t xml:space=\"preserve\">{safe}</w:t></w:r>"
        "</w:p>"
    )


def _build_document_xml(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    body_parts = []
    title_written = False

    for raw_line in lines:
        stripped = raw_line.strip()

        if not stripped:
            body_parts.append("<w:p/>")
            continue

        if stripped.startswith("# "):
            body_parts.append(_paragraph_xml(_clean_inline_markdown(stripped[2:]), "Title"))
            title_written = True
            continue

        if stripped.startswith("## "):
            body_parts.append(_paragraph_xml(_clean_inline_markdown(stripped[3:]), "Heading1"))
            continue

        if re.match(r"^[-*]\s+", stripped):
            bullet = re.sub(r"^[-*]\s+", "", stripped)
            body_parts.append(_paragraph_xml(f"• {_clean_inline_markdown(bullet)}", "Normal"))
            continue

        if stripped in ("---", "***"):
            body_parts.append(_paragraph_xml("────────────────────────────────────────", "Divider"))
            continue

        if not title_written:
            body_parts.append(_paragraph_xml(_clean_inline_markdown(stripped), "Title"))
            title_written = True
            continue

        body_parts.append(_paragraph_xml(_clean_inline_markdown(stripped), "Normal"))

    body_parts.append(
        "<w:sectPr>"
        "<w:pgSz w:w=\"12240\" w:h=\"15840\"/>"
        "<w:pgMar w:top=\"1008\" w:right=\"1008\" w:bottom=\"1008\" w:left=\"1008\"/>"
        "</w:sectPr>"
    )

    body = "".join(body_parts)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        f"<w:body>{body}</w:body>"
        "</w:document>"
    )


def _styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:sz w:val="22"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:after="160"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:b/>
      <w:color w:val="0F4C81"/>
      <w:sz w:val="38"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:pPr><w:spacing w:before="180" w:after="100"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
      <w:b/>
      <w:color w:val="0F4C81"/>
      <w:sz w:val="26"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Divider">
    <w:name w:val="Divider"/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:before="120" w:after="120"/></w:pPr>
    <w:rPr>
      <w:color w:val="0F4C81"/>
      <w:sz w:val="20"/>
    </w:rPr>
  </w:style>
</w:styles>"""


def save_markdown_as_styled_docx(markdown_text: str, output_path: str) -> bool:
    if not markdown_text or not markdown_text.strip():
        logging.warning("Skipping DOCX generation because markdown content is empty.")
        return False

    try:
        created = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

        doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""

        core_props = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Tailored Resume</dc:title>
  <dc:creator>killer-jobstreet</dc:creator>
  <cp:lastModifiedBy>killer-jobstreet</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified>
</cp:coreProperties>"""

        app_props = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>killer-jobstreet</Application>
</Properties>"""

        document_xml = _build_document_xml(markdown_text)

        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as docx:
            docx.writestr("[Content_Types].xml", content_types)
            docx.writestr("_rels/.rels", rels)
            docx.writestr("word/document.xml", document_xml)
            docx.writestr("word/styles.xml", _styles_xml())
            docx.writestr("word/_rels/document.xml.rels", doc_rels)
            docx.writestr("docProps/core.xml", core_props)
            docx.writestr("docProps/app.xml", app_props)

        logging.info(f"Styled DOCX resume saved to {output_path}")
        return True
    except Exception as exc:
        logging.error(f"Failed to convert markdown resume to DOCX: {exc}")
        return False
