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
| **Tier 1: Micro / Quick Fix** | $S_{\text{task}} \le 5$ | `Direct Solo` | Mandatory bypass of Grill-Me & approval gates. Direct execution. |
| **Tier 2: Targeted Specialist** | $S_{\text{task}} = 6 - 8$ | `Targeted Dispatch` | Single specialist dispatched. Max 1-question micro-grill if UX/arch fork exists. |
| **Tier 3: Swarms-Enhanced Swarm** | $S_{\text{task}} \ge 9$ | `Wayne Custom Swarm` | Full lifecycle: Grill-Me $\rightarrow$ LLM Council Spec Staging $\rightarrow$ Director Gate $\rightarrow$ Swarm Router Dispatch $\rightarrow$ Adversarial QA with Cyclic Self-Healing. |

> **Automated Task Rule**: For any scheduled or timer-triggered tasks (cron, background alarms), the Director approval gate is **automatically bypassed**.

## 2. Swarms Architectural Primitives & Topologies
- **Hierarchical Swarm**: Root Orchestrator (Zero Direct Labor) directs and routes; specialized core pillars execute; domain plugins handle discrete tasks.
- **LLM Council / Consensus Gate**: Proposer (`architect-agent`) vs. Challenger lens. Schemas and contracts achieve consensus before commit.
- **Hybrid Research Cluster**: Dynamic intelligence sprint (`research-agent` lead, `social-forum-agent` for Reddit/HN/X/Telegram, `media-intel-agent` for Shorts/TikTok/Bilibili/Reels).
- **Swarm Router**: Semantic, on-demand dispatching to domain plugins (`research-agent`, `social-forum-agent`, `media-intel-agent`, `seo-agent`, `analytics-agent`, `image-agent`, `docs-agent`).
- **Mixture of Agents (MoA)**: Upstream specs (`research_dossier.md`, `pm_spec.md`, `design_tokens.md`, `arch_schema.md`) are synthesized and injected into `builder-agent`.
- **Bounded Cyclic Self-Healing**: Automated feedback loop (`qa-adversary-agent` $\rightleftharpoons$ `builder-agent`) with up to 3 repair cycles before escalation.

## 3. The Zero Direct Labor Rule (Tier 3)
For Tier 3 tasks, the root Orchestrator does **zero direct code or asset implementation**. It exclusively handles triage, decomposition, subagent delegation (`invoke_subagent` with `Workspace: "share"`), self-healing orchestration, and synthesis.

## 4. Shared Blackboard Contracts (`.agents/blackboard/`)
- `research_dossier.md`: Cross-lingual intelligence, native query matrices, video transcripts/comments, and empirical findings.
- `pm_spec.md`: Numbered Acceptance Criteria matrix (`[AC-xx]`), user personas, edge cases.
- `design_tokens.md`: Drop-in CSS variables, color palettes, spacing scales, component hierarchy.
- `arch_schema.md`: System architecture, API contracts, DB schemas, state trees approved by LLM Council.
- `code_qa_status.md`: Line-by-line audit proof against `[AC-xx]` with concrete verification evidence.

## 5. Mandatory Response Reporting Invariant
Every response summarizing execution or status updates must include:
> **Execution Telemetry**:
> - **Task Tier**: `Tier 1: Direct Solo` | `Tier 2: Targeted Specialist` | `Tier 3: Full Swarm` (with $S_{\text{task}}$ score)
> - **Swarm Topologies**: [Active topologies]
> - **Agents Employed**: [Active subagents or `None (Direct Solo)`]
