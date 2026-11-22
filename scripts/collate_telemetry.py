#!/usr/bin/env python3
"""
collate_telemetry.py - Token & Model Telemetry Collator for Wayne Custom Orchestrator.

Parses transcript.jsonl files across the Root Orchestrator and all invoked Subagents
as well as Native Swarm workers (located in <appDataDir>/brain/<conv_id>/.system_generated/logs/transcript.jsonl),
extracting model details, input tokens, output tokens, cache read tokens, and total tokens,
and outputs a formatted Markdown telemetry table with a run sum total row.

Features:
  - Multi-source auto-discovery:
      * Filesystem discovery of subagents (.system_generated/subagents/*.json)
      * Filesystem discovery of swarm workers (.system_generated/swarm/members.json)
      * Step-level tool call extraction (invoke_subagent and swarm{action: 'add'})
  - Unattended spending ceiling guard (e.g. 50,000 token limit) for Rule 8 compliance.
  - JSON and Markdown output formats.

Usage:
  python3 scripts/collate_telemetry.py [OPTIONS] [CONVERSATION_IDS_OR_PATHS...]
  python3 scripts/collate_telemetry.py --root <ROOT_CONVERSATION_ID>
  python3 scripts/collate_telemetry.py --root <ROOT_ID> --ceiling 50000 --enforce-ceiling
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set

DEFAULT_MODEL_MAP = {
    "inherit": "Gemini 3.8 Pro (High)",
    "flash": "Gemini 3.8 Flash (High)",
    "pro": "Gemini 3.8 Pro (High)",
    "flash_lite": "Gemini 3.8 Flash-Lite",
    "gemini-3.8-flash-high": "Gemini 3.8 Flash (High)",
    "gemini-3.8-pro-high": "Gemini 3.8 Pro (High)",
    "gemini-3.8-flash-lite": "Gemini 3.8 Flash-Lite",
}
DEFAULT_ROOT_MODEL = "Gemini 3.8 Flash (High)"
DEFAULT_FALLBACK_MODEL = "Gemini 3.8 Flash (High)"


def normalize_model_name(name: Optional[str], default: str = DEFAULT_FALLBACK_MODEL) -> str:
    if not name or name == "None":
        return default
    clean = name.strip()
    low = clean.lower()
    if low in DEFAULT_MODEL_MAP:
        return DEFAULT_MODEL_MAP[low]
    if "flash" in low:
        if "lite" in low:
            return "Gemini 3.8 Flash-Lite"
        return "Gemini 3.8 Flash (High)"
    if "pro" in low:
        return "Gemini 3.8 Pro (High)"
    if low == "inherit":
        return default
    return clean


def find_app_data_dir(custom_path: Optional[str] = None) -> Path:
    if custom_path:
        return Path(custom_path).expanduser().resolve()
    env_dir = os.environ.get("ANTIGRAVITY_APP_DATA_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return (Path.home() / ".gemini" / "antigravity").resolve()


def resolve_transcript_path(id_or_path: str, app_data_dir: Path) -> Optional[Path]:
    p = Path(id_or_path).expanduser().resolve()
    if p.is_file():
        return p

    # Try looking in app_data_dir/brain/<id>/.system_generated/logs/transcript.jsonl
    candidate = app_data_dir / "brain" / id_or_path / ".system_generated" / "logs" / "transcript.jsonl"
    if candidate.is_file():
        return candidate

    candidate_alt = app_data_dir / "brain" / id_or_path / "transcript.jsonl"
    if candidate_alt.is_file():
        return candidate_alt

    return None


def extract_model_from_text(text: str) -> Optional[str]:
    """Search for Model Used: <name> in text."""
    patterns = [
        r"(?:\*\*|\b)Model\s*(?:Used)?\s*(?:\*\*)?\s*[:=\-]\s*(?:\*\*)?\s*[`\*]*((?:Gemini|Claude|GPT|o1|o3|DeepSeek|Llama)[A-Za-z0-9\.\-\_\s\(\)]+?)[`\*]*(?:\n|$|\r)",
        r"(?:\*\*|\b)Model\s*[:=\-]\s*(?:\*\*)?\s*[`\*]*((?:Gemini|Claude|GPT|o1|o3|DeepSeek|Llama)[A-Za-z0-9\.\-\_\s\(\)]+?)[`\*]*(?:\n|$|\r)",
        r"Model\s*Used\s*[:=\-]\s*[`\*]*([A-Za-z0-9\.\-\_\s\(\)]+?)[`\*]*(?:\n|$|\r)",
        r"Model\s*[:=\-]\s*[`\*]*([A-Za-z0-9\.\-\_\s\(\)]+?)[`\*]*(?:\n|$|\r)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if len(val) > 2 and not val.lower().startswith("used"):
                return val
    return None


def parse_transcript(
    transcript_path: Path,
    since_step: Optional[int] = None,
) -> Dict[str, Any]:
    """Parse transcript.jsonl and aggregate token counts, subagents, and swarm worker invocations."""
    input_tokens = 0
    output_tokens = 0
    cache_read_tokens = 0
    reported_model = None
    user_steps: List[int] = []
    invocations: List[Dict[str, Any]] = []

    if not transcript_path.is_file():
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "total_tokens": 0,
            "reported_model": None,
            "user_steps": [],
            "invocations": [],
        }

    with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    conv_id_regex = re.compile(r'"conversation_?id":\s*"([0-9a-fA-F\-]{36})"', re.IGNORECASE)

    for idx, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            step = json.loads(line)
        except Exception:
            continue

        step_idx = step.get("step_index", 0)
        source = step.get("source", "")
        step_type = step.get("type", "")

        if source == "USER_EXPLICIT" or step_type == "USER_INPUT":
            user_steps.append(step_idx)

        content = step.get("content") or ""
        if content and not reported_model:
            found = extract_model_from_text(content)
            if found:
                reported_model = found

        tool_calls = step.get("tool_calls") or []
        for tc in tool_calls:
            tc_name = tc.get("name", "")
            args = tc.get("args") or {}
            if tc_name == "invoke_subagent":
                type_name = args.get("TypeName") or "subagent"
                role = args.get("Role") or type_name
                sub_model = args.get("Model") or "inherit"

                sub_id = None
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1]
                    cid_match = conv_id_regex.search(next_line)
                    if cid_match:
                        sub_id = cid_match.group(1)

                invocations.append({
                    "TypeName": type_name,
                    "Role": role,
                    "Model": sub_model,
                    "conversationId": sub_id,
                    "type": "subagent",
                })
            elif tc_name == "swarm":
                action = args.get("action")
                if action == "add":
                    name = args.get("name") or "worker"
                    model = args.get("model") or "inherit"
                    sub_id = None
                    if idx + 1 < len(lines):
                        next_line = lines[idx + 1]
                        cid_match = conv_id_regex.search(next_line)
                        if cid_match:
                            sub_id = cid_match.group(1)

                    invocations.append({
                        "TypeName": name,
                        "Role": f"Swarm Worker: `{name}`",
                        "Model": model,
                        "conversationId": sub_id,
                        "type": "swarm_worker",
                    })
            elif tc_name == "send_message":
                msg = args.get("Message", "")
                if msg and not reported_model:
                    found = extract_model_from_text(msg)
                    if found:
                        reported_model = found

        if since_step is not None and step_idx < since_step:
            continue

        input_tokens += step.get("input_tokens") or 0
        output_tokens += step.get("output_tokens") or 0
        cache_read_tokens += step.get("cache_read_tokens") or 0

    total_tokens = input_tokens + output_tokens + cache_read_tokens
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_tokens": cache_read_tokens,
        "total_tokens": total_tokens,
        "reported_model": reported_model,
        "user_steps": user_steps,
        "invocations": invocations,
    }


def discover_subagents(root_conv_id: str, app_data_dir: Path) -> List[Dict[str, Any]]:
    """Scan brain/<root_id>/.system_generated/subagents/*.json for all spawned subagents."""
    discovered = []
    subagents_dir = app_data_dir / "brain" / root_conv_id / ".system_generated" / "subagents"
    if not subagents_dir.is_dir():
        return discovered

    for f in sorted(subagents_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            cid = data.get("conversationId") or f.stem
            descriptor = data.get("subagentDescriptor") or {}
            type_name = descriptor.get("typeName") or "subagent"
            role = descriptor.get("role") or type_name
            state = data.get("state")
            discovered.append({
                "conversationId": cid,
                "role": f"Subagent: `{role}`" if role != "subagent" else f"Subagent: `{type_name}`",
                "typeName": type_name,
                "type": "subagent",
                "state": state,
                "model": descriptor.get("model"),
            })
        except Exception:
            continue
    return discovered


def discover_swarm_workers(root_conv_id: str, app_data_dir: Path) -> List[Dict[str, Any]]:
    """Scan brain/<root_id>/.system_generated/swarm/members.json for all swarm workers."""
    discovered = []
    swarm_dir = app_data_dir / "brain" / root_conv_id / ".system_generated" / "swarm"
    members_file = swarm_dir / "members.json"
    if not members_file.is_file():
        return discovered

    try:
        data = json.loads(members_file.read_text(encoding="utf-8"))
        members = data.get("members") or {}
        for name, m_info in members.items():
            cid = m_info.get("conversation_id")
            role_type = m_info.get("role")
            if not cid or cid == root_conv_id or role_type == "coordinator":
                continue
            model = m_info.get("applied_model") or m_info.get("desired_model") or m_info.get("model")
            discovered.append({
                "conversationId": cid,
                "role": f"Swarm Worker: `{name}`",
                "typeName": name,
                "type": "swarm_worker",
                "model": model,
                "killed": m_info.get("killed", False),
            })
    except Exception:
        pass
    return discovered


def collate_telemetry(
    root_conv_id: Optional[str] = None,
    subagent_ids: Optional[List[str]] = None,
    transcript_paths: Optional[List[str]] = None,
    turn_mode: str = "latest",
    root_model: Optional[str] = None,
    app_data_dir: Optional[str] = None,
    spending_ceiling: Optional[int] = None,
) -> Dict[str, Any]:
    """Collate telemetry data across root orchestrator, subagents, and swarm workers."""
    app_data = find_app_data_dir(app_data_dir)
    rows: List[Dict[str, Any]] = []

    sum_input = 0
    sum_output = 0
    sum_cache = 0
    sum_total = 0

    role_map: Dict[str, str] = {}
    model_map: Dict[str, str] = {}
    discovered_workers: List[Dict[str, Any]] = []
    discovered_ids: Set[str] = set()

    # 1. Process Root Orchestrator if provided
    if root_conv_id:
        root_path = resolve_transcript_path(root_conv_id, app_data)
        if root_path and root_path.is_file():
            initial_parse = parse_transcript(root_path, since_step=None)
            since_step = None
            if turn_mode == "latest" and initial_parse["user_steps"]:
                since_step = initial_parse["user_steps"][-1]

            root_stats = parse_transcript(root_path, since_step=since_step)
            model_used = normalize_model_name(
                root_model or root_stats.get("reported_model"),
                default=DEFAULT_ROOT_MODEL,
            )

            rows.append({
                "agent_level": "Root Orchestrator",
                "conversation_id": root_conv_id,
                "model_used": model_used,
                "input_tokens": root_stats["input_tokens"],
                "output_tokens": root_stats["output_tokens"],
                "cache_read_tokens": root_stats["cache_read_tokens"],
                "total_tokens": root_stats["total_tokens"],
            })
            sum_input += root_stats["input_tokens"]
            sum_output += root_stats["output_tokens"]
            sum_cache += root_stats["cache_read_tokens"]
            sum_total += root_stats["total_tokens"]

            # Multi-source discovery for subagents and swarm workers:
            # Source A: Check filesystem .system_generated/subagents/*.json
            for sub in discover_subagents(root_conv_id, app_data):
                cid = sub["conversationId"]
                if cid not in discovered_ids and cid != root_conv_id:
                    discovered_ids.add(cid)
                    discovered_workers.append(sub)
                    role_map[cid] = sub["role"]
                    if sub.get("model"):
                        model_map[cid] = sub["model"]

            # Source B: Check filesystem .system_generated/swarm/members.json
            for swm in discover_swarm_workers(root_conv_id, app_data):
                cid = swm["conversationId"]
                if cid not in discovered_ids and cid != root_conv_id:
                    discovered_ids.add(cid)
                    discovered_workers.append(swm)
                    role_map[cid] = swm["role"]
                    if swm.get("model"):
                        model_map[cid] = swm["model"]

            # Source C: Check tool call invocations in root transcript
            for inv in initial_parse.get("invocations", []):
                cid = inv.get("conversationId")
                if cid and cid not in discovered_ids and cid != root_conv_id:
                    discovered_ids.add(cid)
                    discovered_workers.append(inv)
                    role_map[cid] = inv.get("Role") or inv.get("TypeName")
                    if inv.get("Model"):
                        model_map[cid] = inv.get("Model")

    # If subagent_ids passed explicitly on CLI, include any that were not discovered
    if subagent_ids:
        for sid in subagent_ids:
            if sid not in discovered_ids and sid != root_conv_id:
                discovered_ids.add(sid)
                discovered_workers.append({
                    "conversationId": sid,
                    "role": role_map.get(sid) or f"Subagent `{sid[:8]}`",
                    "type": "subagent",
                })

    # 2. Process all discovered subagents and swarm workers
    for worker in discovered_workers:
        sub_id = worker["conversationId"]
        sub_path = resolve_transcript_path(sub_id, app_data)
        if not sub_path or not sub_path.is_file():
            continue
        sub_stats = parse_transcript(sub_path, since_step=None)

        assigned_role = role_map.get(sub_id) or worker.get("Role") or f"Subagent: `{sub_id[:8]}`"
        model_hint = sub_stats.get("reported_model") or model_map.get(sub_id) or worker.get("Model")
        model_used = normalize_model_name(model_hint, default=DEFAULT_FALLBACK_MODEL)

        rows.append({
            "agent_level": assigned_role,
            "conversation_id": sub_id,
            "model_used": model_used,
            "input_tokens": sub_stats["input_tokens"],
            "output_tokens": sub_stats["output_tokens"],
            "cache_read_tokens": sub_stats["cache_read_tokens"],
            "total_tokens": sub_stats["total_tokens"],
        })
        sum_input += sub_stats["input_tokens"]
        sum_output += sub_stats["output_tokens"]
        sum_cache += sub_stats["cache_read_tokens"]
        sum_total += sub_stats["total_tokens"]

    # 3. Process direct transcript paths if given
    if transcript_paths:
        for idx, t_path_str in enumerate(transcript_paths):
            t_path = Path(t_path_str).expanduser().resolve()
            if not t_path.is_file():
                continue
            stats = parse_transcript(t_path, since_step=None)
            model_used = normalize_model_name(stats.get("reported_model"), default=DEFAULT_FALLBACK_MODEL)
            rows.append({
                "agent_level": f"Transcript {idx + 1} ({t_path.name})",
                "conversation_id": t_path.parent.parent.name if ".system_generated" in str(t_path) else t_path.stem,
                "model_used": model_used,
                "input_tokens": stats["input_tokens"],
                "output_tokens": stats["output_tokens"],
                "cache_read_tokens": stats["cache_read_tokens"],
                "total_tokens": stats["total_tokens"],
            })
            sum_input += stats["input_tokens"]
            sum_output += stats["output_tokens"]
            sum_cache += stats["cache_read_tokens"]
            sum_total += stats["total_tokens"]

    # Check spending ceiling (Rule 8: 50,000 token limit on unattended crons)
    ceiling_breached = False
    ceiling_msg = None
    if spending_ceiling is not None:
        ceiling_breached = sum_total > spending_ceiling
        if ceiling_breached:
            ceiling_msg = (
                f"TOKEN SPENDING CEILING BREACHED: {sum_total:,} tokens consumed "
                f"exceeds ceiling limit of {spending_ceiling:,} tokens!"
            )

    return {
        "rows": rows,
        "totals": {
            "input_tokens": sum_input,
            "output_tokens": sum_output,
            "cache_read_tokens": sum_cache,
            "total_tokens": sum_total,
        },
        "spending_ceiling": spending_ceiling,
        "ceiling_breached": ceiling_breached,
        "ceiling_message": ceiling_msg,
    }


def format_markdown_table(data: Dict[str, Any]) -> str:
    lines = [
        "| Agent / Level | Model Used | Input Tokens | Output Tokens | Cache Read Tokens | Total Tokens |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in data["rows"]:
        lines.append(
            f"| {r['agent_level']} | {r['model_used']} | "
            f"{r['input_tokens']:,} | {r['output_tokens']:,} | "
            f"{r['cache_read_tokens']:,} | {r['total_tokens']:,} |"
        )
    tot = data["totals"]
    lines.append(
        f"| **Total (Run Sum)** | **-** | "
        f"**{tot['input_tokens']:,}** | **{tot['output_tokens']:,}** | "
        f"**{tot['cache_read_tokens']:,}** | **{tot['total_tokens']:,}** |"
    )

    if data.get("ceiling_breached"):
        lines.append("")
        lines.append("> [!CAUTION]")
        lines.append(f"> **TOKEN SPENDING CEILING BREACHED**: Total tokens ({tot['total_tokens']:,}) "
                     f"exceeded limit of {data['spending_ceiling']:,} tokens!")
        lines.append("> Swarm operations must halt immediately for Director review.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Collate Token & Model Execution Telemetry for Wayne Custom Orchestrator."
    )
    parser.add_argument("targets", nargs="*", help="Conversation IDs or transcript.jsonl paths to parse.")
    parser.add_argument("--root", type=str, default=None, help="Root conversation ID.")
    parser.add_argument("--subagents", nargs="+", default=None, help="Explicit subagent conversation IDs.")
    parser.add_argument("--turn", type=str, default="latest", choices=["latest", "all"], help="Turn scope for root: latest or all.")
    parser.add_argument("--model", type=str, default=None, help="Override model name.")
    parser.add_argument("--app-data-dir", type=str, default=None, help="Path to Antigravity app data directory.")
    parser.add_argument("--format", type=str, default="markdown", choices=["markdown", "json"], help="Output format.")
    parser.add_argument("--ceiling", type=int, default=None, help="Spending ceiling in total tokens (e.g. 50000).")
    parser.add_argument("--enforce-ceiling", action="store_true", help="Exit with non-zero status if ceiling is breached.")

    args = parser.parse_args()

    root_id = args.root
    subagents = list(args.subagents) if args.subagents else []
    direct_transcripts = []

    if args.targets:
        for t in args.targets:
            if os.path.isfile(t):
                direct_transcripts.append(t)
            elif not root_id:
                root_id = t
            else:
                subagents.append(t)

    if not root_id and not direct_transcripts:
        env_conv = os.environ.get("ANTIGRAVITY_CONVERSATION_ID")
        root_id = env_conv

    if not root_id and not direct_transcripts:
        print("Error: No conversation ID or transcript file specified.", file=sys.stderr)
        sys.exit(1)

    result = collate_telemetry(
        root_conv_id=root_id,
        subagent_ids=subagents if subagents else None,
        transcript_paths=direct_transcripts if direct_transcripts else None,
        turn_mode=args.turn,
        root_model=args.model,
        app_data_dir=args.app_data_dir,
        spending_ceiling=args.ceiling,
    )

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_markdown_table(result))

    if args.enforce_ceiling and result.get("ceiling_breached"):
        print(f"\nError: {result.get('ceiling_message')}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
