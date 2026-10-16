#!/usr/bin/env python3
"""
find_skill.py - Just-in-Time (JIT) Skill Retrieval Utility for Wayne Custom Orchestrator

Discovers, searches, and inspects agentic skills from the Cold Storage catalog
(.agents/skills/catalog/) and active skills (.agents/skills/) with zero prompt context bloat.
Used by the Swarm Router to selectively mount domain skills only to target subagents.
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path

# Paths relative to workspace root
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_DIR = WORKSPACE_ROOT / ".agents" / "skills" / "catalog"
ACTIVE_SKILLS_DIR = WORKSPACE_ROOT / ".agents" / "skills"
INDEX_FILE = CATALOG_DIR / "index.json"
ROSTER_DIR = WORKSPACE_ROOT / ".agents" / "roster"

# Fallback path to agentic-awesome-skills npm package if installed locally
AAS_NPM_PATH = Path.home() / ".npm" / "_npx" / "0cf0c6a227c7a933" / "node_modules" / "agentic-awesome-skills"


def parse_frontmatter(file_path: Path) -> dict:
    """Extract YAML-like frontmatter from SKILL.md without external dependencies."""
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
                    rel_path = str(skill_md.relative_to(WORKSPACE_ROOT))
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

    # Discover active skills in .agents/skills/ (excluding catalog)
    if ACTIVE_SKILLS_DIR.is_dir():
        for item in ACTIVE_SKILLS_DIR.iterdir():
            if item.is_dir() and item.name not in ("catalog", ".system_generated"):
                skill_md = item / "SKILL.md"
                if skill_md.is_file():
                    skill_id = item.name
                    rel_path = str(skill_md.relative_to(WORKSPACE_ROOT))
                    if skill_id in skills_by_id:
                        skills_by_id[skill_id]["status"] = "active"
                        skills_by_id[skill_id]["local_path"] = rel_path
                    else:
                        fm = parse_frontmatter(skill_md)
                        skills_by_id[skill_id] = {
                            "id": skill_id,
                            "name": fm.get("name", skill_id.title()),
                            "category": "active-core",
                            "description": fm.get("description", f"Active workspace skill in {rel_path}"),
                            "tags": [skill_id, "active"],
                            "target_subagent": "design-agent" if "design" in skill_id or skill_id == "impeccable" else "builder-agent",
                            "status": "active",
                            "local_path": rel_path,
                            "source_url": "local"
                        }

    return list(skills_by_id.values())


def score_skill(skill: dict, query_terms: list) -> int:
    """Score a skill based on query term matches."""
    if not query_terms:
        return 1

    score = 0
    sid = skill.get("id", "").lower()
    sname = skill.get("name", "").lower()
    scat = skill.get("category", "").lower()
    sdesc = skill.get("description", "").lower()
    stags = [t.lower() for t in skill.get("tags", [])]
    target = skill.get("target_subagent", "").lower()

    for term in query_terms:
        term = term.lower()
        if term == sid:
            score += 100
        elif term in sid:
            score += 40
        if term in sname:
            score += 30
        if term in stags:
            score += 25
        if term in scat:
            score += 15
        if term in target:
            score += 15
        if term in sdesc:
            score += 10

    return score


def search_skills(query: str = None, category: str = None, tag: str = None, subagent: str = None, active_only: bool = False) -> list:
    """Filter and score skills."""
    all_skills = discover_all_skills()
    results = []

    query_terms = query.split() if query else []

    for skill in all_skills:
        if active_only and skill.get("status") != "active":
            continue
        if category and category.lower() not in skill.get("category", "").lower():
            continue
        if tag and not any(tag.lower() in t.lower() for t in skill.get("tags", [])):
            continue
        if subagent and subagent.lower() not in skill.get("target_subagent", "").lower():
            continue

        score = score_skill(skill, query_terms)
        if score > 0:
            skill_copy = dict(skill)
            skill_copy["_score"] = score
            results.append(skill_copy)

    results.sort(key=lambda s: s["_score"], reverse=True)
    return results


def format_markdown(matches: list, query_str: str = "") -> str:
    """Format search results into clean, actionable Markdown."""
    if not matches:
        return f"### ⚠️ No skills found matching: `{query_str}`\n\nRun `python3 .agents/scripts/find_skill.py --list` to view all available catalog skills."

    header = f"## 🔍 Just-in-Time (JIT) Skill Discovery"
    if query_str:
        header += f': "{query_str}"'
    header += f"\n\nFound **{len(matches)}** matching skill{'s' if len(matches) != 1 else ''}:\n"

    blocks = [header]
    for s in matches:
        sid = s.get("id")
        name = s.get("name", sid)
        cat = s.get("category", "general")
        target = s.get("target_subagent", "builder-agent")
        status = s.get("status", "catalog")
        desc = s.get("description", "No description provided.")
        tags = ", ".join(f"`{t}`" for t in s.get("tags", []))
        local_path = s.get("local_path")
        source = s.get("source_url", "N/A")

        status_badge = {
            "active": "🟢 Active Workspace Skill",
            "local": "📦 Cold Catalog (Cached Offline)",
            "catalog": "🌐 Cold Catalog (On-Demand / Remote)"
        }.get(status, f"ℹ️ {status}")

        block = f"### 🛠️ `{sid}` - {name}\n"
        block += f"- **Status**: {status_badge}\n"
        block += f"- **Category**: `{cat}`\n"
        block += f"- **Recommended Subagent**: [`{target}`](file:///.agents/roster/{target}/AGENTS.md)\n"
        if local_path:
            block += f"- **Local Path**: [`{local_path}`](file:///{local_path})\n"
        block += f"- **Description**: {desc}\n"
        block += f"- **Tags**: {tags}\n"
        if source and source != "local":
            block += f"- **Source URL**: {source}\n"

        # Provide concrete JIT invocation recipe
        path_to_ref = local_path if local_path else f".agents/skills/catalog/{sid}/SKILL.md (fetch on demand)"
        block += f"\n#### 💡 JIT Mount Instruction (Zero Context Bloat):\n"
        block += f"```python\n"
        block += f"# In Root Orchestrator or Swarm Router (Zero root token overhead):\n"
        block += f'invoke_subagent(\n'
        block += f'    TypeName="{target}",\n'
        block += f'    Role="{target.replace("-agent", "").title()} ({sid.upper()} Specialist)",\n'
        block += f'    Workspace="share",\n'
        block += f'    Prompt="Follow domain skill instructions at {path_to_ref} to execute the task."\n'
        block += f')\n'
        block += f"```\n"

        blocks.append(block)

    return "\n".join(blocks)


def fetch_skill(skill_id: str) -> None:
    """Fetch or cache a skill locally into .agents/skills/catalog/<skill_id>/."""
    target_dir = CATALOG_DIR / skill_id
    target_file = target_dir / "SKILL.md"

    if target_file.is_file():
        print(f"✅ Skill `{skill_id}` is already cached locally at: {target_file.relative_to(WORKSPACE_ROOT)}")
        return

    # Check if present in local AAS node_modules
    if AAS_NPM_PATH.is_dir():
        aas_skill_dir = AAS_NPM_PATH / "skills" / f"{skill_id}-official"
        if not aas_skill_dir.is_dir():
            aas_skill_dir = AAS_NPM_PATH / "skills" / skill_id

        if aas_skill_dir.is_dir() and (aas_skill_dir / "SKILL.md").is_file():
            target_dir.mkdir(parents=True, exist_ok=True)
            src_md = aas_skill_dir / "SKILL.md"
            target_file.write_text(src_md.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"✅ Successfully hydrated `{skill_id}` from local AAS package to: {target_file.relative_to(WORKSPACE_ROOT)}")
            return

    # Check catalog index for source
    skills = {s["id"]: s for s in load_catalog_index()}
    if skill_id in skills:
        src = skills[skill_id].get("source_url", "")
        print(f"📥 Remote fetch required for `{skill_id}`.")
        print(f"Source repository: {src}")
        print(f"\nTo fetch and store in cold catalog:")
        print(f"  mkdir -p .agents/skills/catalog/{skill_id}")
        print(f"  curl -sSL {src}/raw/main/SKILL.md -o .agents/skills/catalog/{skill_id}/SKILL.md")
    else:
        print(f"❌ Skill `{skill_id}` not found in catalog index.")


def main():
    parser = argparse.ArgumentParser(
        description="Just-in-Time (JIT) Skill Retrieval Utility for Wayne Custom Swarm.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 .agents/scripts/find_skill.py docx
  python3 .agents/scripts/find_skill.py --list
  python3 .agents/scripts/find_skill.py --category devops
  python3 .agents/scripts/find_skill.py --subagent docs-agent
  python3 .agents/scripts/find_skill.py --fetch pptx
  python3 .agents/scripts/find_skill.py "pdf form" --format json
        """
    )
    parser.add_argument("query", nargs="?", default=None, help="Search query (keywords, skill name, format)")
    parser.add_argument("--list", action="store_true", help="List all catalog and active skills")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--tag", "-t", help="Filter by tag")
    parser.add_argument("--subagent", "-s", help="Filter by recommended subagent")
    parser.add_argument("--active", action="store_true", help="Show active workspace skills only")
    parser.add_argument("--fetch", help="Hydrate/cache a remote skill into .agents/skills/catalog/<skill_id>/")
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
