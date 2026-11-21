#!/usr/bin/env python3
"""
Programmatic Blackboard Contract Validator.

Validates:
1. Syntax and uniqueness of Acceptance Criteria [AC-xx] and Negative Criteria [NAC-xx] in pm_spec.md.
2. 1:1 Parity between pm_spec.md and code_qa_status.md.
3. Structural integrity of arch_schema.md (Data Models & Council Consensus Resolution).
4. Token block structure in design_tokens.md.
"""

import sys
import os
import re
import argparse
from pathlib import Path

def validate_blackboard(bb_dir: Path):
    print(f"=== Validating Blackboard Contracts in: {bb_dir} ===\n")
    if not bb_dir.exists():
        print(f"❌ Blackboard directory does not exist: {bb_dir}")
        return False

    errors = []
    warnings = []

    pm_spec_path = bb_dir / "pm_spec.md"
    arch_path = bb_dir / "arch_schema.md"
    design_path = bb_dir / "design_tokens.md"
    qa_path = bb_dir / "code_qa_status.md"

    # 1. Validate pm_spec.md
    ac_ids = []
    if not pm_spec_path.exists():
        warnings.append(f"pm_spec.md missing from {bb_dir}")
    else:
        pm_content = pm_spec_path.read_text(encoding="utf-8")
        # Extract [AC-xx] and [NAC-xx]
        found_acs = re.findall(r"\[(AC-\d+|NAC-\d+)\]", pm_content)
        if not found_acs:
            errors.append("pm_spec.md: No numbered acceptance criteria ([AC-xx] or [NAC-xx]) detected.")
        else:
            seen = set()
            for acid in found_acs:
                if acid in seen:
                    errors.append(f"pm_spec.md: Duplicate criterion ID detected: '[{acid}]'")
                seen.add(acid)
                ac_ids.append(acid)

    # 2. Validate arch_schema.md
    if not arch_path.exists():
        warnings.append(f"arch_schema.md missing from {bb_dir}")
    else:
        arch_content = arch_path.read_text(encoding="utf-8")
        if not re.search(r"##\s*.*(?:Schema|Data Model|API.*Contract)", arch_content, re.IGNORECASE):
            warnings.append("arch_schema.md: Missing standard Schema/Data Models or API Contracts section.")
        if not re.search(r"##\s*.*(?:LLM Council|Consensus Resolution)", arch_content, re.IGNORECASE):
            warnings.append("arch_schema.md: Missing 'LLM Council Consensus Resolution' section for Phase 2 gate.")

    # 3. Validate design_tokens.md
    if not design_path.exists():
        warnings.append(f"design_tokens.md missing from {bb_dir}")
    else:
        design_content = design_path.read_text(encoding="utf-8")
        if "--" not in design_content and ":root" not in design_content:
            warnings.append("design_tokens.md: No CSS custom properties (variables) detected.")

    # 4. Validate code_qa_status.md and check parity with pm_spec.md
    if not qa_path.exists():
        warnings.append(f"code_qa_status.md not yet created in {bb_dir} (expected during QA phase)")
    else:
        qa_content = qa_path.read_text(encoding="utf-8")
        qa_acs = set(re.findall(r"\[(AC-\d+|NAC-\d+)\]", qa_content))
        
        # Check if all pm_spec criteria are represented in QA status
        if ac_ids:
            missing_in_qa = set(ac_ids) - qa_acs
            if missing_in_qa:
                errors.append(f"code_qa_status.md: Missing verification entries for: {sorted(list(missing_in_qa))}")
            
            phantom_in_qa = qa_acs - set(ac_ids)
            if phantom_in_qa:
                warnings.append(f"code_qa_status.md: Contains criteria IDs not defined in pm_spec.md: {sorted(list(phantom_in_qa))}")

    # Output results
    for w in warnings:
        print(f"  ⚠️  {w}")

    if errors:
        for e in errors:
            print(f"  ❌ {e}")
        print("\nResult: Blackboard validation FAILED.")
        return False
    else:
        print("\nResult: Blackboard validation PASSED.")
        return True

def main():
    parser = argparse.ArgumentParser(description="Validate blackboard contract files.")
    parser.add_argument("blackboard_dir", nargs="?", default=".agents/blackboard", 
                        help="Path to .agents/blackboard directory (default: .agents/blackboard)")
    args = parser.parse_args()
    
    target_dir = Path(args.blackboard_dir).resolve()
    success = validate_blackboard(target_dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
