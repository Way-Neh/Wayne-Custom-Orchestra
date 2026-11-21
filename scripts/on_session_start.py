#!/usr/bin/env python3
"""
on_session_start.py - Automatic Workspace Bootstrapper for Wayne Custom Swarm.

Fires on Antigravity SessionStart lifecycle hook.
Automatically initializes Git (if missing) and scaffolds .agents/blackboard/
contracts in new project workspaces without requiring manual user commands.
"""

import sys
import json
import os
import subprocess
from pathlib import Path


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    workspaces = data.get("workspacePaths") or []
    cwd = data.get("cwd") or os.getcwd()
    target = Path(workspaces[0] if workspaces else cwd).resolve()

    # Skip internal root directories to prevent pollution
    home = Path.home()
    if target in [home, Path("/"), home / "Desktop", home / "Downloads"]:
        print(json.dumps({}))
        return

    bb_dir = target / ".agents" / "blackboard"
    actions = []

    # 1. Initialize Git repository if missing
    if not (target / ".git").is_dir():
        try:
            subprocess.run(["git", "init"], cwd=target, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            actions.append("Initialized Git repository")
        except Exception:
            pass

    # 2. Initialize .agents/blackboard/ if missing or incomplete
    if not (bb_dir / "pm_spec.md").is_file():
        script_dir = Path(__file__).resolve().parent
        templates_dir = script_dir.parent / "templates" / "blackboard"
        bb_dir.mkdir(parents=True, exist_ok=True)

        files = [
            ("research_dossier.template.md", "research_dossier.md"),
            ("pm_spec.template.md", "pm_spec.md"),
            ("design_tokens.template.md", "design_tokens.md"),
            ("arch_schema.template.md", "arch_schema.md"),
            ("code_qa_status.template.md", "code_qa_status.md"),
        ]
        created = []
        for src_name, dest_name in files:
            dest = bb_dir / dest_name
            if not dest.is_file():
                src = templates_dir / src_name
                if src.is_file():
                    content = src.read_text(encoding="utf-8").replace("{{PROJECT_TITLE}}", target.name)
                    dest.write_text(content, encoding="utf-8")
                else:
                    dest.touch()
                created.append(dest_name)
        if created:
            actions.append("Auto-bootstrapped `.agents/blackboard/` contracts")

    # 3. Ensure .gitignore protects .worktrees/
    gitignore = target / ".gitignore"
    if (target / ".git").is_dir():
        if gitignore.is_file():
            text = gitignore.read_text(encoding="utf-8", errors="ignore")
            if ".worktrees" not in text:
                with open(gitignore, "a", encoding="utf-8") as f:
                    f.write("\n.worktrees/\n")
        else:
            gitignore.write_text(".worktrees/\n", encoding="utf-8")

    if actions:
        result = {
            "injectSteps": [
                {
                    "systemMessage": {
                        "systemMessage": f"🎻 Wayne Custom Orchestra: {'; '.join(actions)} for workspace `{target.name}`."
                    }
                }
            ]
        }
        print(json.dumps(result))
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
