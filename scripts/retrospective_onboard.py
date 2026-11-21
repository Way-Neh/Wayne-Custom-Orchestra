#!/usr/bin/env python3
"""
retrospective_onboard.py - Retroactive Project Onboarding for Wayne Custom Swarm.

Scans all user project directories and safely retrofits:
1. Git repository initialization (if missing)
2. .agents/blackboard/ contracts (adds missing contracts, never overwrites existing files)
3. .worktrees/ entry in .gitignore
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def get_default_project_paths():
    candidates = []

    # 1. Subdirectories of agy_projects
    agy_root = Path("/home/wayne/agy_projects")
    if agy_root.is_dir():
        for d in sorted(agy_root.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                if d.name == "GitHub":
                    orch = d / "Wayne-Custom-Orchestra"
                    if orch.is_dir():
                        candidates.append(orch)
                else:
                    candidates.append(d)

    # 2. Subdirectories of teamwork_projects
    tw_root = Path("/home/wayne/teamwork_projects")
    if tw_root.is_dir():
        for d in sorted(tw_root.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                candidates.append(d)

    # 3. Subdirectories of gpt_projects
    gpt_root = Path("/home/wayne/gpt_projects")
    if gpt_root.is_dir():
        for d in sorted(gpt_root.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                candidates.append(d)

    # 4. Known project directories in home
    home_projects = [
        "drivingStuff", "visitingMalaysia", "HomeAnalysis", "RimsForMe",
        "marrow-mcp", "social-to-mealie", "sparkyfitness", "selfie-timelapse",
        "EthanDevelopment", "Cloudflare", "tinkerBox"
    ]
    for name in home_projects:
        p = Path("/home/wayne") / name
        if p.is_dir() and p not in candidates:
            candidates.append(p)

    return candidates


def onboard_project(target_dir: Path, templates_dir: Path, dry_run: bool = False):
    report = {
        "path": target_dir,
        "name": target_dir.name,
        "git_status": "already_git",
        "contracts_added": [],
        "contracts_existing": [],
        "gitignore_updated": False,
    }

    # 1. Git initialization
    is_git = (target_dir / ".git").is_dir()
    if not is_git:
        if not dry_run:
            try:
                subprocess.run(
                    ["git", "init"],
                    cwd=target_dir,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                report["git_status"] = "initialized"
            except Exception as e:
                report["git_status"] = f"error: {e}"
        else:
            report["git_status"] = "would_init"

    # 2. Blackboard contracts
    bb_dir = target_dir / ".agents" / "blackboard"
    files = [
        ("research_dossier.template.md", "research_dossier.md"),
        ("pm_spec.template.md", "pm_spec.md"),
        ("design_tokens.template.md", "design_tokens.md"),
        ("arch_schema.template.md", "arch_schema.md"),
        ("code_qa_status.template.md", "code_qa_status.md"),
    ]

    if not dry_run:
        bb_dir.mkdir(parents=True, exist_ok=True)

    for src_name, dest_name in files:
        dest = bb_dir / dest_name
        src = templates_dir / src_name
        if dest.is_file():
            report["contracts_existing"].append(dest_name)
        else:
            if not dry_run:
                if src.is_file():
                    content = src.read_text(encoding="utf-8").replace("{{PROJECT_TITLE}}", target_dir.name)
                    dest.write_text(content, encoding="utf-8")
                else:
                    dest.touch()
            report["contracts_added"].append(dest_name)

    # 3. .gitignore protection for .worktrees/
    gitignore = target_dir / ".gitignore"
    if (target_dir / ".git").is_dir() or report["git_status"] in ("initialized", "would_init"):
        if gitignore.is_file():
            text = gitignore.read_text(encoding="utf-8", errors="ignore")
            if ".worktrees" not in text:
                if not dry_run:
                    with open(gitignore, "a", encoding="utf-8") as f:
                        f.write("\n.worktrees/\n")
                report["gitignore_updated"] = True
        else:
            if not dry_run:
                gitignore.write_text(".worktrees/\n", encoding="utf-8")
            report["gitignore_updated"] = True

    return report


def main():
    parser = argparse.ArgumentParser(description="Retroactively onboard existing projects to Wayne Custom Swarm.")
    parser.add_argument("targets", nargs="*", help="Specific project directories (defaults to all known projects).")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without modifying disk.")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    templates_dir = script_dir.parent / "templates" / "blackboard"

    if args.targets:
        projects = [Path(t).resolve() for t in args.targets]
    else:
        projects = get_default_project_paths()

    print(f"\n🎻 Wayne Custom Swarm — Retrospective Project Onboarding")
    print(f"Mode: {'DRY RUN (Preview Only)' if args.dry_run else 'EXECUTE (Modifying Disk)'}")
    print(f"Total Projects Targeted: {len(projects)}\n")

    results = []
    for p in projects:
        if not p.is_dir():
            continue
        rep = onboard_project(p, templates_dir, dry_run=args.dry_run)
        results.append(rep)

    # Print summary table
    print(f"{'Project':<26} | {'Git Status':<12} | {'Contracts Added':<20} | {'Existing Kept':<15} | {'.gitignore':<10}")
    print("-" * 95)
    for r in results:
        added_str = f"+{len(r['contracts_added'])} files" if r['contracts_added'] else "All present"
        exist_str = f"{len(r['contracts_existing'])} kept" if r['contracts_existing'] else "None"
        git_str = "Git Init" if r['git_status'] in ("initialized", "would_init") else "Existing Git"
        ign_str = "Updated" if r['gitignore_updated'] else "Protected"
        print(f"{r['name']:<26} | {git_str:<12} | {added_str:<20} | {exist_str:<15} | {ign_str:<10}")

    print("\n✅ Retrospective onboarding complete!\n")


if __name__ == "__main__":
    main()
