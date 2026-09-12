#!/usr/bin/env python3
"""
cv-build.py — render a CV markdown file to an ATS-safe .docx (plus a .txt).

Input format is fixed in .claude/skills/cv/SKILL.md §8:
  frontmatter    contact block: name (required), title, email (required),
                 phone, location, linkedin, github, website
  ## Heading     section heading (Summary, Skills, Experience, ...)
  ### Entry      "Title — Company | Location | Dates"
  - bullet       one achievement
  **Label:** x   a skills line (each such line is its own paragraph)
  text           paragraph; consecutive lines are joined
  **bold**       inline bold anywhere

Output: single column, standard font, real heading styles, no tables, no
text boxes, no images, no header/footer. Standard library only.

usage:
  python scripts/cv-build.py career/cv/master.md
  python scripts/cv-build.py career/cv/tailored/2026-09-11-acme-role-cv.md
  options: -o OUT.docx   --letter   --font Calibri   --size 11   --no-txt
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
SAFE_FONTS = {"Calibri", "Arial", "Helvetica", "Georgia", "Cambria", "Garamond", "Aptos", "Segoe UI"}


# ------------------------------------------------------------------ parsing

def read_markdown(path: str):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text = text.replace("\r\n", "\n")
    fm: dict[str, str] = {}
    body = text
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end == -1:
            sys.exit("frontmatter opened with --- but never closed")
        for line in text[4:end].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip().lower()] = v.strip().strip('"').strip("'")
        body = text[end + 4:]
    return fm, body


def parse_blocks(body: str):
    """Yield (kind, text) blocks: h2, h3, li, p."""
    blocks = []
    para: list[str] = []

    def flush():
        if para:
            blocks.append(("p", " ".join(s.strip() for s in para)))
            para.clear()

    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        if line.startswith("### "):
            flush()
            blocks.append(("h3", line[4:].strip()))
        elif line.startswith("## "):
            flush()
            blocks.append(("h2", line[3:].strip()))
        elif line.startswith("# "):
            flush()  # a stray H1 is treated as a section heading
            blocks.append(("h2", line[2:].strip()))
        elif re.match(r"^\s*[-*•]\s+", line):
            flush()
            blocks.append(("li", re.sub(r"^\s*[-*•]\s+", "", line).strip()))
        elif line.lstrip().startswith("**"):
            flush()  # a skills line stands alone
            para.append(line)
            flush()
        else:
            para.append(line)
    flush()
    return blocks


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def inline_runs(text: str):
    """Split '**bold** plain' into [(text, bold)]. Links become 'text (url)'."""
    text = LINK_RE.sub(lambda m: m.group(1) if m.group(1) == m.group(2) else f"{m.group(1)} ({m.group(2)})", text)
    runs = []
    bold = False
    for part in re.split(r"(\*\*)", text):
        if part == "**":
            bold = not bold
            continue
        if part:
            runs.append((part, bold))
    return runs


def split_entry(text: str):
    """'Title — Company | Location | Dates' -> (title, company, [rest])."""
    parts = [p.strip() for p in text.split(" | ")]
    head = parts[0]
    rest = parts[1:]
    m = re.split(r"\s+[—–-]\s+", head, maxsplit=1)
    title = m[0].strip()
    company = m[1].strip() if len(m) > 1 else ""
    return title, company, rest


# ------------------------------------------------------------------ docx xml

def run_xml(text: str, bold=False, size_half_pts: int | None = None, color: str | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/><w:bCs/>")
    if size_half_pts:
        props.append(f'<w:sz w:val="{size_half_pts}"/><w:szCs w:val="{size_half_pts}"/>')
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    out = []
    pieces = text.split("\t")
    for i, piece in enumerate(pieces):
        if i:
            out.append(f"<w:r>{rpr}<w:tab/></w:r>")
        if piece:
            out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{escape(piece)}</w:t></w:r>')
    return "".join(out)


def para_xml(runs, style: str | None = None, ppr_extra: str = "") -> str:
    ppr = ""
    if style or ppr_extra:
        ppr = "<w:pPr>" + (f'<w:pStyle w:val="{style}"/>' if style else "") + ppr_extra + "</w:pPr>"
    return f"<w:p>{ppr}{''.join(runs)}</w:p>"


def bullet_para(text: str) -> str:
    ppr = ('<w:tabs><w:tab w:val="left" w:pos="360"/></w:tabs>'
           '<w:ind w:left="360" w:hanging="360"/>'
           '<w:spacing w:after="40"/>')
    runs = [run_xml("•\t")]
    for t, b in inline_runs(text):
        runs.append(run_xml(t, bold=b))
    return para_xml(runs, ppr_extra=ppr)


def build_document(fm: dict, blocks, letter: bool) -> str:
    body: list[str] = []
    name = fm.get("name", "").strip()
    if not name or not fm.get("email"):
        sys.exit("frontmatter needs at least `name:` and `email:`")

    body.append(para_xml([run_xml(name)], style="Heading1"))
    if fm.get("title"):
        body.append(para_xml([run_xml(fm["title"], bold=True)], ppr_extra='<w:spacing w:after="40"/>'))
    contact = [fm.get(k, "") for k in ("email", "phone", "location", "linkedin", "github", "website")]
    contact = [c for c in contact if c]
    body.append(para_xml([run_xml("  ·  ".join(contact))], ppr_extra='<w:spacing w:after="160"/>'))

    for kind, text in blocks:
        if kind == "h2":
            body.append(para_xml([run_xml(text)], style="Heading2"))
        elif kind == "h3":
            title, company, rest = split_entry(text)
            runs = [run_xml(title, bold=True)]
            if company:
                runs.append(run_xml(" — " + company))
            body.append(para_xml(runs, style="Heading3"))
            if rest:
                body.append(para_xml([run_xml("  |  ".join(rest), color="444444")],
                                     ppr_extra='<w:spacing w:after="60"/>'))
        elif kind == "li":
            body.append(bullet_para(text))
        else:
            runs = [run_xml(t, bold=b) for t, b in inline_runs(text)]
            body.append(para_xml(runs))

    if letter:
        page = '<w:pgSz w:w="12240" w:h="15840"/>'
    else:
        page = '<w:pgSz w:w="11906" w:h="16838"/>'
    sect = (f"<w:sectPr>{page}"
            '<w:pgMar w:top="900" w:right="1000" w:bottom="900" w:left="1000" w:header="0" w:footer="0" w:gutter="0"/>'
            '<w:cols w:space="720"/></w:sectPr>')
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:document xmlns:w="{W_NS}"><w:body>{"".join(body)}{sect}</w:body></w:document>')


def build_styles(font: str, size_pt: float) -> str:
    sz = int(round(size_pt * 2))
    def rfonts():
        return f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}" w:eastAsia="{font}"/>'
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W_NS}">
  <w:docDefaults>
    <w:rPrDefault><w:rPr>{rfonts()}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/><w:lang w:val="en-US"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:after="80" w:line="252" w:lineRule="auto"/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="0" w:after="20"/><w:outlineLvl w:val="0"/></w:pPr>
    <w:rPr><w:b/><w:bCs/><w:sz w:val="{sz + 16}"/><w:szCs w:val="{sz + 16}"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="220" w:after="80"/><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="777777"/></w:pBdr><w:outlineLvl w:val="1"/></w:pPr>
    <w:rPr><w:b/><w:bCs/><w:caps/><w:sz w:val="{sz + 2}"/><w:szCs w:val="{sz + 2}"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="120" w:after="0"/><w:outlineLvl w:val="2"/></w:pPr>
    <w:rPr><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/></w:rPr></w:style>
</w:styles>'''


CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''


def core_xml(name: str) -> str:
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    n = escape(name)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{n} — CV</dc:title><dc:creator>{n}</dc:creator><cp:lastModifiedBy>{n}</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>'''


APP_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>cv-build.py</Application></Properties>'''


# ------------------------------------------------------------------ txt

def build_txt(fm: dict, blocks) -> str:
    out = [fm.get("name", "")]
    if fm.get("title"):
        out.append(fm["title"])
    out.append("  ·  ".join(fm[k] for k in ("email", "phone", "location", "linkedin", "github", "website") if fm.get(k)))
    out.append("")
    for kind, text in blocks:
        plain = re.sub(r"\*\*", "", LINK_RE.sub(lambda m: f"{m.group(1)} ({m.group(2)})", text))
        if kind == "h2":
            out += ["", plain.upper(), ""]
        elif kind == "h3":
            title, company, rest = split_entry(plain)
            out.append(f"{title}" + (f" — {company}" if company else ""))
            if rest:
                out.append("  |  ".join(rest))
        elif kind == "li":
            out.append("• " + plain)
        else:
            out.append(plain)
    return "\n".join(out).rstrip() + "\n"


# ------------------------------------------------------------------ main

def default_output(fm: dict, src: str) -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "career", "cv", "out")
    os.makedirs(out_dir, exist_ok=True)
    base = re.sub(r"[^A-Za-z0-9]+", "-", fm.get("name", "cv")).strip("-") or "cv"
    stem = os.path.splitext(os.path.basename(src))[0]
    suffix = "" if stem == "master" else "-" + re.sub(r"^\d{4}-\d{2}-\d{2}-", "", re.sub(r"-cv$", "", stem))
    return os.path.join(out_dir, f"{base}-CV{suffix}.docx")


def main():
    ap = argparse.ArgumentParser(description="Render a CV markdown file to an ATS-safe .docx")
    ap.add_argument("source")
    ap.add_argument("-o", "--out")
    ap.add_argument("--letter", action="store_true", help="US Letter instead of A4")
    ap.add_argument("--font", default="Calibri")
    ap.add_argument("--size", type=float, default=11.0, help="body size in pt")
    ap.add_argument("--no-txt", action="store_true")
    a = ap.parse_args()

    if a.font not in SAFE_FONTS:
        print(f"warning: {a.font} is not in the safe font list {sorted(SAFE_FONTS)}", file=sys.stderr)

    fm, body = read_markdown(a.source)
    blocks = parse_blocks(body)
    out = a.out or default_output(fm, a.source)

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", build_document(fm, blocks, a.letter))
        z.writestr("word/styles.xml", build_styles(a.font, a.size))
        z.writestr("docProps/core.xml", core_xml(fm.get("name", "")))
        z.writestr("docProps/app.xml", APP_XML)

    n_words = sum(len(t.split()) for _, t in blocks)
    print(f"wrote {out}  ({len(blocks)} blocks, ~{n_words} words, ~{n_words / 550:.1f} pages)")
    if not a.no_txt:
        txt = os.path.splitext(out)[0] + ".txt"
        with open(txt, "w", encoding="utf-8", newline="\n") as f:
            f.write(build_txt(fm, blocks))
        print(f"wrote {txt}")


if __name__ == "__main__":
    main()
