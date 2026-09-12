#!/usr/bin/env python3
"""
cv-check.py — check a CV file for ATS parse safety and keyword coverage.

Reads .docx (zip/XML, no dependencies), .pdf (needs `pdftotext` from poppler
on PATH; `pdfinfo`/`pdffonts` used if present), .md (the cv skill format) or
.txt. Optionally compares against a job description — a plain text file or an
application file from career/applications/ (only its `## Job description`
section is used) — and against the keyword bank in career/keywords.md.

The score at the end is a heuristic. No ATS vendor publishes one. Exit code
is 1 when any FAIL was found, else 0.

usage:
  python scripts/cv-check.py career/cv/out/Name-CV.docx
  python scripts/cv-check.py cv.pdf --jd career/applications/2026-09-11-acme-role.md
  options: --jd FILE  --keywords career/keywords.md  --title "Senior .NET Engineer"
           --out report.md  --lines 60
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
SAFE_FONTS = {"calibri", "arial", "helvetica", "georgia", "cambria", "garamond", "aptos", "segoe ui",
              "times new roman", "verdana", "tahoma", "trebuchet ms", "lato", "roboto", "open sans",
              "source sans pro", "carlito", "liberation sans", "liberation serif", "dejavu sans", "symbol"}

SECTION_SYNONYMS = {
    "Summary": ["summary", "professional summary", "profile", "professional profile", "about", "about me",
                "objective", "career summary", "executive summary"],
    "Skills": ["skills", "technical skills", "core skills", "key skills", "technologies", "tech stack",
               "core competencies", "skills & tools", "technical expertise", "competencies"],
    "Experience": ["experience", "work experience", "professional experience", "employment",
                   "employment history", "work history", "career history", "relevant experience"],
    "Education": ["education", "education & training", "academic background", "academics"],
    "Certifications": ["certifications", "certificates", "certifications & courses",
                       "licenses & certifications", "licences & certifications", "courses"],
    "Projects": ["projects", "selected projects", "personal projects", "open source", "side projects"],
}
CANONICAL = {k: k.lower() for k in SECTION_SYNONYMS}

WEAK_PHRASES = ["responsible for", "duties included", "helped", "worked on", "involved in", "participated in",
                "assisted with", "various", "team player", "hard-working", "hardworking", "results-driven",
                "detail-oriented", "synergy", "go-getter", "think outside the box", "passionate about",
                "fast-paced", "self-starter", "dynamic", "leverage"]

# (acronym, full forms, both_directions). both_directions=False: only flag the
# acronym appearing without its full form — never suggest adding the acronym.
ACRONYM_PAIRS = [
    ("CI/CD", ["continuous integration", "continuous delivery", "continuous deployment"], True),
    ("EF Core", ["Entity Framework Core", "Entity Framework"], True),
    ("K8s", ["Kubernetes"], False),
    ("AWS", ["Amazon Web Services"], False),
    ("GCP", ["Google Cloud"], False),
    ("TDD", ["test-driven development", "test driven development"], True),
    ("DDD", ["domain-driven design", "domain driven design"], True),
    ("CQRS", ["command query responsibility segregation"], False),
    ("OOP", ["object-oriented"], False),
    ("MSSQL", ["SQL Server"], False),
    ("OIDC", ["OpenID Connect"], True),
    ("IaC", ["infrastructure as code"], False),
    ("SRE", ["site reliability"], False),
]

# Backend / .NET lexicon: seeds JD extraction alongside the keyword bank. Comma-separated terms.
LEXICON = """
C#, .NET, .NET Core, .NET Framework, .NET 6, .NET 7, .NET 8, .NET 9, .NET 10, ASP.NET, ASP.NET Core, ASP.NET MVC,
Web API, Minimal APIs, Entity Framework, Entity Framework Core, EF Core, Dapper, LINQ, ADO.NET, SQL, T-SQL, SQL Server,
PostgreSQL, MySQL, MariaDB, Oracle, SQLite, MongoDB, Cosmos DB, DynamoDB, Redis, Elasticsearch, OpenSearch, Cassandra,
Neo4j, ClickHouse, Snowflake, BigQuery, RabbitMQ, Kafka, Apache Kafka, Azure Service Bus, Azure Event Hubs, Event Grid,
MassTransit, NServiceBus, SQS, SNS, EventBridge, Pub/Sub, NATS, MQTT, gRPC, REST, RESTful, REST APIs, RESTful APIs,
GraphQL, SignalR, WebSockets, OpenAPI, Swagger, OData, Protobuf, JSON, XML, SOAP, WCF, OAuth, OAuth2, OAuth 2.0,
OpenID Connect, OIDC, JWT, SAML, IdentityServer, Duende, Azure AD, Entra ID, Keycloak, Auth0, Okta, Azure, AWS, GCP,
Google Cloud, Amazon Web Services, Azure Functions, AWS Lambda, Azure App Service, AKS, Azure Kubernetes Service, EKS,
GKE, ECS, Fargate, S3, Blob Storage, Azure Storage, Azure SQL, Azure DevOps, GitHub Actions, GitLab CI, Jenkins,
TeamCity, Octopus Deploy, ArgoCD, Argo CD, Flux, CI/CD, continuous integration, continuous delivery,
continuous deployment, Docker, Kubernetes, Helm, Terraform, Bicep, ARM templates, Pulumi, Ansible, Nginx, IIS, Linux,
Windows, Bash, PowerShell, infrastructure as code, xUnit, NUnit, MSTest, Moq, NSubstitute, FluentAssertions,
Testcontainers, Playwright, Selenium, SpecFlow, AutoFixture, k6, JMeter, TDD, BDD, DDD, CQRS, Event Sourcing,
test-driven development, domain-driven design, SOLID, Clean Architecture, Hexagonal Architecture, Onion Architecture,
Vertical Slice, design patterns, clean code, dependency injection, microservices, microservices architecture, monolith,
modular monolith, event-driven, event-driven architecture, distributed systems, saga, outbox, idempotency,
eventual consistency, message queues, message broker, background services, background jobs, MediatR, AutoMapper,
FluentValidation, Mapster, Serilog, NLog, Polly, Hangfire, Quartz, Quartz.NET, Refit, YARP, Ocelot, OpenTelemetry,
Application Insights, Prometheus, Grafana, Seq, ELK, Elastic Stack, Datadog, New Relic, Splunk, Jaeger, Zipkin, Sentry,
observability, monitoring, logging, tracing, metrics, alerting, on-call, SLA, SLO, incident management,
site reliability, Blazor, Razor, MAUI, Xamarin, WPF, WinForms, Angular, React, Vue, TypeScript, JavaScript, Node.js,
HTML, CSS, Python, Go, Golang, Java, Kotlin, Rust, C++, Scala, Ruby, PHP, Git, GitHub, GitLab, Bitbucket, Jira,
Confluence, Agile, Scrum, Kanban, SAFe, code review, pair programming, mentoring, technical leadership, team lead,
tech lead, performance, scalability, high availability, fault tolerance, caching, load balancing, rate limiting,
security, OWASP, encryption, unit testing, integration testing, end-to-end testing, load testing, contract testing,
mutation testing, async/await, multithreading, concurrency, parallelism, garbage collection, memory management,
profiling, BenchmarkDotNet, Span<T>, PerfView, dotnet-trace, system design, API design, database design,
data modeling, schema design, migrations, indexing, query optimization, stored procedures, software architecture,
solution architecture, cloud architecture, fintech, payments, banking, e-commerce, healthcare, SaaS, B2B, B2C, ERP,
CRM, Dynamics 365, Power Platform, Power BI, SharePoint, Unity, Service Fabric, Orleans, Dapr, Akka.NET,
Cloud Native, serverless, API Gateway, Azure API Management, Kong, Istio, service mesh, release management,
English, German, Polish, Ukrainian
"""
LEXICON_TERMS = list(dict.fromkeys(t.strip() for t in LEXICON.replace("\n", " ").split(",") if t.strip()))

STOP_ACRONYMS = {"AND", "OR", "THE", "YOU", "WE", "OUR", "FOR", "WITH", "NOT", "ARE", "ALL", "ANY", "NEW", "CV", "PDF",
                 "USA", "UK", "EU", "EMEA", "HR", "PR", "CEO", "CTO", "VP", "OK", "PLUS", "ETC", "FAQ", "LLC", "INC",
                 "LTD", "GMBH", "IT", "IS", "IN", "ON", "AT", "TO", "OF", "AS", "BY", "AN", "A", "I", "II", "III"}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?<![\w/])(\+?\d[\d\s().-]{7,}\d)(?![\w/])")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w%-]+", re.I)
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"
DATE_TOKEN = re.compile(rf"(?:{MONTH}\s+\d{{4}}|\b(?:0?[1-9]|1[0-2])[./]\d{{4}}\b|\b(?:19|20)\d{{2}}\b)")
DATE_RANGE = re.compile(
    rf"({MONTH}\s+\d{{4}}|\b(?:0?[1-9]|1[0-2])[./]\d{{4}}\b|\b(?:19|20)\d{{2}}\b)\s*(?:-|–|—|to)\s*"
    rf"({MONTH}\s+\d{{4}}|\b(?:0?[1-9]|1[0-2])[./]\d{{4}}\b|\b(?:19|20)\d{{2}}\b|Present|Current|Now|Today)", re.I)


class Report:
    def __init__(self):
        self.sections: dict[str, list[tuple[str, str]]] = {}
        self.counts = {"FAIL": 0, "WARN": 0, "PASS": 0, "INFO": 0}

    def add(self, section: str, level: str, msg: str):
        self.sections.setdefault(section, []).append((level, msg))
        self.counts[level] += 1

    def fail(self, s, m): self.add(s, "FAIL", m)
    def warn(self, s, m): self.add(s, "WARN", m)
    def ok(self, s, m): self.add(s, "PASS", m)
    def info(self, s, m): self.add(s, "INFO", m)


# ------------------------------------------------------------------ extraction

def para_texts_docx(root) -> list[str]:
    """Paragraph texts in document order, skipping mc:Fallback duplicates."""
    out = []

    def walk(el):
        if el.tag == MC + "Fallback":
            return
        if el.tag == W + "p":
            out.append(para_text(el))
            return  # paragraphs do not nest except via text boxes, handled by continuing below
        for ch in el:
            walk(ch)

    def para_text(p):
        buf = []
        for node in p.iter():
            if node.tag == W + "t":
                buf.append(node.text or "")
            elif node.tag == W + "tab":
                buf.append("\t")
            elif node.tag in (W + "br", W + "cr"):
                buf.append("\n")
        return "".join(buf)

    walk(root)
    return out


def extract_docx(path: str, rep: Report):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        doc = ET.fromstring(z.read("word/document.xml"))
        styles = ET.fromstring(z.read("word/styles.xml")) if "word/styles.xml" in names else None
        header_text = []
        for n in names:
            if re.match(r"word/(header|footer)\d*\.xml", n):
                hf = ET.fromstring(z.read(n))
                t = " ".join((x.text or "") for x in hf.iter(W + "t")).strip()
                if t:
                    header_text.append((n, t))
        media = [n for n in names if n.startswith("word/media/")]

    body = doc.find(W + "body")
    paras = para_texts_docx(body)
    text = "\n".join(paras)

    # --- structure
    n_tbl = len(list(body.iter(W + "tbl")))
    n_txbx = len(list(body.iter(W + "txbxContent")))
    n_draw = len(list(body.iter(W + "drawing"))) + len(list(body.iter(W + "pict"))) + len(list(body.iter(W + "object")))
    cols = [c for c in body.iter(W + "cols") if int(c.get(W + "num", "1")) > 1]
    S = "Structure"
    if n_tbl:
        rep.fail(S, f"{n_tbl} table(s) in the body — tables are parsed inconsistently; the two-column layout or the skills grid is the usual culprit. Use paragraphs.")
    else:
        rep.ok(S, "no tables")
    if n_txbx:
        rep.fail(S, f"{n_txbx} text box(es) — most parsers skip text boxes entirely.")
    else:
        rep.ok(S, "no text boxes")
    if cols:
        rep.fail(S, f"multi-column section ({int(cols[0].get(W + 'num'))} columns) — reading order breaks.")
    else:
        rep.ok(S, "single column")
    if n_draw or media:
        rep.warn(S, f"{n_draw} drawing/picture object(s), {len(media)} media file(s) — images and icons carry no text and some parsers choke on them. Remove photos, icons, skill bars.")
    else:
        rep.ok(S, "no images or drawing objects")
    if header_text:
        joined = " ".join(t for _, t in header_text)
        if EMAIL_RE.search(joined) or PHONE_RE.search(joined) or LINKEDIN_RE.search(joined):
            if not (EMAIL_RE.search(text) or PHONE_RE.search(text)):
                rep.fail(S, "contact details live only in the header/footer — many parsers never read those parts. Move the contact block into the body.")
            else:
                rep.warn(S, "contact details appear in a header/footer; they are also in the body, so this is only a duplication risk.")
        else:
            rep.warn(S, f"header/footer contains text ({joined[:60]!r}) — content there is often dropped by parsers.")
    else:
        rep.ok(S, "no header/footer text")

    # --- hidden text
    hidden = []
    for r in body.iter(W + "r"):
        rpr = r.find(W + "rPr")
        if rpr is None:
            continue
        t = "".join((x.text or "") for x in r.iter(W + "t")).strip()
        if not t:
            continue
        color = rpr.find(W + "color")
        sz = rpr.find(W + "sz")
        if rpr.find(W + "vanish") is not None:
            hidden.append(("vanish", t))
        elif color is not None and re.fullmatch(r"[0-9A-Fa-f]{6}", color.get(W + "val", "")) and \
                all(int(color.get(W + "val")[i:i + 2], 16) >= 0xF0 for i in (0, 2, 4)):
            hidden.append(("white text", t))
        elif sz is not None and sz.get(W + "val", "22").isdigit() and int(sz.get(W + "val")) < 12:
            hidden.append((f"{int(sz.get(W + 'val')) / 2:.0f}pt text", t))
    if hidden:
        rep.fail(S, "hidden text detected — " + "; ".join(f"{k}: {v[:40]!r}" for k, v in hidden[:5]) +
                 ". Parsers extract it, recruiters see it, applications get binned.")
    else:
        rep.ok(S, "no hidden, white, or sub-6pt text")

    # --- fonts
    fonts = set()
    for el in list(body.iter(W + "rFonts")) + (list(styles.iter(W + "rFonts")) if styles is not None else []):
        for attr in ("ascii", "hAnsi"):
            v = el.get(W + attr)
            if v and not v.startswith("+"):
                fonts.add(v)
    odd = sorted(f for f in fonts if f.lower() not in SAFE_FONTS)
    if odd:
        rep.warn(S, f"non-standard font(s): {', '.join(odd)} — if a font is an icon or display face, glyphs may extract as garbage. Standard: Calibri, Arial, Georgia, Cambria.")
    else:
        rep.ok(S, f"fonts: {', '.join(sorted(fonts)) or 'document default'}")

    # --- heading styles
    styled = [p for p in body.iter(W + "p") if (ps := p.find(f"{W}pPr/{W}pStyle")) is not None and
              ps.get(W + "val", "").lower().startswith("heading")]
    if styled:
        rep.info(S, f"{len(styled)} paragraph(s) use Heading styles — parsers use these as section anchors.")
    else:
        rep.info(S, "no Heading styles used — parsers fall back to text matching of section names.")

    return text, {"pages": None}


def extract_pdf(path: str, rep: Report):
    S = "Structure"
    if not shutil.which("pdftotext"):
        sys.exit("pdftotext not found on PATH (poppler). Install poppler or check the .docx instead.")
    text = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout
    if not text.strip():
        rep.fail(S, "no extractable text — the PDF is an image (scanned or 'printed' to an image). Export from Word as text PDF, or send .docx.")
    else:
        rep.ok(S, f"text extractable ({len(text.split())} words)")
    meta = {"pages": None}
    if shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", path], capture_output=True, text=True, errors="replace").stdout
        m = re.search(r"Pages:\s+(\d+)", info)
        if m:
            meta["pages"] = int(m.group(1))
    if shutil.which("pdffonts"):
        fl = subprocess.run(["pdffonts", path], capture_output=True, text=True, errors="replace").stdout.splitlines()[2:]
        names = []
        not_emb = []
        for line in fl:
            parts = line.split()
            if len(parts) >= 4:
                nm = re.sub(r"^[A-Z]{6}\+", "", parts[0])
                names.append(nm)
                if parts[-6:] and "no" in parts[3:5]:
                    not_emb.append(nm)
        base = {re.split(r"[-,]", n)[0].lower() for n in names}
        odd = sorted(b for b in base if b.replace("mt", "").strip() not in SAFE_FONTS and b not in SAFE_FONTS)
        if odd:
            rep.warn(S, f"non-standard font(s): {', '.join(odd)}")
        else:
            rep.ok(S, f"fonts: {', '.join(sorted(base))}")
        if any("Type 3" in l for l in fl):
            rep.warn(S, "Type 3 fonts present — text often extracts as garbage from these.")
    # form feeds separate pages
    if meta["pages"] is None and text:
        meta["pages"] = text.count("\f") + (0 if text.endswith("\f") else 1)
    pua = sum(1 for ch in text if 0xE000 <= ord(ch) <= 0xF8FF)
    if pua:
        rep.fail(S, f"{pua} private-use glyph(s) (icon fonts) in the text — they extract as garbage.")
    # crude column detection: contact far down, or many short lines
    lines = [l for l in text.splitlines() if l.strip()]
    first_contact = next((i for i, l in enumerate(lines) if EMAIL_RE.search(l) or LINKEDIN_RE.search(l)), None)
    if first_contact is not None and first_contact > 25:
        rep.warn(S, f"contact details first appear on extracted line {first_contact + 1} — a sidebar or footer is likely; parsers may not associate it with the name.")
    if len(lines) > 40:
        short = sum(1 for l in lines if len(l.strip()) < 35)
        if short / len(lines) > 0.7:
            rep.warn(S, f"{short}/{len(lines)} extracted lines are under 35 chars — looks like a multi-column layout or a sidebar.")
    return text, meta


def extract_md(path: str):
    with open(path, encoding="utf-8") as f:
        raw = f.read().replace("\r\n", "\n")
    fm = {}
    body = raw
    if raw.startswith("---\n"):
        end = raw.find("\n---", 4)
        for line in raw[4:end].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip().lower()] = v.strip()
        body = raw[end + 4:]
    head = [fm.get("name", ""), fm.get("title", ""),
            "  ·  ".join(fm[k] for k in ("email", "phone", "location", "linkedin", "github", "website") if fm.get(k))]
    lines = [h for h in head if h]
    for line in body.splitlines():
        line = re.sub(r"^#+\s*", "", line)
        line = re.sub(r"^\s*[-*]\s+", "• ", line)
        line = line.replace("**", "")
        line = line.replace(" | ", "  |  ")
        lines.append(line)
    return "\n".join(lines)


def extract(path: str, rep: Report):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return extract_docx(path, rep)
    if ext == ".pdf":
        return extract_pdf(path, rep)
    if ext in (".md", ".markdown"):
        rep.info("Structure", "markdown source — structure checks apply to the built .docx, not to this file.")
        return extract_md(path), {"pages": None}
    if ext == ".txt":
        rep.info("Structure", "plain text — no structure to check.")
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(), {"pages": None}
    if ext == ".doc":
        sys.exit("legacy .doc is not supported; save as .docx")
    sys.exit(f"unsupported file type {ext}")


# ------------------------------------------------------------------ checks

def check_parse(text: str, meta: dict, rep: Report):
    P = "Parse"
    lines = [l.strip() for l in text.splitlines()]
    nonempty = [l for l in lines if l]

    if EMAIL_RE.search(text):
        rep.ok(P, f"email found: {EMAIL_RE.search(text).group(0)}")
    else:
        rep.fail(P, "no email address found in the extracted text")
    if PHONE_RE.search(text):
        rep.ok(P, "phone number found")
    else:
        rep.warn(P, "no phone number found (or it is formatted in a way the regex missed)")
    if LINKEDIN_RE.search(text):
        rep.ok(P, "LinkedIn URL found")
    else:
        rep.warn(P, "no LinkedIn URL — recruiters cross-reference it")
    idx = next((i for i, l in enumerate(nonempty) if EMAIL_RE.search(l)), None)
    if idx is not None and idx > 6:
        rep.warn(P, f"email is on extracted line {idx + 1}; contact block should be within the first few lines")

    # headings
    found: dict[str, str] = {}
    candidates = []
    for l in nonempty:
        key = re.sub(r"[:\s]+$", "", l).strip().lower()
        key = re.sub(r"\s+", " ", key)
        if not key or len(key) > 40:
            continue
        for canon, syns in SECTION_SYNONYMS.items():
            if key in syns and canon not in found:
                found[canon] = l.strip()
        words = key.split()
        if 1 <= len(words) <= 3 and (l.isupper() or l.istitle()) and not DATE_TOKEN.search(l) \
                and not EMAIL_RE.search(l) and not any(key in s for s in SECTION_SYNONYMS.values()) \
                and not re.search(r"[|•,.@()]", l) and len(l) < 32:
            candidates.append(l.strip())
    for canon in ("Experience", "Skills", "Education", "Summary"):
        if canon in found:
            if found[canon].strip().lower() != CANONICAL[canon]:
                rep.info(P, f"section '{found[canon]}' recognised as {canon} — the plain word '{canon}' is the safest spelling")
            else:
                rep.ok(P, f"section heading: {canon}")
        elif canon == "Experience":
            rep.fail(P, "no Experience section heading recognised — parsers need it to find your roles")
        elif canon in ("Skills", "Education"):
            rep.warn(P, f"no {canon} section heading recognised")
        else:
            rep.info(P, "no Summary heading — a three-line summary carrying the target title helps search and skim")
    odd = [c for c in candidates if c.lower() not in {s for v in SECTION_SYNONYMS.values() for s in v}]
    if odd:
        rep.info(P, "short title-case lines that are not standard headings (fine if they are job titles or names): " + ", ".join(dict.fromkeys(odd[:8])))

    # dates
    ranges = DATE_RANGE.findall(text)
    if not ranges:
        rep.fail(P, "no date ranges found (e.g. 'Mar 2022 – Present') — roles without dates are not counted toward years of experience")
    else:
        styles = set()
        for a, b in ranges:
            for d in (a, b):
                if re.match(r"(?i)present|current|now|today", d):
                    continue
                m = re.match(r"([A-Za-z]+)", d)
                if m:
                    styles.add("full" if len(m.group(1).rstrip(".")) > 4 else "abbr")
                elif "/" in d or "." in d:
                    styles.add("numeric")
                else:
                    styles.add("year")
        if len(styles - {"year"}) > 1:
            rep.warn(P, f"mixed date formats {sorted(styles)} — use one, 'Mon YYYY', throughout")
        else:
            rep.ok(P, f"{len(ranges)} date range(s), consistent format")
        if styles == {"year"}:
            rep.warn(P, "dates are year-only — parsers round months; use 'Mon YYYY'")

    # length
    words = len(text.split())
    pages = meta.get("pages") or round(words / 550, 1)
    if pages > 2.2:
        rep.warn(P, f"length ≈ {pages} pages ({words} words) — two pages is the ceiling")
    elif words < 250:
        rep.warn(P, f"only {words} words — thin; every role needs bullets with numbers")
    else:
        rep.ok(P, f"length ≈ {pages} page(s), {words} words")


def check_content(text: str, rep: Report):
    C = "Content"
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    bullets = [l for l in lines if re.match(r"^[•\-*–▪◦]\s*\S", l)]
    if not bullets:
        rep.warn(C, "no bullet lines detected — achievements should be bullets under each role")
    else:
        with_num = [b for b in bullets if re.search(r"\d", b)]
        pct = 100 * len(with_num) // len(bullets)
        (rep.ok if pct >= 50 else rep.warn)(C, f"{len(bullets)} bullets, {pct}% carry a number — aim for at least half")
        long = [b for b in bullets if len(b) > 230]
        if long:
            rep.warn(C, f"{len(long)} bullet(s) over 230 chars — split or cut: {long[0][:70]!r}…")
        weak_starts = [b for b in bullets if re.match(r"^[•\-*–▪◦]\s*(responsible|helped|worked|involved|participated|assisted|duties|I |my )", b, re.I)]
        if weak_starts:
            rep.warn(C, f"{len(weak_starts)} bullet(s) open weakly: {weak_starts[0].replace(chr(9), ' ')[:70]!r}")

    pron = len(re.findall(r"\b(I|me|my|mine)\b", text))
    if pron:
        rep.warn(C, f"{pron} first-person pronoun(s) — CV bullets drop the subject ('Led…', not 'I led…')")
    else:
        rep.ok(C, "no first-person pronouns")

    low = text.lower()
    hits = [(p, low.count(p)) for p in WEAK_PHRASES if low.count(p)]
    if hits:
        rep.warn(C, "weak phrases: " + ", ".join(f"'{p}'×{n}" for p, n in hits))
    else:
        rep.ok(C, "no weak phrases")

    for acr, fulls, both in ACRONYM_PAIRS:
        has_acr = re.search(r"(?<![\w/])" + re.escape(acr) + r"(?![\w])", text, re.I) is not None
        has_full = any(f.lower() in low for f in fulls)
        if has_acr and not has_full:
            rep.info(C, f"'{acr}' used without its full form ('{fulls[0]}') — recruiters search either; use both once")
        elif both and has_full and not has_acr:
            rep.info(C, f"'{fulls[0]}' used without the acronym '{acr}' — use both once")


# ------------------------------------------------------------------ keywords

def load_bank(path: str) -> list[tuple[str, list[str], str]]:
    if not path or not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("|") or line.startswith("|---") or line.lower().startswith("| keyword"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3 or not cells[0]:
                continue
            variants = [] if cells[1] in ("—", "-", "") else [v.strip() for v in re.split(r"[;,]", cells[1]) if v.strip()]
            out.append((cells[0], variants, cells[2]))
    return out


def jd_text(path: str) -> tuple[str, str | None]:
    with open(path, encoding="utf-8") as f:
        raw = f.read().replace("\r\n", "\n")
    title = None
    m = re.search(r"^role:\s*(.+)$", raw, re.M)
    if m:
        title = m.group(1).strip().strip('"')
    sec = re.search(r"^## Job description\s*\n(.*?)(?=^## |\Z)", raw, re.M | re.S)
    if sec:
        return sec.group(1), title
    if raw.startswith("---\n"):
        end = raw.find("\n---", 4)
        raw = raw[end + 4:]
    return raw, title


def term_re(term: str) -> re.Pattern:
    return re.compile(r"(?<![\w#+.])" + re.escape(term) + r"(?![\w#+])", re.I)


def extract_jd_terms(jd: str, bank) -> list[tuple[str, list[str], str, int, str]]:
    """-> [(keyword, variants, category, jd_count, weight)]"""
    low = jd.lower()
    nice_idx = None
    m = re.search(r"^\W*(nice[- ]to[- ]have|preferred|bonus|good to have|desirable|would be a plus|nice-to-haves?|plus(?:es)?)\b.*$",
                  jd, re.I | re.M)
    if m:
        nice_idx = m.start()
    seen: dict[str, tuple[list[str], str]] = {}
    for kw, variants, cat in bank:
        seen.setdefault(kw, (variants, cat))
    for t in LEXICON_TERMS:
        seen.setdefault(t, ([], "lexicon"))
    # heuristics: acronyms, CamelCase, dotted tokens
    for tok in set(re.findall(r"\b[A-Z][A-Z0-9]{1,5}\b", jd)):
        if tok not in STOP_ACRONYMS and tok not in seen:
            seen[tok] = ([], "acronym")
    for tok in set(re.findall(r"\b[A-Z][a-z]+(?:[A-Z][A-Za-z]+)+\b", jd)):
        seen.setdefault(tok, ([], "camelcase"))
    for tok in set(re.findall(r"(?<!\w)\.?[A-Za-z][A-Za-z0-9]*\.[A-Za-z]{2,}(?:\s\d+)?\b", jd)):
        if not re.search(r"\.(com|io|net|org|co|dev|ai)\b", tok.lower()) or tok.startswith(".NET"):
            seen.setdefault(tok, ([], "dotted"))
    out = []
    for kw, (variants, cat) in seen.items():
        forms = [kw] + variants
        cnt = 0
        first = None
        for f in forms:
            for mm in term_re(f).finditer(jd):
                cnt += 1
                if first is None or mm.start() < first:
                    first = mm.start()
        if cnt == 0:
            continue
        weight = "nice" if (nice_idx is not None and first is not None and first > nice_idx) else "must"
        if cat in ("soft",):
            weight = "nice"
        out.append((kw, variants, cat, cnt, weight))
    # drop subsumed single tokens when a multiword containing them also matched (e.g. "Core" in "ASP.NET Core")
    names = [o[0] for o in out]
    keep = []
    for o in out:
        kw = o[0]
        # a heuristic token that only occurs inside a longer matched term ("ASP" in "ASP.NET Core") is noise
        if o[2] in ("acronym", "camelcase", "dotted") and \
                any(n.lower() != kw.lower() and term_re(kw).search(n) for n in names):
            continue
        keep.append(o)
    keep.sort(key=lambda o: (o[4] != "must", -o[3], o[0].lower()))
    return keep


def check_keywords(cv_text: str, jd_path: str, bank_path: str, title_arg: str | None, rep: Report):
    K = "Keywords"
    jd, title = jd_text(jd_path)
    title = title_arg or title
    bank = load_bank(bank_path)
    terms = extract_jd_terms(jd, bank)
    if not terms:
        rep.warn(K, "no keywords extracted from the JD")
        return None
    rows = []
    must_total = must_hit = nice_total = nice_hit = 0
    stuffed = []
    missing_must = []
    for kw, variants, cat, jdc, weight in terms:
        forms = [kw] + variants
        cvc = 0
        found_as = None
        for f in forms:
            n = len(term_re(f).findall(cv_text))
            if n and found_as is None:
                found_as = f
            cvc += n
        if weight == "must":
            must_total += 1
            must_hit += bool(cvc)
            if not cvc:
                missing_must.append(kw)
        else:
            nice_total += 1
            nice_hit += bool(cvc)
        if cvc > 6:
            stuffed.append((kw, cvc))
        rows.append((kw, weight, cat, jdc, cvc, "yes" if cvc else "NO", found_as if found_as and found_as != kw else ""))
    cov_m = must_hit / must_total if must_total else 1.0
    cov_n = nice_hit / nice_total if nice_total else 1.0
    (rep.ok if cov_m >= 0.8 else rep.warn if cov_m >= 0.5 else rep.fail)(
        K, f"must-have coverage {must_hit}/{must_total}" + (f" — missing: {', '.join(missing_must[:12])}" if missing_must else ""))
    rep.info(K, f"nice-to-have coverage {nice_hit}/{nice_total}")
    if stuffed:
        rep.warn(K, "possible stuffing (>6 uses): " + ", ".join(f"{k}×{n}" for k, n in stuffed))
    if title:
        head = "\n".join(cv_text.splitlines()[:12])
        if term_re(title).search(head):
            rep.ok(K, f"target title '{title}' appears in the top of the CV")
        elif term_re(title).search(cv_text):
            rep.warn(K, f"target title '{title}' appears, but not in the summary block — put it in the first three lines")
        else:
            rep.warn(K, f"target title '{title}' not found — the summary's first line should carry the title the JD uses")
    else:
        rep.info(K, "no target title given (use --title or an application file with `role:`)")
    return {"rows": rows, "must": (must_hit, must_total), "nice": (nice_hit, nice_total), "cov_m": cov_m, "cov_n": cov_n}


# ------------------------------------------------------------------ output

def render(rep: Report, path: str, kw, text: str, n_lines: int) -> tuple[str, int]:
    struct = 100 - 12 * rep.counts["FAIL"] - 4 * rep.counts["WARN"]
    struct = max(0, min(100, struct))
    if kw:
        score = round(0.6 * struct + 40 * (0.75 * kw["cov_m"] + 0.25 * kw["cov_n"]))
    else:
        score = struct
    out = [f"# CV check — {os.path.basename(path)} — {dt.date.today().isoformat()}", ""]
    out.append(f"**Heuristic score: {score}/100** — not an ATS score; no vendor publishes one. "
               f"FAIL {rep.counts['FAIL']} · WARN {rep.counts['WARN']} · PASS {rep.counts['PASS']}"
               + (f" · must-have keywords {kw['must'][0]}/{kw['must'][1]}" if kw else ""))
    out.append("")
    for sec in ("Structure", "Parse", "Content", "Keywords"):
        items = rep.sections.get(sec)
        if not items:
            continue
        out.append(f"## {sec}")
        out.append("")
        order = {"FAIL": 0, "WARN": 1, "INFO": 2, "PASS": 3}
        for lvl, msg in sorted(items, key=lambda x: order[x[0]]):
            out.append(f"- **{lvl}** — {msg}")
        out.append("")
    if kw:
        out.append("## Keyword table")
        out.append("")
        out.append("| Keyword | Weight | Category | In JD | In CV | Found | Matched as |")
        out.append("|---|---|---|---|---|---|---|")
        for kwd, weight, cat, jdc, cvc, found, as_ in kw["rows"]:
            out.append(f"| {kwd} | {weight} | {cat} | {jdc} | {cvc} | {found} | {as_} |")
        out.append("")
    out.append(f"## Extracted text (first {n_lines} lines — this is roughly what a parser sees)")
    out.append("")
    out.append("```")
    shown = [l for l in text.replace("\f", "\n").splitlines() if l.strip()][:n_lines]
    out += shown
    out.append("```")
    return "\n".join(out) + "\n", score


def main():
    ap = argparse.ArgumentParser(description="ATS parse-safety and keyword check for a CV file")
    ap.add_argument("cv")
    ap.add_argument("--jd", help="job description: text file or career/applications/*.md")
    ap.add_argument("--keywords", default=None, help="keyword bank (default career/keywords.md if present)")
    ap.add_argument("--title", help="target title to look for in the summary")
    ap.add_argument("--out", help="write the markdown report here as well as printing it")
    ap.add_argument("--lines", type=int, default=60, help="lines of extracted text to show")
    a = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bank = a.keywords or os.path.join(root, "career", "keywords.md")

    rep = Report()
    text, meta = extract(a.cv, rep)
    check_parse(text, meta, rep)
    check_content(text, rep)
    kw = check_keywords(text, a.jd, bank, a.title, rep) if a.jd else None
    report, score = render(rep, a.cv, kw, text, a.lines)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(report)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(report)
        print(f"(report written to {a.out})")
    sys.exit(1 if rep.counts["FAIL"] else 0)


if __name__ == "__main__":
    main()
