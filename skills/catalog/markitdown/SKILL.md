---
name: markitdown
description: Unified multi-format document conversion to Markdown (PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, images, audio) using Microsoft MarkItDown CLI & Python library.
---

# MarkItDown — Unified Multi-Format Document Conversion

## Overview

[Microsoft MarkItDown](https://github.com/microsoft/markitdown) is a lightweight Python utility and CLI tool for converting heterogeneous office documents, web pages, structured data, and media files into clean, token-efficient Markdown suitable for LLM pipelines, technical documentation, and research synthesis.

Unlike plain text extractors, MarkItDown preserves structural semantics—headings, nested lists, Markdown tables, hyperlinks, slide boundaries, and workbook sheets—making converted output immediately usable by `docs-agent` and `research-agent`.

### Supported Input Formats
| Category | Extensions / Inputs | Extraction Behavior |
| :--- | :--- | :--- |
| **Office Documents** | `.docx`, `.pptx`, `.xlsx`, `.xls`, `.msg` | Preserves headings, tables, slide titles/notes, and sheet tabs as Markdown sections. |
| **PDF & Ebooks** | `.pdf`, `.epub` | Extracts embedded text and reading order (use Azure Doc Intelligence for scanned PDFs). |
| **Web & Structured** | `.html`, `.htm`, `.csv`, `.json`, `.xml`, RSS | Converts DOM hierarchy and tabular/structured nodes to readable Markdown. |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.webp` | Extracts EXIF metadata and optional LLM vision descriptions when `llm_client` is configured. |
| **Audio & Video** | `.wav`, `.mp3`, YouTube URLs | Extracts metadata and speech transcripts (requires transcription extras / `ffmpeg`). |
| **Archives** | `.zip` | Recursively iterates contained files and concatenates converted Markdown outputs. |

---

## Installation & Environment Setup

### 1. Package Installation
Install only the dependencies needed for your workflow, or install all format converters at once:

```bash
# Minimal core installation
pip install markitdown

# Full installation with all built-in format converters (recommended for swarm environments)
pip install "markitdown[all]"

# Isolated global CLI installation via pipx or uv
pipx install "markitdown[all]"
# OR
uv tool install "markitdown[all]"
```

### 2. Selective Optional Extras
When minimizing container or virtualenv footprint, install only required extras:

```bash
pip install "markitdown[pdf,docx,pptx,xlsx]"
# Other available extras:
#   xls, outlook, az-doc-intel, audio-transcription, youtube-transcription
```

### 3. System & Environment Verification
```bash
# Verify CLI availability and version
markitdown --help

# Optional: verify ffmpeg is on PATH for compressed audio (.mp3, .m4a) conversion
command -v ffmpeg || echo "ffmpeg missing: WAV works natively; MP3/M4A requires ffmpeg"
```

---

## CLI Recipes

### Standard File Conversion
```bash
# Convert to stdout
markitdown input.pdf

# Write output directly to a Markdown file (-o / --output)
markitdown whitepaper.pdf -o whitepaper.md

# Convert via stdin piping
cat exported_page.html | markitdown > exported_page.md
```

### Format-Specific Examples
```bash
# PDF technical report / whitepaper
markitdown architecture_whitepaper.pdf -o architecture_whitepaper.md

# Microsoft Word (.docx) legacy specification
markitdown legacy_api_spec.docx -o legacy_api_spec.md

# PowerPoint (.pptx) presentation deck (preserves slide boundaries & speaker notes)
markitdown q4_platform_roadmap.pptx -o q4_platform_roadmap.md

# Excel (.xlsx) multi-sheet workbook (renders each sheet as a Markdown table)
markitdown benchmark_results.xlsx -o benchmark_results.md

# HTML documentation export
markitdown confluence_export.html -o confluence_export.md

# Image (EXIF metadata; combine with Python llm_client for visual descriptions)
markitdown system_diagram.png -o system_diagram.md

# Audio recording transcription (requires markitdown[audio-transcription] + ffmpeg for mp3)
markitdown stakeholder_interview.mp3 -o stakeholder_interview.md
```

### Plugins & Scanned PDFs (Azure Document Intelligence)
```bash
# List installed 3rd-party MarkItDown plugins
markitdown --list-plugins

# Enable installed plugins during conversion
markitdown --use-plugins complex_document.pdf -o complex_document.md

# Use Azure Document Intelligence for scanned PDFs or complex multi-column layouts
markitdown -d -e "https://<your-resource>.cognitiveservices.azure.com/" scanned.pdf -o scanned.md
```

### Batch Directory Conversion
```bash
mkdir -p converted_md
for f in legacy_docs/*.{pdf,docx,pptx,xlsx,html}; do
  [ -e "$f" ] || continue
  base=$(basename "${f%.*}")
  markitdown "$f" -o "converted_md/${base}.md"
done
```

---

## Python API Integration Patterns

### 1. Basic Local Conversion
```python
from pathlib import Path
from markitdown import MarkItDown

def convert_to_markdown(source_path: str, output_path: str | None = None) -> str:
    """Convert a supported document to Markdown and optionally persist to disk."""
    md = MarkItDown(enable_plugins=False)
    result = md.convert(source_path)
    content = result.text_content
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
    return content
```

### 2. Stream Conversion (In-Memory Buffers / HTTP Downloads)
```python
import io
from markitdown import MarkItDown, StreamInfo

md = MarkItDown()
raw_bytes = Path("report.docx").read_bytes()
result = md.convert_stream(
    io.BytesIO(raw_bytes),
    stream_info=StreamInfo(extension=".docx"),
)
print(result.text_content)
```

### 3. Multimodal Image Captioning via LLM Client
```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("network_topology.png")
print(result.text_content)
```

### 4. Resilient Batch Processor with Per-File Error Handling
```python
from pathlib import Path
from markitdown import MarkItDown

SUPPORTED_EXTS = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".csv", ".json"}

def batch_convert(src_dir: Path, dst_dir: Path) -> dict[str, str]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    md = MarkItDown(enable_plugins=False)
    report: dict[str, str] = {}

    for path in sorted(src_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTS:
            continue
        out_file = dst_dir / f"{path.stem}.md"
        try:
            res = md.convert(str(path))
            out_file.write_text(res.text_content, encoding="utf-8")
            report[str(path)] = f"ok -> {out_file}"
        except Exception as exc:
            report[str(path)] = f"error: {exc}"
    return report
```

---

## Guidelines for `docs-agent` (Legacy Office Migration to Diátaxis)

When migrating legacy Word specs (`.docx`), slide decks (`.pptx`), PDF manuals (`.pdf`), spreadsheets (`.xlsx`), or wiki exports (`.html`) into developer documentation:

1. **Convert to Scratch First, Never Publish Raw Output**:
   - Invoke `markitdown <source> -o <scratch_path>.md` via `run_command`.
   - Treat the converted Markdown as raw source material, never final documentation.
2. **Enforce Diátaxis Quadrant Decomposition**:
   - Split monolithic `.docx` or `.pdf` manuals into strict Diátaxis quadrants:
     - **Tutorials** (`docs/tutorials/`): 0-to-1 onboarding paths extracted from intro chapters.
     - **How-To Guides** (`docs/how-to/`): Task-oriented procedures extracted from runbooks or SOPs.
     - **Reference** (`docs/reference/`): Parameter tables, CLI flags, and schemas verified against `arch_schema.md` and actual code.
     - **Explanation / ADRs** (`docs/explanation/`, `docs/adr/`): Rationale and trade-offs extracted from architecture decks or RFCs.
3. **Post-Conversion Hygiene Checklist**:
   - Normalize heading hierarchy (ensure a single `# H1` per document and monotonic `H2`/`H3` nesting).
   - Remove slide-deck boilerplate (`<!-- Slide number: N -->`, repeated footers, page numbers).
   - Inspect converted Markdown tables for wrapped/merged cells from `.pdf` or `.docx` and repair column alignment.
   - Replace static embedded diagram references from `.pptx`/`.docx` with GitHub-native **Mermaid** (`flowchart`, `sequenceDiagram`) whenever the architecture is representable in code.
   - Re-verify all API payloads, endpoints, and CLI commands against current repository source files before committing.

---

## Guidelines for `research-agent` (Multi-Format Ingestion into `research_dossier.md`)

When ingesting whitepapers, vendor decks, spreadsheets, or recorded talks into `.agents/blackboard/research_dossier.md`:

1. **Standardize Heterogeneous Inputs Before Synthesis**:
   - Convert `.pdf` whitepapers, `.pptx` conference decks, `.xlsx` data tables, and `.html` snapshots to Markdown files in a scratch directory (`-o`) so findings can be searched economically with `rg` and read selectively with line ranges.
2. **Maintain Numbered Provenance (`[RES-xx]`)**:
   - Every insight distilled into `research_dossier.md` must cite the source artifact, conversion method, and exact structural anchor (e.g., `whitepaper.pdf` via MarkItDown, Section 3.2; `deck.pptx`, Slide 14; `benchmarks.xlsx`, Sheet `Latency_P99`).
   - Record all ingested files in the dossier's **Platform Provenance Matrix**.
3. **Cross-Check Quantitative Data & Tables**:
   - MarkItDown renders Excel formulas by their cached values and can flatten complex PDF multi-column tables. Before citing numbers in `[RES-xx]` findings, inspect the extracted Markdown table around the relevant lines to confirm headers and units align.
4. **Prevent Context Bloat**:
   - Never copy-paste full converted Markdown documents into `.agents/blackboard/research_dossier.md` or `#council` / `#builders` messages. Summarize verified evidence, key metrics, and architectural implications concisely.

---

## Common Pitfalls & Constraints

- **Scanned / Image-Only PDFs**: Standard `markitdown` PDF extraction reads embedded text streams; scanned PDFs yield empty or minimal output unless processed with Azure Document Intelligence (`-d -e <endpoint>`) or an OCR preprocessor.
- **Audio Format Dependencies**: Converting `.mp3` or `.m4a` files requires `ffmpeg` installed on the system `$PATH` in addition to `markitdown[audio-transcription]`.
- **Large Workbooks & Multi-Hundred-Page PDFs**: Always write output to a file (`-o`) instead of streaming massive output directly into terminal stdout; inspect the generated Markdown selectively using `rg` and bounded `read_file` ranges.
- **Formulas in `.xlsx`**: `markitdown` surfaces cached cell values rather than live Excel formula expressions; if formula audit is required, pair with the `xlsx` catalog skill (`openpyxl`).
