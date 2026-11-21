#!/usr/bin/env python3
"""
init_blackboard.py - Blackboard Initializer for Wayne Custom Swarm.

Bootstraps `.agents/blackboard/` in the target project directory with
structured starter templates for cross-agent collaboration.
"""

import os
import sys
import argparse
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "blackboard"

FILES = [
    ("research_dossier.template.md", "research_dossier.md"),
    ("pm_spec.template.md", "pm_spec.md"),
    ("design_tokens.template.md", "design_tokens.md"),
    ("arch_schema.template.md", "arch_schema.md"),
    ("code_qa_status.template.md", "code_qa_status.md"),
]


def init_blackboard(target_dir: Path, title: str = "Project"):
    bb_dir = target_dir / ".agents" / "blackboard"
    bb_dir.mkdir(parents=True, exist_ok=True)

    print(f"📁 Initializing blackboard at: {bb_dir}")
    for src_name, dest_name in FILES:
        src = TEMPLATES_DIR / src_name
        dest = bb_dir / dest_name
        if dest.is_file():
            print(f"  ⏭️  Existing: {dest_name} (skipped)")
            continue
        if src.is_file():
            content = src.read_text(encoding="utf-8")
            content = content.replace("{{PROJECT_TITLE}}", title)
            dest.write_text(content, encoding="utf-8")
            print(f"  ✅ Created: {dest_name}")
        else:
            dest.touch()
            print(f"  ⚠️  Created empty: {dest_name}")

    print("✨ Blackboard initialized successfully!")


def main():
    parser = argparse.ArgumentParser(description="Initialize .agents/blackboard/ contracts.")
    parser.add_argument("target", nargs="?", default=".", help="Target project root directory (default: current dir).")
    parser.add_argument("--title", default="Project", help="Project title for templates.")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    init_blackboard(target_path, args.title)


if __name__ == "__main__":
    main()
