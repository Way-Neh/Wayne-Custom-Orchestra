#!/usr/bin/env python3
"""
swarm_orchestrator.py - Hybrid Swarm Orchestration Controller for Wayne Custom Orchestra.

Provides CLI utilities to bridge Wayne Custom Orchestra's 6-phase lifecycle and
machine blackboard contracts with Antigravity Native Swarm primitives:
  1. Standardized, persona-primed briefs for native `swarm{action: "add"}` calls.
  2. Native Swarm topic channel topology definitions (#council, #builders, #qa).
  3. Seamless integration with cyclic healing state tracker (healing_tracker.py)
     generating automated board announcements with sequence numbers and criterion IDs.

Usage:
  python3 scripts/swarm_orchestrator.py brief <agent_name> [--channel CHANNEL] [--slice SLICE] [--model MODEL] [--json]
  python3 scripts/swarm_orchestrator.py channels [--format {text,json,markdown}]
  python3 scripts/swarm_orchestrator.py record-qa --passed AC-01 AC-02 --failed AC-03 [--dir .agents/blackboard] [--seq SEQ]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any

# Ensure local script directory is on sys.path for sibling imports
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import healing_tracker
except ImportError:
    healing_tracker = None

# Canonical channel topology definitions
CHANNELS = {
    "council": {
        "name": "council",
        "description": "Spec staging, architectural threat modeling, STRIDE verification, and consensus locking.",
        "phases": ["Phase 1: PM Spec Staging", "Phase 2: LLM Council Consensus Gate"],
        "default_participants": ["pm-agent", "architect-agent", "council-challenger", "design-agent"],
        "primary_contracts": [
            ".agents/blackboard/pm_spec.md",
            ".agents/blackboard/arch_schema.md",
            ".agents/blackboard/design_tokens.md",
        ],
    },
    "builders": {
        "name": "builders",
        "description": "Concurrent feature construction in isolated Git worktrees and shared workspaces.",
        "phases": ["Phase 4: Swarm Router & Parallel Construction"],
        "default_participants": ["builder-agent", "builder-api", "builder-ui"],
        "primary_contracts": [
            ".agents/blackboard/pm_spec.md",
            ".agents/blackboard/design_tokens.md",
            ".agents/blackboard/arch_schema.md",
        ],
        "isolation_protocol": ".worktrees/worker-<id> on branch swarm/worker-<id>",
    },
    "qa": {
        "name": "qa",
        "description": "Adversarial verification, regression assertions, and bounded self-healing loop (<= 3 cycles).",
        "phases": ["Phase 5: Adversarial QA & Bounded Cyclic Self-Healing"],
        "default_participants": ["qa-adversary-agent", "builder-agent", "coordinator"],
        "primary_contracts": [
            ".agents/blackboard/code_qa_status.md",
            ".agents/blackboard/healing_state.json",
        ],
    },
    "research": {
        "name": "research",
        "description": "Upstream market, competitive intelligence, developer community sentiment, and video analysis.",
        "phases": ["Phase 0: Hybrid Research Cluster"],
        "default_participants": ["research-agent", "social-forum-agent", "media-intel-agent"],
        "primary_contracts": [
            ".agents/blackboard/research_dossier.md",
        ],
    },
}

# Persona metadata and brief templates
PERSONA_CONFIGS = {
    "pm-agent": {
        "canonical_name": "pm-agent",
        "spec_file": "agents/pm-agent.md",
        "default_channel": "council",
        "default_model": "gemini-3.8-flash-high",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/pm_spec.md",
        "summary": "Authoritative Product Manager for acceptance criteria and finite state tables.",
    },
    "architect-agent": {
        "canonical_name": "architect-agent",
        "spec_file": "agents/architect-agent.md",
        "default_channel": "council",
        "default_model": "gemini-3.8-flash-high",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/arch_schema.md",
        "summary": "Technical architecture pillar; authors Zod schemas, DB models, and STRIDE mitigations.",
    },
    "council-challenger": {
        "canonical_name": "council-challenger",
        "spec_file": "agents/council-challenger.md",
        "default_channel": "council",
        "default_model": "gemini-3.8-flash-high",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/arch_schema.md",
        "summary": "Adversarial council challenger; executes STRIDE threat modeling and concurrency audits.",
    },
    "builder-agent": {
        "canonical_name": "builder-agent",
        "spec_file": "agents/builder-agent.md",
        "default_channel": "builders",
        "default_model": "gemini-3.8-flash-medium",
        "default_workspace": "share",
        "primary_contract": ".agents/blackboard/pm_spec.md, .agents/blackboard/design_tokens.md, .agents/blackboard/arch_schema.md",
        "summary": "Construction engine; implements logic and UI styling in isolated Git worktrees.",
    },
    "qa-adversary-agent": {
        "canonical_name": "qa-adversary-agent",
        "spec_file": "agents/qa-adversary-agent.md",
        "default_channel": "qa",
        "default_model": "gemini-3.8-flash-high",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/code_qa_status.md",
        "summary": "Adversarial verification lead with cognitive parity; executes independent QA audits.",
    },
    "narrator": {
        "canonical_name": "narrator",
        "spec_file": None,
        "default_channel": "all",
        "default_model": "gemini-3.8-flash-low",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/",
        "summary": "Antigravity Live UI narrator for real-time overview of swarm milestones and metrics.",
    },
    "monitor": {
        "canonical_name": "monitor",
        "spec_file": None,
        "default_channel": "all",
        "default_model": "gemini-3.8-flash-low",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/",
        "summary": "Swarm stall watchdog and deadlock breaker across all topics.",
    },
    "research-agent": {
        "canonical_name": "research-agent",
        "spec_file": "agents/research-agent.md",
        "default_channel": "research",
        "default_model": "gemini-3.8-flash-high",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/research_dossier.md",
        "summary": "Lead researcher coordinating multilingual query matrix and platform provenance.",
    },
    "social-forum-agent": {
        "canonical_name": "social-forum-agent",
        "spec_file": "agents/social-forum-agent.md",
        "default_channel": "research",
        "default_model": "gemini-3.8-flash-medium",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/research_dossier.md",
        "summary": "Developer community sentiment and edge case extractor across forums.",
    },
    "media-intel-agent": {
        "canonical_name": "media-intel-agent",
        "spec_file": "agents/media-intel-agent.md",
        "default_channel": "research",
        "default_model": "gemini-3.8-flash-medium",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/research_dossier.md",
        "summary": "Multimodal video ingest, transcript extraction, and frame sampler.",
    },
    "design-agent": {
        "canonical_name": "design-agent",
        "spec_file": "agents/design-agent.md",
        "default_channel": "council",
        "default_model": "gemini-3.8-flash-low",
        "default_workspace": "inherit",
        "primary_contract": ".agents/blackboard/design_tokens.md",
        "summary": "Anti-Slop Design Trinity lead; authors 3-tier CSS tokens and typography.",
    },
    "docs-agent": {
        "canonical_name": "docs-agent",
        "spec_file": "agents/docs-agent.md",
        "default_channel": "council",
        "default_model": "gemini-3.8-flash-low",
        "default_workspace": "inherit",
        "primary_contract": "Documentation & ADRs",
        "summary": "Technical documentation and architectural decision record author.",
    },
    "analytics-agent": {
        "canonical_name": "analytics-agent",
        "spec_file": "agents/analytics-agent.md",
        "default_channel": "council",
        "default_model": "gemini-3.8-flash-medium",
        "default_workspace": "inherit",
        "primary_contract": "Event schemas & metrics",
        "summary": "Data pipeline instrumentation and event telemetry engineer.",
    },
    "seo-agent": {
        "canonical_name": "seo-agent",
        "spec_file": "agents/seo-agent.md",
        "default_channel": "council",
        "default_model": "gemini-3.8-flash-low",
        "default_workspace": "inherit",
        "primary_contract": "Semantic HTML & structured data",
        "summary": "Search engine optimization and structured metadata specialist.",
    },
    "image-agent": {
        "canonical_name": "image-agent",
        "spec_file": "agents/image-agent.md",
        "default_channel": "council",
        "default_model": "gemini-3.8-flash-low",
        "default_workspace": "inherit",
        "primary_contract": "Visual assets & SVG specs",
        "summary": "Visual asset prompt engineering and SVG optimization specialist.",
    },
}

# Alias resolution mapping
ALIASES = {
    "pm": "pm-agent",
    "pm-agent": "pm-agent",
    "architect": "architect-agent",
    "arch": "architect-agent",
    "architect-agent": "architect-agent",
    "challenger": "council-challenger",
    "council-challenger": "council-challenger",
    "builder": "builder-agent",
    "builder-agent": "builder-agent",
    "builder-api": "builder-agent",
    "builder-ui": "builder-agent",
    "qa": "qa-adversary-agent",
    "qa-adversary": "qa-adversary-agent",
    "qa-adversary-agent": "qa-adversary-agent",
    "narrator": "narrator",
    "monitor": "monitor",
    "research": "research-agent",
    "research-agent": "research-agent",
    "social": "social-forum-agent",
    "social-forum": "social-forum-agent",
    "social-forum-agent": "social-forum-agent",
    "media": "media-intel-agent",
    "media-intel": "media-intel-agent",
    "media-intel-agent": "media-intel-agent",
    "design": "design-agent",
    "design-agent": "design-agent",
    "docs": "docs-agent",
    "docs-agent": "docs-agent",
    "analytics": "analytics-agent",
    "analytics-agent": "analytics-agent",
    "seo": "seo-agent",
    "seo-agent": "seo-agent",
    "image": "image-agent",
    "image-agent": "image-agent",
}

# Google Gemini Model Tiers
GOOGLE_MODELS = {
    "gemini-3.8-flash-high",
    "gemini-3.8-flash-medium",
    "gemini-3.8-flash-low",
}

MODEL_ALIASES = {
    "high": "gemini-3.8-flash-high",
    "medium": "gemini-3.8-flash-medium",
    "low": "gemini-3.8-flash-low",
    "pro": "gemini-3.8-flash-high",
    "flash": "gemini-3.8-flash-low",
}


def resolve_persona(name: str) -> Optional[Dict[str, Any]]:
    clean = name.strip().lower()
    canonical_key = ALIASES.get(clean)
    if not canonical_key:
        # Fallback check if matches any prefix
        for k in PERSONA_CONFIGS:
            if clean in k:
                canonical_key = k
                break
    if not canonical_key or canonical_key not in PERSONA_CONFIGS:
        return None
    return PERSONA_CONFIGS[canonical_key]


def generate_brief(
    agent_name: str,
    channel: Optional[str] = None,
    slice_target: Optional[str] = None,
    model_tier: Optional[str] = None,
    workspace_mode: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a standardized, persona-primed brief for a native swarm worker."""
    conf = resolve_persona(agent_name)
    if not conf:
        raise ValueError(
            f"Unknown agent name: '{agent_name}'. Available agents: {', '.join(sorted(PERSONA_CONFIGS.keys()))}"
        )

    canonical_name = conf["canonical_name"]
    spec_file = conf["spec_file"]
    effective_channel = channel or conf["default_channel"]
    if model_tier:
        effective_model = MODEL_ALIASES.get(model_tier.lower(), model_tier)
    else:
        effective_model = conf["default_model"]
    effective_workspace = workspace_mode or conf["default_workspace"]
    contract_file = conf["primary_contract"]

    slice_clause = ""
    if slice_target:
        slice_clause = f"Target Slice: {slice_target}. "

    brief_parts: List[str] = []

    if canonical_name == "pm-agent":
        brief_parts.append(
            f"You are pm-agent in Wayne Custom Swarm. Load spec at {spec_file}. Model Tier: {effective_model}. "
            f"Strictly obey blackboard contracts in .agents/blackboard/ (stage pm_spec.md with numbered acceptance criteria [AC-01]..[AC-xx], negative criteria [NAC-xx], edge cases, and finite state tables). "
            f"{slice_clause}Communicate on the shared message board using channel '#{effective_channel}'. "
            f"Always use explicit mentions ('@<agent_name>'), cite relevant sequence numbers ('#<seq>'), and address peer questions. "
            f"When specification staging is complete and consensus is unlocked, report to '@coordinator [done]' with deliverable summary and token telemetry (Model Used, Input Tokens, Output Tokens, Cache Read Tokens, Total Tokens)."
        )
    elif canonical_name == "architect-agent":
        brief_parts.append(
            f"You are architect-agent in Wayne Custom Swarm. Load spec at {spec_file}. Model Tier: {effective_model} (High Thinking). "
            f"Strictly obey blackboard contracts in .agents/blackboard/ (author arch_schema.md against pm_spec.md, specifying machine types, Zod schemas, DB migrations, STRIDE threat mitigations, and mutation lifecycles). "
            f"{slice_clause}Communicate on channel '#{effective_channel}'. Defend the architecture against council-challenger. "
            f"Always use explicit mentions ('@council-challenger'), cite sequence numbers ('#<seq>'), and answer challenge tags ([CHAL-SEC-xx], [CHAL-CONC-xx]). "
            f"When consensus is achieved and arch_schema.md is locked, report to '@coordinator [done]' with token telemetry (Model Used, Input Tokens, Output Tokens, Cache Read Tokens, Total Tokens)."
        )
    elif canonical_name == "council-challenger":
        brief_parts.append(
            f"You are council-challenger in Wayne Custom Swarm. Load spec at {spec_file}. Model Tier: {effective_model} (High Thinking). "
            f"Strictly obey blackboard contracts in .agents/blackboard/ (stress-test arch_schema.md against STRIDE threat models, concurrency races, error states, and unvalidated payloads). "
            f"{slice_clause}Communicate on channel '#{effective_channel}'. "
            f"Always use explicit mentions ('@architect-agent'), cite sequence numbers ('#<seq>'), and post structured challenges ([CHAL-SEC-xx], [CHAL-CONC-xx]). "
            f"Enforce the 2-turn debate limit. When all objections are resolved, report to '@coordinator [done] Consensus achieved on arch_schema.md' with token telemetry (Model Used, Input Tokens, Output Tokens, Cache Read Tokens, Total Tokens)."
        )
    elif canonical_name == "builder-agent":
        brief_parts.append(
            f"You are builder-agent in Wayne Custom Swarm. Load spec at {spec_file}. Model Tier: {effective_model}. "
            f"{slice_clause}Execute implementation strictly within an isolated Git worktree (.worktrees/worker-<id> on branch swarm/worker-<id>). "
            f"Strictly obey blackboard contracts in .agents/blackboard/ (pm_spec.md, design_tokens.md, arch_schema.md). "
            f"Zero design discovery: implement exact tokens and contracts provided. Apply minimal surgical diffs. "
            f"Communicate on channel '#{effective_channel}'. Always use explicit mentions ('@<agent_name>') and cite sequence numbers ('#<seq>'). "
            f"Run local verification commands to ensure zero build errors and passing unit tests. When implementation completes, commit to your branch and report to '@coordinator [done]' with git diff summary and token telemetry (Model Used, Input Tokens, Output Tokens, Cache Read Tokens, Total Tokens)."
        )
    elif canonical_name == "qa-adversary-agent":
        brief_parts.append(
            f"You are qa-adversary-agent in Wayne Custom Swarm. Load spec at {spec_file}. Model Tier: {effective_model} (Cognitive Parity, High Thinking). "
            f"Enforce Zero Self-Auditing. Strictly obey blackboard contracts in .agents/blackboard/ (audit integrated feat/task branch against pm_spec.md using validate_blackboard.py and update code_qa_status.md). "
            f"{slice_clause}Communicate on channel '#{effective_channel}'. Always use explicit mentions ('@<agent_name>') and cite sequence numbers ('#<seq>'). "
            f"If failures exist, post '@builder-<id> [AC-xx FAIL] <reproduction trace and file:line>'. Track iterations (<= 3 loops) and enforce Regression Lock. "
            f"When all criteria PASS, record via scripts/healing_tracker.py, lock code_qa_status.md (ALL_PASS), and report to '@coordinator [done]' with verification matrix and token telemetry (Model Used, Input Tokens, Output Tokens, Cache Read Tokens, Total Tokens)."
        )
    elif canonical_name == "narrator":
        brief_parts.append(
            f"You are narrator in Wayne Custom Swarm. Model Tier: {effective_model}. Maintain live UI overview of swarm progress across the 6-phase lifecycle. "
            "Monitor .agents/blackboard/ and board channels (#council, #builders, #qa). "
            "Update Director UI in real time with active S_task score, passing/failing criteria counts, and healing iteration count (N/3). "
            "Report milestones and phase transitions to '@coordinator' with token telemetry (Model Used, Input Tokens, Output Tokens, Cache Read Tokens, Total Tokens)."
        )
    elif canonical_name == "monitor":
        brief_parts.append(
            f"You are monitor (stall watchdog) in Wayne Custom Swarm. Model Tier: {effective_model}. Continuously track board activity and agent execution states across all channels. "
            "If an agent hangs, stops responding, or deadlocks during Phase 2 (Council debate), Phase 4 (build/test), or Phase 5 (QA healing), "
            "alert '@coordinator [STALL_DETECTED]' citing the stalled agent and last known sequence number (#<seq>)."
        )
    elif canonical_name == "research-agent":
        brief_parts.append(
            f"You are research-agent in Wayne Custom Swarm. Load spec at {spec_file}. Model Tier: {effective_model}. "
            f"Lead the Hybrid Research Cluster on channel '#{effective_channel}'. "
            f"Strictly obey blackboard contracts in .agents/blackboard/ (author research_dossier.md with cross-lingual query matrix [EN/ZH/JA/KO/RU], platform provenance, and numbered findings [RES-01]..[RES-xx]). "
            f"Always use explicit mentions ('@<agent_name>'), cite sequence numbers ('#<seq>'), and report completion to '@coordinator [done]' with token telemetry (Model Used, Input Tokens, Output Tokens, Cache Read Tokens, Total Tokens)."
        )
    elif canonical_name == "design-agent":
        brief_parts.append(
            f"You are design-agent in Wayne Custom Swarm. Load spec at {spec_file}. Model Tier: {effective_model}. "
            f"Strictly obey blackboard contracts in .agents/blackboard/ (author design_tokens.md with 3-tier CSS custom properties [primitive -> semantic -> component], OKLCH scales, and optical typography; zero runtime code). "
            f"Communicate on channel '#{effective_channel}'. Always use explicit mentions ('@<agent_name>'), cite sequence numbers ('#<seq>'), and report completion to '@coordinator [done]' with token telemetry (Model Used, Input Tokens, Output Tokens, Cache Read Tokens, Total Tokens)."
        )
    else:
        brief_parts.append(
            f"You are {canonical_name} in Wayne Custom Swarm. Load spec at {spec_file}. Model Tier: {effective_model}. "
            f"Strictly obey blackboard contracts in .agents/blackboard/ ({contract_file}). "
            f"{slice_clause}Communicate on channel '#{effective_channel}'. Always use explicit mentions ('@<agent_name>'), cite sequence numbers ('#<seq>'), "
            f"and report completion to '@coordinator [done]' with deliverable summary and token telemetry (Model Used, Input Tokens, Output Tokens, Cache Read Tokens, Total Tokens)."
        )

    brief_text = " ".join(brief_parts)

    return {
        "name": agent_name,
        "canonical_name": canonical_name,
        "brief": brief_text,
        "model": effective_model,
        "channels": [effective_channel] if effective_channel != "all" else ["council", "builders", "qa"],
        "workspace": effective_workspace,
        "spec_file": spec_file,
        "primary_contract": contract_file,
    }


def print_channels(output_format: str = "text") -> None:
    """Print the standardized channel topology."""
    if output_format == "json":
        print(json.dumps(CHANNELS, indent=2))
        return

    if output_format == "markdown":
        print("# Wayne Custom Swarm — Standard Channel Topology\n")
        print("| Channel | Lifecycle Phases | Participants | Primary Contracts | Description |")
        print("| :--- | :--- | :--- | :--- | :--- |")
        for ch_key, ch in CHANNELS.items():
            phases_str = "<br>".join(ch["phases"])
            parts_str = ", ".join([f"`{p}`" for p in ch["default_participants"]])
            contracts_str = "<br>".join([f"`{Path(c).name}`" for c in ch["primary_contracts"]])
            print(f"| `#{ch['name']}` | {phases_str} | {parts_str} | {contracts_str} | {ch['description']} |")
        print("\n### Global Oversight Agents")
        print("- `narrator`: Live UI Overview for Director across all channels.")
        print("- `monitor`: Stall watchdog and deadlock breaker across all channels.")
        return

    # Plain text format
    print("================================================================================")
    print("Wayne Custom Swarm — Standard Channel Topology")
    print("================================================================================\n")
    for ch_key, ch in CHANNELS.items():
        print(f"[{ch['name'].upper()}] Channel: #{ch['name']}")
        print(f"  Description : {ch['description']}")
        print(f"  Phases      : {', '.join(ch['phases'])}")
        print(f"  Participants: {', '.join(ch['default_participants'])}")
        print(f"  Contracts   : {', '.join(ch['primary_contracts'])}")
        if "isolation_protocol" in ch:
            print(f"  Isolation   : {ch['isolation_protocol']}")
        print()
    print("Global Oversight Agents (Cross-Channel):")
    print("  - narrator: Live UI Overview for Director.")
    print("  - monitor : Stall watchdog and deadlock breaker.")
    print("================================================================================")


def record_qa_integration(
    bb_dir: Path,
    passed_ids: List[str],
    failed_ids: List[str],
    seq: Optional[int] = None,
    output_json: bool = False,
) -> Dict[str, Any]:
    """Integrate with healing_tracker.py and generate native board announcement recommendations."""
    if healing_tracker is None:
        raise RuntimeError("healing_tracker module could not be imported.")

    state = healing_tracker.record_qa_cycle(bb_dir, passed_ids, failed_ids)

    announcements: List[str] = []
    iteration = state["iteration"]
    max_iter = state["max_iterations"]
    seq_prefix = f"Triggered at #seq {seq}: " if seq is not None else ""

    # Check for regression violations
    if state.get("regression_violations"):
        announcements.append(
            f"@builder [ALERT] Regression Violation: Criterion previously verified as PASS has failed: "
            f"{state['regression_violations']}. Revert offending commits immediately!"
        )

    # Check for architectural escalation (2 consecutive failures on same criterion)
    if state.get("escalated_to_architect"):
        consecutive = state.get("consecutive_failures", {})
        consecutive_keys = [k for k, v in consecutive.items() if v >= 2]
        announcements.append(
            f"@architect-agent [ESCALATION] Criteria failed across 2 consecutive iterations: "
            f"{consecutive_keys}. Pausing builder fixes for arch_schema.md review."
        )

    # Overall state announcement
    if state["status"] == "PASSED_ALL":
        announcements.append(
            f"@coordinator [done] {seq_prefix}ALL ACCEPTANCE CRITERIA PASSED! Verification complete in iteration {iteration}/{max_iter}."
        )
    elif state["status"] == "ESCALATED_MAX_CYCLES_EXCEEDED":
        announcements.append(
            f"@coordinator [HALT] {seq_prefix}Maximum repair iterations ({max_iter}) exceeded with unresolved failures: "
            f"{failed_ids}. Automated fixes halted; clean escalation to human Director."
        )
    elif state["status"] == "REPAIR_REQUIRED":
        escalation_note = ""
        if state.get("model_escalation"):
            esc_str = state["model_escalation"].rstrip(".")
            escalation_note = f" Model Escalation: {esc_str}."
        announcements.append(
            f"@builder [HEALING-CYCLE {iteration}/{max_iter}] {seq_prefix}Target repair criteria: {failed_ids}.{escalation_note} "
            f"Regression lock permanently active for locked criteria: {state['locked_passed']}."
        )

    result = {
        "status": state["status"],
        "iteration": state["iteration"],
        "max_iterations": state["max_iterations"],
        "locked_passed": state["locked_passed"],
        "failed_criteria": failed_ids,
        "regression_violations": state.get("regression_violations", []),
        "escalated_to_architect": state.get("escalated_to_architect", False),
        "model_escalation": state.get("model_escalation"),
        "board_announcements": announcements,
    }

    if output_json:
        print(json.dumps(result, indent=2))
    else:
        print("\n--- Swarm Board Announcement Recommendations ---")
        for ann in announcements:
            print(f"📢 {ann}")
        print("--------------------------------------------------\n")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Hybrid Swarm Orchestration Controller for Wayne Custom Orchestra."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: brief
    brief_parser = subparsers.add_parser("brief", help="Generate standardized brief for swarm{action: 'add'}")
    brief_parser.add_argument("agent", help="Agent name or alias (e.g. pm-agent, architect, builder, qa)")
    brief_parser.add_argument("--channel", type=str, default=None, help="Target topic channel (council, builders, qa, etc.)")
    brief_parser.add_argument("--slice", type=str, default=None, help="Assigned slice target (e.g. '[AC-01]..[AC-05]')")
    brief_parser.add_argument(
        "--model",
        type=str,
        default=None,
        choices=["gemini-3.8-flash-high", "gemini-3.8-flash-medium", "gemini-3.8-flash-low"],
        help="Cognitive model tier override (gemini-3.8-flash-high, gemini-3.8-flash-medium, gemini-3.8-flash-low)",
    )
    brief_parser.add_argument("--workspace", type=str, default=None, choices=["inherit", "share", "clone"], help="Workspace mode override")
    brief_parser.add_argument("--json", action="store_true", help="Output as JSON matching swarm{action: 'add'} parameters")

    # Subcommand: channels
    channels_parser = subparsers.add_parser("channels", help="Print standard topic channel topology")
    channels_parser.add_argument(
        "--format", type=str, default="text", choices=["text", "json", "markdown"], help="Output format"
    )

    # Subcommand: record-qa
    qa_parser = subparsers.add_parser("record-qa", help="Record QA verification cycle and generate board announcements")
    qa_parser.add_argument("--passed", nargs="*", default=[], help="List of passing criterion IDs (e.g. AC-01 AC-02)")
    qa_parser.add_argument("--failed", nargs="*", default=[], help="List of failing criterion IDs (e.g. AC-03)")
    qa_parser.add_argument("--dir", type=str, default=".agents/blackboard", help="Blackboard directory path")
    qa_parser.add_argument("--seq", type=int, default=None, help="Native swarm board sequence number triggering record")
    qa_parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    if args.command == "brief":
        res = generate_brief(
            agent_name=args.agent,
            channel=args.channel,
            slice_target=args.slice,
            model_tier=args.model,
            workspace_mode=args.workspace,
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(res["brief"])

    elif args.command == "channels":
        print_channels(args.format)

    elif args.command == "record-qa":
        bb_path = Path(args.dir).resolve()
        record_qa_integration(
            bb_dir=bb_path,
            passed_ids=args.passed,
            failed_ids=args.failed,
            seq=args.seq,
            output_json=args.json,
        )


if __name__ == "__main__":
    main()
