#!/usr/bin/env python3
"""
Bounded Cyclic Self-Healing State Tracker.

Enforces:
1. Hard bound of maximum 3 repair iterations.
2. Regression Lock Rule (once an AC passes, it cannot fail in later iterations).
3. Architectural Escalation Gate (triggers architect-agent if same AC fails 2 consecutive times).
"""

import sys
import os
import json
import argparse
from pathlib import Path

DEFAULT_STATE_FILE = "healing_state.json"

def get_state_path(bb_dir: Path) -> Path:
    return bb_dir / DEFAULT_STATE_FILE

def init_state(bb_dir: Path):
    bb_dir.mkdir(parents=True, exist_ok=True)
    state_file = get_state_path(bb_dir)
    state = {
        "iteration": 1,
        "max_iterations": 3,
        "status": "INITIALIZED",
        "locked_passed": [],
        "consecutive_failures": {},
        "regression_violations": [],
        "escalated_to_architect": False,
        "history": []
    }
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(f"✔ Initialized healing state machine at: {state_file}")
    return state

def load_state(bb_dir: Path):
    state_file = get_state_path(bb_dir)
    if not state_file.exists():
        return init_state(bb_dir)
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"⚠️ Failed to parse {state_file}: {e}, reinitializing...")
        return init_state(bb_dir)

def save_state(bb_dir: Path, state):
    state_file = get_state_path(bb_dir)
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

def record_qa_cycle(bb_dir: Path, passed_ids, failed_ids):
    state = load_state(bb_dir)
    iteration = state["iteration"]
    
    print(f"\n--- Recording QA Verification Cycle (Iteration {iteration}/{state['max_iterations']}) ---")
    
    # 1. Check Regression Lock Rule
    locked = set(state["locked_passed"])
    current_failed = set(failed_ids)
    
    regressions = list(locked.intersection(current_failed))
    if regressions:
        print(f"🚨 REGRESSION VIOLATION: Criteria previously passing have now failed: {regressions}")
        for reg in regressions:
            if reg not in state["regression_violations"]:
                state["regression_violations"].append(reg)

    # 2. Lock newly passed criteria
    current_passed = set(passed_ids)
    for p in current_passed:
        if p not in state["locked_passed"]:
            state["locked_passed"].append(p)

    # 3. Track consecutive failures
    consecutive = state.get("consecutive_failures", {})
    for f in current_failed:
        consecutive[f] = consecutive.get(f, 0) + 1
    # Reset counts for criteria that now passed
    for p in current_passed:
        if p in consecutive:
            del consecutive[p]
    state["consecutive_failures"] = consecutive

    # 4. Check Architectural Escalation Gate (2 consecutive failures on same criterion)
    escalate = [acid for acid, count in consecutive.items() if count >= 2]
    if escalate and not state["escalated_to_architect"]:
        state["escalated_to_architect"] = True
        print(f"🛑 ARCHITECTURAL ESCALATION GATE TRIGGERED: Criteria failed across 2 consecutive iterations: {escalate}")
        print("   Action Required: Dispatch architect-agent to review arch_schema.md before next builder fix.")

    # 5. Record History
    state["history"].append({
        "iteration": iteration,
        "passed": list(current_passed),
        "failed": list(current_failed),
        "regressions": regressions
    })

    # 6. Status Determination
    if not current_failed:
        state["status"] = "PASSED_ALL"
        print("🎉 ALL ACCEPTANCE CRITERIA PASSED! Healing cycle complete.")
    elif iteration >= state["max_iterations"]:
        state["status"] = "ESCALATED_MAX_CYCLES_EXCEEDED"
        print(f"❌ MAXIMUM ITERATIONS ({state['max_iterations']}) EXCEEDED with unresolved failures: {list(current_failed)}")
        print("   Action Required: Halting automatic fixes; escalate to human Director with diagnostics.")
    else:
        state["iteration"] += 1
        state["status"] = "REPAIR_REQUIRED"
        print(f"🔄 Repair cycle scheduled. Next iteration: {state['iteration']}/{state['max_iterations']}")

    save_state(bb_dir, state)
    return state

def show_status(bb_dir: Path):
    state = load_state(bb_dir)
    print(f"\n=== Healing State: {bb_dir} ===")
    print(f"Iteration: {state['iteration']} / {state['max_iterations']}")
    print(f"Status: {state['status']}")
    print(f"Locked Passed Criteria ({len(state['locked_passed'])}): {state['locked_passed']}")
    print(f"Consecutive Failures: {state.get('consecutive_failures', {})}")
    print(f"Regression Violations: {state.get('regression_violations', [])}")
    print(f"Escalated to Architect: {state.get('escalated_to_architect', False)}")
    print("=" * 40 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Cyclic self-healing bounded state tracker.")
    parser.add_argument("--dir", default=".agents/blackboard", help="Path to blackboard directory")
    subparsers = parser.add_subparsers(dest="command")

    init_p = subparsers.add_parser("init", help="Initialize healing state")
    status_p = subparsers.add_parser("status", help="Show current healing state")
    
    qa_p = subparsers.add_parser("record", help="Record QA cycle results")
    qa_p.add_argument("--passed", nargs="*", default=[], help="List of passing criterion IDs (e.g. AC-01 AC-02)")
    qa_p.add_argument("--failed", nargs="*", default=[], help="List of failing criterion IDs (e.g. AC-03)")

    args = parser.parse_args()
    bb_dir = Path(args.dir).resolve()

    if args.command == "init":
        init_state(bb_dir)
    elif args.command == "status":
        show_status(bb_dir)
    elif args.command == "record":
        record_qa_cycle(bb_dir, args.passed, args.failed)
    else:
        show_status(bb_dir)

if __name__ == "__main__":
    main()
