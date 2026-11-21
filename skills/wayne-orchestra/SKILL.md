---
name: wayne-orchestra
description: Wayne Custom 2.0 (Swarms Enhanced) Adaptive Multi-Agent Swarm Orchestrator architecture, operating model, dynamic task sizing (S_task), blackboard contracts, Swarm topologies, and bounded cyclic self-healing QA.
---

# Wayne Custom Orchestra (Wayne Custom 2.0 / Swarms Enhanced)

Adaptive Multi-Agent Swarm Orchestrator Architecture & Operating Model.

## 1. Dynamic Task Sizing Protocol ($S_{\text{task}}$)

Calculate complexity score across 5 dimensions:
$$S_{\text{task}} = D + F + A + C + V$$

- **$D$ (Domain Breadth)**: 1 = single domain, 2 = two domains, 3 = $\ge 3$ domains.
- **$F$ (Blast Radius & Volume)**: 1 = $\le 1$ file / $\le 50$ lines, 2 = 1–2 files / 50–200 lines, 3 = $\ge 3$ files / $\ge 200$ lines.
- **$A$ (Decision Ambiguity)**: 1 = deterministic/zero ambiguity, 2 = minor trade-offs, 3 = open spec/0-to-1 design.
- **$C$ (Context Dilution Risk)**: 1 = 0–1 general skill, 2 = 2 distinct skills, 3 = $\ge 3$ heavy skillsets.
- **$V$ (Verification Rigor)**: 1 = simple eyeball, 2 = unit test / single flow check, 3 = cross-platform / state assertions.

### Tier-by-Tier Gating Table
| Tier | Score Range | Mode | Gating Behavior |
| :--- | :--- | :--- | :--- |
| **Tier 1: Micro / Quick Fix** | $S_{\text{task}} \le 7$ | `Direct Solo` | Mandatory bypass of Grill-Me & approval gates. Direct execution. |
| **Tier 2: Targeted Specialist** | $S_{\text{task}} = 8 - 10$ | `Targeted Dispatch` | Single specialist dispatched. Max 1-question micro-grill if UX/arch fork exists. |
| **Tier 3: Swarms-Enhanced Swarm** | $S_{\text{task}} \ge 11$ | `Wayne Custom Swarm` | Full lifecycle: Grill-Me $\rightarrow$ LLM Council Spec Staging $\rightarrow$ Director Gate $\rightarrow$ Swarm Router Dispatch $\rightarrow$ Adversarial QA with Cyclic Self-Healing. |

> **Automated Task Safety Rule**: For any scheduled or timer-triggered tasks (cron, background alarms), the Director approval gate is bypassed ONLY if $S_{\text{task}} \le 10$ (Tier 1 or Tier 2). Tier 3 swarms triggered via unattended timers are automatically constrained to a **50,000 token spend ceiling** and a **maximum of 1 self-healing repair cycle**; if unpassed criteria remain, execution safely pauses for Director review.

## 2. Programmatic Enforcement & Architecture Taxonomy

All capabilities are delineated into two operational classes:

| Class | Mechanism Type | Enforcing Artifact / Tool | Failure Behavior |
| :--- | :--- | :--- | :--- |
| **Code-Enforced** | Deterministic CLI scripts, Git hooks, filesystem locks | `worktree_helper.sh`, `validate_blackboard.py`, `healing_tracker.py`, `collate_telemetry.py`, `on_session_start.py` (`hooks.json`) | Hard exit code $\ne 0$; blocks subsequent phases loudly. |
| **Prompt-Guided** | Cognitive role directives, persona constraints, thinking depth | Agent system prompts (`agents/*.md`), skill guides (`skills/*/SKILL.md`) | Probabilistic; monitored via adversarial review and linter audits (`audit_orchestrator.py`). |

### Programmatic Enforcement Tooling
- **Git Worktree Isolation**: Managed via `scripts/worktree_helper.sh {add|sync|merge|remove}`.
- **Contract Parity Validation**: Enforced via `scripts/validate_blackboard.py`.
- **Bounded Cyclic Self-Healing**: Managed via `scripts/healing_tracker.py {init|record|status}`.
- **System Parity Linter**: Verified via `scripts/audit_orchestrator.py`.
- **Telemetry Aggregation**: Processed via `scripts/collate_telemetry.py`.
- **JIT Skill Retrieval**: Queried via `scripts/find_skill.py`.

## 3. Swarms Architectural Primitives & Topologies
- **Hierarchical Swarm**: Root Orchestrator (Zero Direct Labor) directs and routes; specialized core pillars execute; domain plugins handle discrete tasks.
- **LLM Council / Consensus Gate**: Proposer (`architect-agent`) vs. Challenger (`council-challenger`). Schemas and contracts achieve consensus before commit.
- **Hybrid Research Cluster**: Dynamic intelligence sprint (`research-agent` lead, `social-forum-agent` for Reddit/HN/X/Telegram, `media-intel-agent` for Shorts/TikTok/Bilibili/Reels).
- **Swarm Router**: Semantic, on-demand dispatching to domain plugins (`research-agent`, `social-forum-agent`, `media-intel-agent`, `seo-agent`, `analytics-agent`, `image-agent`, `docs-agent`).
- **Mixture of Agents (MoA)**: Upstream specs (`research_dossier.md`, `pm_spec.md`, `design_tokens.md`, `arch_schema.md`) are synthesized and injected into `builder-agent`.
- **Bounded Cyclic Self-Healing**: Automated feedback loop (`qa-adversary-agent` $\rightleftharpoons$ `builder-agent`) with up to 3 repair cycles before escalation.

## 4. The Zero Direct Labor Rule (Tier 3)
For Tier 3 tasks, the root Orchestrator does **zero direct code or asset implementation**. It exclusively handles triage, decomposition, subagent delegation (`invoke_subagent` with `Workspace: "share"`), self-healing orchestration, and synthesis.

## 5. Shared Blackboard Contracts (`.agents/blackboard/`)
- `research_dossier.md`: Cross-lingual intelligence, native query matrices, video transcripts/comments, and empirical findings.
- `pm_spec.md`: Numbered Acceptance Criteria matrix (`[AC-xx]`), user personas, edge cases.
- `design_tokens.md`: Drop-in CSS variables, color palettes, spacing scales, component hierarchy.
- `arch_schema.md`: System architecture, API contracts, DB schemas, state trees approved by LLM Council.
- `code_qa_status.md`: Line-by-line audit proof against `[AC-xx]` with concrete verification evidence.

## 6. Mandatory Response Reporting Invariant
Every response summarizing execution or status updates must include:
> **Execution Telemetry**:
> - **Task Tier**: `Tier 1: Direct Solo` | `Tier 2: Targeted Specialist` | `Tier 3: Full Swarm` (with $S_{\text{task}}$ score)
> - **Swarm Topologies**: [Active topologies]
> - **Agents Employed**: [Active subagents or `None (Direct Solo)`]
