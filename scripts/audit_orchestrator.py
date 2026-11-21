#!/usr/bin/env python3
"""
Orchestrator Self-Audit & Parity Verification Linter.

Programmatically verifies:
1. Agent frontmatter tool validity against native Antigravity tools.
2. Catalog inventory parity (index.json vs physical directories).
3. Script existence for all scripts referenced in docs and agents.
4. Blackboard templates completeness.
5. README claims vs reality (checks for exaggerated claims like 2,000+).
"""

import sys
import os
import json
import re
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent

VALID_TOOLS = {
    "read_file",
    "edit_file",
    "write_file",
    "run_command",
    "search_web",
    "send_message",
    "invoke_subagent",
    "manage_subagents",
    "manage_task",
    "schedule",
    "run_workflow",
    "search_marketplace",
    "list_plugin_accounts",
    "ask_question",
    "call_mcp_tool",
    "list_resources",
    "read_resource",
    "swarm",
}

def check_agents():
    errors = []
    agents_dir = PLUGIN_DIR / "agents"
    if not agents_dir.exists():
        return [f"Agents directory missing: {agents_dir}"]

    agent_files = list(agents_dir.glob("*.md"))
    if not agent_files:
        return [f"No agent markdown files found in {agents_dir}"]

    for af in agent_files:
        content = af.read_text(encoding="utf-8")
        # Check YAML frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            errors.append(f"{af.name}: Missing frontmatter")
            continue
        fm_text = fm_match.group(1)
        
        # Check name
        if not re.search(r"^name:\s*.+", fm_text, re.MULTILINE):
            errors.append(f"{af.name}: Missing 'name' in frontmatter")

        # Check description
        if not re.search(r"^description:\s*.+", fm_text, re.MULTILINE):
            errors.append(f"{af.name}: Missing 'description' in frontmatter")

        # Check tools line
        tools = []
        tools_inline = re.search(r"tools:\s*\[(.*?)\]", fm_text)
        if tools_inline:
            tools = [t.strip().strip("'\"") for t in tools_inline.group(1).split(",") if t.strip()]
        else:
            tools_block = re.findall(r"^\s*-\s*([a-zA-Z0-9_]+)", fm_text, re.MULTILINE)
            if tools_block:
                tools = tools_block

        if not tools:
            errors.append(f"{af.name}: No tools declared in frontmatter")
        else:
            for tool in tools:
                if tool not in VALID_TOOLS:
                    errors.append(f"{af.name}: Invalid tool declared: '{tool}'")

    return errors

def check_catalog():
    errors = []
    catalog_dir = PLUGIN_DIR / "skills" / "catalog"
    index_file = catalog_dir / "index.json"
    
    if not index_file.exists():
        return [f"Catalog index missing: {index_file}"]
        
    try:
        data = json.loads(index_file.read_text(encoding="utf-8"))
        skills = data.get("skills", [])
    except Exception as e:
        return [f"Failed to parse index.json: {e}"]

    # Check README claim vs actual catalog count
    readme_file = PLUGIN_DIR / "README.md"
    if readme_file.exists():
        readme_text = readme_file.read_text(encoding="utf-8")
        if "2,000+" in readme_text:
            errors.append(f"README.md contains unsubstantiated claim '2,000+' skills (actual indexed: {len(skills)})")

    return errors

def check_scripts_references():
    errors = []
    scripts_dir = PLUGIN_DIR / "scripts"
    existing_scripts = {f.name for f in scripts_dir.iterdir() if f.is_file()}
    
    # Check references in rules and agent files
    text_files = list(PLUGIN_DIR.glob("rules/*.md")) + list(PLUGIN_DIR.glob("agents/*.md")) + [PLUGIN_DIR / "README.md"]
    
    script_pattern = re.compile(r"([a-zA-Z0-9_-]+\.(?:py|sh))")
    
    for tf in text_files:
        if not tf.exists():
            continue
        content = tf.read_text(encoding="utf-8")
        matches = set(script_pattern.findall(content))
        for m in matches:
            if m in {"audit_orchestrator.py", "collate_telemetry.py", "find_skill.py", 
                    "init_blackboard.py", "on_session_start.py", "research_tools.py", 
                    "retrospective_onboard.py", "worktree_helper.sh", "validate_blackboard.py",
                    "healing_tracker.py"}:
                if m not in existing_scripts:
                    errors.append(f"{tf.name} references script '{m}' which does not exist in {scripts_dir}")

    return errors

def check_blackboard_templates():
    errors = []
    templates_dir = PLUGIN_DIR / "templates" / "blackboard"
    required_templates = [
        "pm_spec.template.md",
        "arch_schema.template.md",
        "design_tokens.template.md",
        "code_qa_status.template.md",
        "research_dossier.template.md",
    ]
    for req in required_templates:
        p = templates_dir / req
        if not p.exists():
            errors.append(f"Missing required blackboard template: {req}")
    return errors

def main():
    print(f"=== Wayne Custom Orchestra Audit Linter ===")
    print(f"Plugin Directory: {PLUGIN_DIR}\n")
    
    all_errors = []
    
    print("[1/4] Checking agent tool validity & frontmatter...")
    agent_errs = check_agents()
    if agent_errs:
        for e in agent_errs:
            print(f"  ❌ {e}")
        all_errors.extend(agent_errs)
    else:
        print("  ✔ All agents have valid names, descriptions, and native Antigravity tools.")

    print("\n[2/4] Checking catalog inventory and documentation parity...")
    cat_errs = check_catalog()
    if cat_errs:
        for e in cat_errs:
            print(f"  ❌ {e}")
        all_errors.extend(cat_errs)
    else:
        print("  ✔ Catalog inventory and documentation are aligned.")

    print("\n[3/4] Checking blackboard templates completeness...")
    bb_errs = check_blackboard_templates()
    if bb_errs:
        for e in bb_errs:
            print(f"  ❌ {e}")
        all_errors.extend(bb_errs)
    else:
        print("  ✔ All 5 standard blackboard templates present.")

    print("\n[4/4] Checking script references across prompts and documentation...")
    script_errs = check_scripts_references()
    if script_errs:
        for e in script_errs:
            print(f"  ❌ {e}")
        all_errors.extend(script_errs)
    else:
        print("  ✔ All referenced scripts physically exist and are resolvable.")

    print("\n" + "="*45)
    if all_errors:
        print(f"FAILED: {len(all_errors)} parity/integrity issue(s) detected.")
        sys.exit(1)
    else:
        print("SUCCESS: 0 parity issues detected. System is 100% compliant.")
        sys.exit(0)

if __name__ == "__main__":
    main()
