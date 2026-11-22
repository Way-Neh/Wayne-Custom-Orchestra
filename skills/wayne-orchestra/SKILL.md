---
name: wayne-orchestra
description: Wayne Custom 3.0 (Native Swarm Hybrid) Adaptive Multi-Agent Swarm Orchestrator architecture, operating model, dynamic task sizing (S_task), blackboard contracts, topic channels, and bounded cyclic self-healing QA.
---

# Wayne Custom Orchestra (Wayne Custom 3.0 / Native Swarm Hybrid)

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
- **Swarm Orchestrator & Channel Manager**: Managed via `scripts/swarm_orchestrator.py` (automates multi-channel provisioning, brief generation, persona loading, workspace sharing, and spending limits).
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
For Tier 3 tasks, the root Orchestrator does **zero direct code or asset implementation**. It exclusively handles triage, decomposition, subagent delegation (`invoke_subagent` or native `swarm` tools with `Workspace: "share"`), self-healing orchestration, and synthesis.

## 5. Shared Blackboard Contracts (`.agents/blackboard/`)
- `research_dossier.md`: Cross-lingual intelligence, native query matrices, video transcripts/comments, and empirical findings.
- `pm_spec.md`: Numbered Acceptance Criteria matrix (`[AC-xx]`), user personas, edge cases.
- `design_tokens.md`: Drop-in CSS variables, color palettes, spacing scales, component hierarchy.
- `arch_schema.md`: System architecture, API contracts, DB schemas, state trees approved by LLM Council.
- `code_qa_status.md`: Line-by-line audit proof against `[AC-xx]` with concrete verification evidence.

## 6. Hybrid Native Swarm Execution Mode ($S_{\text{task}} \ge 11$)

For Tier 3 tasks, Wayne Custom Orchestra activates the **Hybrid Native Swarm Execution Mode**, coupling Wayne's rigorous machine blackboard contracts and cognitive tiering with Antigravity Native Swarm's pub/sub message board, workstream channels, shared workspaces, and live UI visualization.

### Topic-Based Channel Architecture
To prevent context dilution and subagent noise, execution is decoupled across dedicated topic channels managed by `scripts/swarm_orchestrator.py`:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Native Swarm Message Board                      │
│                                                                        │
│   #council            #builders                       #qa             │
│   ┌──────────────┐    ┌─────────────────────────┐     ┌──────────────┐ │
│   │ architect    │    │ builder-api (worktree)  │     │ qa-adversary │ │
│   │ challenger   │    │ builder-ui  (worktree)  │     │ (audit &     │ │
│   │ (STRIDE &    │    │ (shared workspace &     │     │  healing)    │ │
│   │  consensus)  │    │  [done] markers)        │     │              │ │
│   └──────────────┘    └─────────────────────────┘     └──────────────┘ │
│                               ▲                              │         │
│                               └─────── repair feedback ──────┘         │
└────────────────────────────────────────────────────────────────────────┘
```

1. **`#council` (Phases 1 & 2 — Spec Staging & LLM Council Debate)**:
   - Dedicated channel for `pm-agent`, `architect-agent`, and `council-challenger`.
   - Proposer (`architect-agent`) stages system topology and Zod schemas against `pm_spec.md`.
   - Challenger (`council-challenger`) conducts adversarial STRIDE threat modeling, concurrency hazard scans, and scalability stress tests.
   - Debate is strictly bounded ($\le 2$ exchanges) to prevent circular argument; locks into `arch_schema.md` upon consensus (`[CONSENSUS_ACHIEVED]`).

2. **`#builders` (Phase 4 — Concurrent Worker Implementation)**:
   - Dedicated channel for parallel builder workers (`builder-api`, `builder-ui`, etc.).
   - Workers execute with shared workspace access (`workspace: "share"`) and physical isolation in Git worktrees (`.worktrees/worker-<id>` on branch `swarm/worker-<id>`).
   - Workers communicate progress via targeted `@mention` syntax and complete tasks with standard `[done]` prefix markers.

3. **`#qa` (Phase 5 — Adversarial Audit & Bounded Cyclic Self-Healing)**:
   - Dedicated channel for `qa-adversary-agent` operating on cognitive parity (`Model: "pro"`).
   - Mechanically verifies merged code on `feat/<task>` against every acceptance criterion in `pm_spec.md`.
   - On defects, posts targeted failure reports (criterion ID, reproduction command, stack trace) directly to `#qa` tagging the responsible builder.
   - Orchestrated via `scripts/healing_tracker.py` with maximum 3 repair iterations and Regression Lock enforcement.

### Native Auxiliary Roles
1. **`narrator` (Live Visual Overview UI)**:
   - Maintains the real-time visual Overview dashboard in the Antigravity Swarm UI for the Director.
   - Synthesizes the active lifecycle phase, $S_{\text{task}}$ score, passing/failing `[AC-xx]` count, and healing iteration count ($N/3$) without clogging developer logs.
2. **`monitor` (Stall Watchdog & Deadlock Breaker)**:
   - Continuously monitors worker turn durations and message board liveness.
   - Alerts the Root Orchestrator if builds, test runs, or channel handoffs hang or exceed reasonable operational thresholds.

### Brief Generator & Channel Manager (`scripts/swarm_orchestrator.py`)
- Programmatic CLI helper that provisions topic channels (`#council`, `#builders`, `#qa`), formats standardized, persona-bound worker briefs, sets up channel subscriptions, model tier pinning (`pro` vs `flash`), and workspace sharing flags (`workspace: "share"`).
- Automatically enforces safety ceilings, token spending limits, and clean teardown (`swarm{action: "kill", name: "all"}`) upon lifecycle completion.

## 7. Mandatory Response Reporting Invariant
Every response summarizing execution or status updates must include:
> **Execution Telemetry**:
> - **Task Tier**: `Tier 1: Direct Solo` | `Tier 2: Targeted Specialist` | `Tier 3: Full Swarm` (with $S_{\text{task}}$ score)
> - **Swarm Topologies**: [Active topologies]
> - **Agents Employed**: [Active subagents or `None (Direct Solo)`]
