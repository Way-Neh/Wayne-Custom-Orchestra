---
name: sample-offline-skill
description: "Template for creating offline skills in the Wayne Custom Cold Catalog. Use when implementing specialized domain workflows."
risk: safe
source: local-catalog
date_added: "2026-10-16"
---

# Sample Offline Skill Specification

## 🎯 Overview
Provide a concise overview of the domain capability, when to use this skill, and what problems it solves. Keep instructions actionable, specific, and token-dense.

## 🗂️ When to Use
- Trigger 1: Specific user request or file format
- Trigger 2: Domain-specific operation (e.g. data transformation, format compilation)
- Boundary: When NOT to use this skill (e.g., delegate to standard tools)

## 🚀 Recommended Workflow
1. **Prerequisites & Environment**: Check necessary CLI tools, libraries, or dependencies.
2. **Execution Steps**: Concrete commands and code patterns.
3. **Verification**: How the executing agent verifies the output before handing off.

## 💻 Code Patterns & Examples

```python
# Minimal example demonstrating core workflow
def process_domain_task(input_path: str, output_path: str):
    """Executes the specialized task with robust error handling."""
    pass
```

## ⚠️ Common Pitfalls & Constraints
- Highlight gotchas, memory limitations, or platform-specific quirks.
- Emphasize error recovery techniques.
