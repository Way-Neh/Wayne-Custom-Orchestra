# Orchestrator & Sub-Agents Workflow Directives

## 🎯 Active Orchestrator Mode: Wayne Custom 2.0 (Primary Default)

This workspace is configured with **Wayne Custom 2.0** as its active orchestrator mode.

```
Global Default: "Wayne Custom 2.0"
Project Setting: .agents/orchestrator_mode.json -> "activeMode": "Wayne Custom 2.0"
```

---

## 🔄 How to Switch Orchestrator Mode in this Project

You can change the active mode at any time by editing [`.agents/orchestrator_mode.json`](file:///Users/ap-wayne.tan/DockerProjects/Orchestrator/.agents/orchestrator_mode.json):

```json
{
  "activeMode": "Wayne Custom 2.0"
}
```

### Supported Modes:
1. **`Wayne Custom 2.0`** *(Default)*:
   - **Adaptive Task Sizing Protocol**: $S_{\text{task}} = D + F + A + C + V$.
   - **Tier 1 ($S_{\text{task}} \le 5$)**: Direct Solo. Mandatory bypass of Grill-Me & approval gates.
   - **Tier 2 ($S_{\text{task}} = 6 - 8$)**: Targeted Specialist. Conditional 1-question micro-grill.
   - **Tier 3 ($S_{\text{task}} \ge 9$)**: Full Multi-Agent Swarm with Zero Direct Labor, Grill-Me Protocol, Spec Staging, and Criteria-Mapped Adversarial QA.
   - **Scheduled Tasks (Cron/Timers)**: Automatically bypasses approval gate and proceeds straight to execution.
2. **`Direct Solo`**:
   - Single-agent direct execution without subagent overhead.
3. **`TDD Pair`**:
   - Strict red-green-refactor pairing workflow with test verification gates.
4. **Custom Modes**:
   - You can add or define new custom modes under `"modes"` in `.agents/orchestrator_mode.json`.

---

## 🚀 Execution Lifecycle & Core Pillars ("Wayne Custom 2.0")

### 1. Task Sizing & Gating
- Compute 5-factor complexity score: $S_{\text{task}} = D + F + A + C + V$.
- For Tier 1: Auto-bypass grill & execute directly.
- For Tier 2: Conditional 1-question micro-grill if architectural fork exists.
- For Tier 3:
  - Interactive: Grilling Protocol ➔ Spec Staging (`pm_spec.md`) ➔ Director Gate (`"Proceed"`).
  - Scheduled (Cron/Timer): Auto-bypasses gate and proceeds straight to work.

### 2. Core Pillars Roster (Always Active in Tier 3 Swarms)
- **The Orchestrator**: Zero direct labor. Triage, sizing calculation, dispatching (`invoke_subagent`), synthesis.
- **`pm-agent`**: PRD, numbered acceptance criteria (`[AC-xx]`), user personas (`pm_spec.md`).
- **`design-agent`**: Visual tokens, layout hierarchy, CSS variables (`design_tokens.md`).
- **`architect-agent`**: API contracts, DB schemas, state trees (`arch_schema.md`).
- **`builder-agent`**: Feature construction and logic wiring.
- **`qa-adversary-agent`**: Independent auditor validating line-by-line against `[AC-xx]` (`code_qa_status.md`).

### 3. Dynamic Domain Plugins (On-Demand)
- **`seo-agent`**: Metadata, OpenGraph, JSON-LD schemas.
- **`analytics-agent`**: Telemetry tracking, funnels, cohort indicators.
- **`image-agent`**: Web asset discovery and custom AI image generation.
- **`docs-agent`**: Developer documentation and changelogs.
