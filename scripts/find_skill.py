#!/usr/bin/env python3
"""
find_skill.py - Just-in-Time (JIT) Skill Retrieval Utility for Wayne Custom Orchestrator

Discovers, searches, and inspects agentic skills from the Cold Storage catalog
(skills/catalog/ or .agents/skills/catalog/) with zero prompt context bloat.
Used by the Swarm Router to selectively mount domain skills only to target subagents.
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path


def find_catalog_dirs():
    """Discover active catalog and skill directories from plugin or workspace."""
    script_dir = Path(__file__).resolve().parent
    plugin_root = script_dir.parent
    
    candidates = [
        plugin_root / "skills" / "catalog",
        plugin_root / ".agents" / "skills" / "catalog",
        Path.cwd() / "skills" / "catalog",
        Path.cwd() / ".agents" / "skills" / "catalog",
    ]
    for c in candidates:
        if c.is_dir() and (c / "index.json").is_file():
            return c, c / "index.json", c.parent
            
    # Default to plugin_root/skills/catalog
    default_cat = plugin_root / "skills" / "catalog"
    return default_cat, default_cat / "index.json", plugin_root / "skills"


CATALOG_DIR, INDEX_FILE, SKILLS_ROOT = find_catalog_dirs()


def parse_frontmatter(file_path: Path) -> dict:
    """Extract YAML frontmatter from SKILL.md without external dependencies."""
    if not file_path.is_file():
        return {}
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}

    fm_text = match.group(1)
    metadata = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            metadata[key] = val
    return metadata


def load_catalog_index() -> list:
    """Load curated skills from index.json."""
    if not INDEX_FILE.is_file():
        return []
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("skills", [])
    except Exception as e:
        print(f"Warning: Failed to parse {INDEX_FILE}: {e}", file=sys.stderr)
        return []


def discover_all_skills() -> list:
    """Aggregate skills from index.json, active skills, and catalog folders."""
    catalog_skills = load_catalog_index()
    skills_by_id = {s["id"]: s for s in catalog_skills}

    # Check for local files in catalog
    if CATALOG_DIR.is_dir():
        for item in CATALOG_DIR.iterdir():
            if item.is_dir() and not item.name.startswith((".", "_", "downloads")):
                skill_md = item / "SKILL.md"
                if skill_md.is_file():
                    skill_id = item.name
                    rel_path = str(skill_md)
                    if skill_id in skills_by_id:
                        skills_by_id[skill_id]["local_path"] = rel_path
                        skills_by_id[skill_id]["status"] = "local"
                    else:
                        fm = parse_frontmatter(skill_md)
                        skills_by_id[skill_id] = {
                            "id": skill_id,
                            "name": fm.get("name", skill_id),
                            "category": "catalog-local",
                            "description": fm.get("description", f"Local skill in {rel_path}"),
                            "tags": [skill_id],
                            "target_subagent": "builder-agent",
                            "status": "local",
                            "local_path": rel_path,
                            "source_url": "local"
                        }

    # Discover other active skills in skills/
    if SKILLS_ROOT.is_dir():
        for item in SKILLS_ROOT.iterdir():
            if item.is_dir() and item.name not in ("catalog", ".system_generated"):
                skill_md = item / "SKILL.md"
                if skill_md.is_file():
                    skill_id = item.name
                    rel_path = str(skill_md)
                    if skill_id in skills_by_id:
                        skills_by_id[skill_id]["status"] = "active"
                        skills_by_id[skill_id]["local_path"] = rel_path
                    else:
                        fm = parse_frontmatter(skill_md)
                        skills_by_id[skill_id] = {
                            "id": skill_id,
                            "name": fm.get("name", skill_id.title()),
                            "category": "active-core",
                            "description": fm.get("description", f"Active skill in {rel_path}"),
                            "tags": [skill_id],
                            "target_subagent": "builder-agent",
                            "status": "active",
                            "local_path": rel_path,
                            "source_url": "local"
                        }

    return list(skills_by_id.values())


def search_skills(query: str = "", category: str = None, tag: str = None, subagent: str = None, active_only: bool = False) -> list:
    all_skills = discover_all_skills()
    results = []

    q_terms = [t.lower() for t in query.split()] if query else []

    for s in all_skills:
        if active_only and s.get("status") != "active":
            continue

        if category and s.get("category", "").lower() != category.lower():
            continue

        if subagent and s.get("target_subagent", "").lower() != subagent.lower():
            continue

        if tag:
            tags = [t.lower() for t in s.get("tags", [])]
            if tag.lower() not in tags:
                continue

        if q_terms:
            text = f"{s.get('id', '')} {s.get('name', '')} {s.get('description', '')} {' '.join(s.get('tags', []))}".lower()
            if not all(term in text for term in q_terms):
                continue

        results.append(s)

    return results


def format_markdown(skills: list, query_str: str = "") -> str:
    if not skills:
        return f"🔍 No skills matching `{query_str}` found in catalog."

    lines = [f"## 🔍 JIT Skill Discovery: Found {len(skills)} matching skill{'s' if len(skills) != 1 else ''}:"]
    for s in skills:
        sid = s.get("id")
        name = s.get("name", sid)
        status = s.get("status", "catalog")
        target = s.get("target_subagent", "builder-agent")
        local_path = s.get("local_path", f"skills/catalog/{sid}/SKILL.md")
        lines.append(f"- `{sid}` ({status}): **{name}** | Target: `{target}` | Path: `{local_path}`")
    return "\n".join(lines)


def fetch_skill(skill_id: str) -> None:
    """Fetch or check a skill locally."""
    target_dir = CATALOG_DIR / skill_id
    target_file = target_dir / "SKILL.md"

    if target_file.is_file():
        print(f"✅ Skill `{skill_id}` is already cached locally at: {target_file}")
        return

    skills = {s["id"]: s for s in load_catalog_index()}
    if skill_id in skills:
        src = skills[skill_id].get("source_url", "")
        print(f"ℹ️ Skill `{skill_id}` ({skills[skill_id].get('name')}):")
        print(f"   Target Subagent: {skills[skill_id].get('target_subagent', 'builder-agent')}")
        print(f"   Description: {skills[skill_id].get('description')}")
        print(f"   To implement, use template at: {CATALOG_DIR / '_template' / 'SKILL.md'}")
    else:
        print(f"❌ Skill `{skill_id}` not found in catalog index.")


def main():
    parser = argparse.ArgumentParser(
        description="Just-in-Time (JIT) Skill Retrieval Utility for Wayne Custom Swarm.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("query", nargs="?", default=None, help="Search query (keywords, skill name, format)")
    parser.add_argument("--list", action="store_true", help="List all catalog and active skills")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--tag", "-t", help="Filter by tag")
    parser.add_argument("--subagent", "-s", help="Filter by recommended subagent")
    parser.add_argument("--active", action="store_true", help="Show active workspace skills only")
    parser.add_argument("--fetch", help="Inspect/hydrate a catalog skill")
    parser.add_argument("--format", choices=["markdown", "json", "compact"], default="markdown", help="Output format")

    args = parser.parse_args()

    if args.fetch:
        fetch_skill(args.fetch)
        return

    query_str = args.query if args.query else ""
    if args.list:
        query_str = ""

    matches = search_skills(
        query=query_str,
        category=args.category,
        tag=args.tag,
        subagent=args.subagent,
        active_only=args.active
    )

    if args.format == "json":
        clean_matches = [{k: v for k, v in m.items() if not k.startswith("_")} for m in matches]
        print(json.dumps({"count": len(clean_matches), "skills": clean_matches}, indent=2))
    elif args.format == "compact":
        for s in matches:
            print(f"{s['id']:<20} [{s.get('category', 'unknown'):<20}] -> {s.get('target_subagent', 'builder-agent'):<18} ({s.get('status', 'catalog')})")
    else:
        print(format_markdown(matches, query_str=query_str or ("All Skills" if args.list else "")))


if __name__ == "__main__":
    main()
