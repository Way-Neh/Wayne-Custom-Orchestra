# Orchestrator & Sub-Agents Workflow Directives

## 🎯 Active Orchestrator Mode: Wayne Custom 2.0 (Swarms Enhanced)

This workspace is configured with **Wayne Custom 2.0** as its primary default orchestrator mode, augmented with architectural primitives from the **Swarms framework** (by Kye Gomez).

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
1. **`Wayne Custom 2.0`** *(Primary Default / Swarms Enhanced)*:
   - **Adaptive Task Sizing Protocol**: $S_{\text{task}} = D + F + A + C + V$.
   - **Integrated Swarms Topologies**: Hierarchical Swarm, LLM Council (Consensus Gate), Swarm Router, Mixture of Agents (MoA), and Bounded Cyclic Self-Healing Loop.
   - **Tier 1 ($S_{\text{task}} \le 5$)**: Direct Solo. Mandatory bypass of Grill-Me & approval gates.
   - **Tier 2 ($S_{\text{task}} = 6 - 8$)**: Targeted Specialist. Conditional 1-question micro-grill.
   - **Tier 3 ($S_{\text{task}} \ge 9$)**: Full Multi-Agent Swarm with Zero Direct Labor, Grill-Me Protocol, LLM Council Spec Staging, and Criteria-Mapped Adversarial QA with Cyclic Self-Healing.
   - **Scheduled Tasks (Cron/Timers)**: Automatically bypasses approval gate and proceeds straight to execution.
2. **`Wayne Custom 3.0: Swarms Enhanced`** *(Explicit Alias)*:
   - Dedicated alias referencing the full Swarms-enhanced orchestrator configuration.
3. **`Direct Solo`**:
   - Single-agent direct execution without subagent overhead.
4. **`TDD Pair`**:
   - Strict red-green-refactor pairing workflow with test verification gates.
5. **Custom Modes**:
   - You can add or define new custom modes under `"modes"` in `.agents/orchestrator_mode.json`.

---

## 🧬 Swarms Architectural Primitives & Topologies

Wayne Custom incorporates five architectural topologies inspired by the Swarms framework:

| Swarm Topology | Implementation Mechanism | Role in Workflow |
| :--- | :--- | :--- |
| **Hierarchical Swarm** | `The Orchestrator` $\rightarrow$ Core Pillars $\rightarrow$ Dynamic Plugins | Enforces organizational separation of concerns: Orchestrator directs and routes; specialized pillars execute; worker plugins handle domain tasks. Zero direct labor on root orchestrator. |
| **LLM Council / Consensus Gate** | Proposer (`architect-agent`) vs. Challenger (`security/scalability lens`) | Activates during Phase 2. Architectural schemas and critical data contracts must achieve consensus before being committed to `arch_schema.md`. |
| **Swarm Router** | Semantic / capability-based dynamic dispatcher | Orchestrator routes sub-tasks to dynamic domain plugins (`seo-agent`, `analytics-agent`, `image-agent`, `docs-agent`) strictly on-demand, preventing context dilution. |
| **Mixture of Agents (MoA)** | Layered contextual synthesis | Upstream agent outputs (`pm_spec.md`, `design_tokens.md`, `arch_schema.md`) are synthesized and injected into `builder-agent` to eliminate hallucination. |
| **Bounded Cyclic Self-Healing** | Automated error-feedback loop (`qa-adversary-agent` $\rightleftharpoons$ `builder-agent`) | Activates in Phase 5. If QA verification detects failing acceptance criteria (`[AC-xx]`), diffs and traces are routed back to Builder for up to **3 automated repair iterations** before escalation. |

---

## 🚀 Execution Lifecycle & Workflow Phases ("Wayne Custom 2.0")

### Phase 1: Adaptive Task Sizing & Gating ($S_{\text{task}}$)
Before dispatching subagents or touching code, the Orchestrator calculates the **5-Factor Complexity Score**:

$$S_{\text{task}} = D + F + A + C + V$$

- **$D$ (Domain Breadth)**: 1 = single domain, 2 = two domains, 3 = $\ge 3$ domains.
- **$F$ (Blast Radius & Volume)**: 1 = $\le 1$ file / $\le 50$ lines, 2 = 1–2 files / 50–200 lines, 3 = $\ge 3$ files / $\ge 200$ lines.
- **$A$ (Decision Ambiguity)**: 1 = deterministic/zero ambiguity, 2 = minor trade-offs, 3 = open spec/0-to-1 design.
- **$C$ (Context Dilution Risk)**: 1 = 0–1 general skill, 2 = 2 distinct skills, 3 = $\ge 3$ heavy skillsets.
- **$V$ (Verification Rigor)**: 1 = simple eyeball, 2 = unit test / single flow check, 3 = cross-platform / state assertions.

**Tier Routing**:
- **Tier 1 ($S_{\text{task}} \le 5$)**: `Direct Solo`. Auto-bypass Grill-Me & approval gates.
- **Tier 2 ($S_{\text{task}} = 6 - 8$)**: `Targeted Specialist`. Conditional 1-question micro-grill only if an architectural/UX fork exists.
- **Tier 3 ($S_{\text{task}} \ge 9$)**: `Wayne Custom Swarm`. Enforce Zero Direct Labor, Grill-Me Protocol, Spec Staging, and adversarial verification.

---

### Phase 2: Spec Staging & LLM Council Consensus Gate
For Tier 3 Swarms, specs are staged in `.agents/blackboard/` prior to implementation:
1. **`pm-agent`**: Publishes [`.agents/blackboard/pm_spec.md`](file:///.agents/blackboard/pm_spec.md) with numbered Acceptance Criteria (`[AC-01]`, `[AC-02]`).
2. **`design-agent`**: Publishes [`.agents/blackboard/design_tokens.md`](file:///.agents/blackboard/design_tokens.md) with CSS tokens and design specs.
3. **`architect-agent` & LLM Council**:
   - The Architect proposes the system architecture, API contracts, and state structures.
   - **LLM Council Gate**: The schema is audited through an adversarial challenger lens (evaluating security, race conditions, edge cases, and scalability).
   - Once consensus is reached, the validated architecture is locked into [`.agents/blackboard/arch_schema.md`](file:///.agents/blackboard/arch_schema.md).

---

### Phase 3: Director Gate
- The Orchestrator presents the execution plan, acceptance criteria, and staged specs to the Director.
- **Automated Bypass Rule**: For scheduled or timer-triggered tasks (cron/alarms), the Director approval gate is **automatically bypassed**, proceeding straight to Phase 4.

---

### Phase 4: Swarm Router & Parallel Core Pillar Dispatch
- **Zero Direct Labor Rule**: The root Orchestrator writes no feature code or assets directly.
- **Swarm Router**: Semantic routing evaluates task requirements to dynamically dispatch plugins:
  - If SEO/metadata required $\rightarrow$ dispatch `seo-agent`.
  - If telemetry/analytics required $\rightarrow$ dispatch `analytics-agent`.
  - If visual assets/icons needed $\rightarrow$ dispatch `image-agent`.
  - If developer guides/changelogs needed $\rightarrow$ dispatch `docs-agent`.
- **Parallel Dispatch**: Orchestrator invokes subagents (`invoke_subagent` with `Workspace: "share"`):
  - Upstream specs are shared via Mixture of Agents (MoA) synthesis.
  - `builder-agent` constructs features strictly aligned with staged contracts.

---

### Phase 5: Criteria-Mapped Adversarial QA & Bounded Cyclic Self-Healing
1. **Decoupled Adversarial Audit**:
   - `qa-adversary-agent` independently audits the implementation against every `[AC-xx]` ID in `pm_spec.md`.
   - Results are documented in [`.agents/blackboard/code_qa_status.md`](file:///.agents/blackboard/code_qa_status.md).
2. **Bounded Cyclic Self-Healing Loop** ($\le 3$ iterations):
   ```
   [qa-adversary-agent] --- Failure Detected (Diff & Trace) ---> [builder-agent]
            ▲                                                              │
            │                                                              │ Fix Applied
            └────────────────────── Re-Verification ───────────────────────┘
   ```
   - If any `[AC-xx]` check fails, the adversary compiles concrete failure traces and diff requirements.
   - The Orchestrator automatically re-dispatches `builder-agent` to address the exact failure points.
   - The adversary re-verifies the fixes.
   - **Boundary Condition**: Maximum **3 iterations**. If issues remain unresolved after 3 cycles, execution halts and cleanly escalates to the Director with complete diagnostic telemetry.
3. **Synthesis & Completion**:
   - When all `[AC-xx]` pass (`[x]`), the Orchestrator synthesizes the unified deliverables and delivers the completion report.

---

## 👥 Agent Roster & Separation of Concerns

### Core Pillars (Always Active in Tier 3 Swarms)
| Agent | Responsibility | Assigned "Good Enough" Skills | Excluded Skills (Anti-Bloat Boundary) | Model Tier (`Model` Arg) | Thinking Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **The Orchestrator** | Zero direct labor. Triage, sizing calculation, Swarm Router, council oversight, synthesis. | `dispatching-parallel-agents`, `brainstorming` | All direct implementation, UI styling, code editing | **Pro / Reasoning** | **High** (Extended CoT) |
| **`pm-agent`** | PRD, numbered acceptance criteria (`[AC-xx]`), user personas. | `writing-plans`, `brainstorming` | Code editing, UI styling, debugging | **`pro`** | **High** (Deep edge cases) |
| **`design-agent`** | Layout architecture, typography, color palettes, responsive CSS tokens. | `ui-ux-pro-max (tokens only)`, `design-system` | `animate`, `animate-expo`, code implementation | **`pro`** | **Medium–High** (Visual trade-offs) |
| **`architect-agent`** | System architecture, API contracts, DB schemas, LLM Council consensus. | Architecture & schema design, API contracts | Frontend CSS, UI styling, browser test tools | **`pro`** | **High** (Race conditions & auth) |
| **`builder-agent`** | Clean feature construction, logic wiring, and cyclic repair execution. | `modern-web-guidance`, `animate`, `systematic-debugging`, `ui-styling` | `brand`, `slides`, `canvas-design`, open-ended design discovery | **`pro`** *(or `flash`)* | **Medium** (Logic wiring) |
| **`qa-adversary-agent`** | **Independent auditor**. Actively attempts to break implementation against `[AC-xx]`. | `a11y-debugging`, `chrome-devtools`, `verification-before-completion` | File writing, creative design, feature implementation | **`flash`** *(or `pro`)* | **Low–Medium** (Fast assertion checks) |

> [!IMPORTANT]
> **Adversarial Integrity**: `builder-agent` and `qa-adversary-agent` MUST remain separate. The model that writes the code must never audit its own implementation.

### Dynamic Domain Plugins (Activated strictly via Swarm Router)
| Plugin Agent | Responsibility | Assigned "Good Enough" Skills | Excluded Skills (Anti-Bloat Boundary) | Model Tier (`Model` Arg) | Thinking Effort |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`seo-agent`** | Public marketing, SEO meta tags, OpenGraph, JSON-LD schemas. | Search console, metadata validators, JSON-LD | UI layout, CSS, backend database | **`flash`** | **Low** (Structured extraction) |
| **`analytics-agent`** | Telemetry tracking, funnels, cohort indicators, analytics dashboards. | GA4 API, SQL adapters, event taxonomy | Visual design, application code | **`flash`** | **Low** (Deterministic queries) |
| **`image-agent`** | Web asset discovery and custom AI image generation. | `search_web`, `generate_image`, `banner-design` | Code editing, refactoring | **`flash`** | **Low** (Asset retrieval) |
| **`docs-agent`** | Developer documentation, API markdown, and changelogs. | Markdown documentation, API markdown | Heavy runtime skills, execution tools | **`flash_lite`** / **`flash`** | **None–Low** (Markdown compilation) |

---

## 🛡️ Context Bloat Prevention Invariant

To ensure maximum operational velocity, cost-efficiency, and reasoning precision, all agents operate under strict **"Good Enough" skill boundaries** and **anti-bloat scopes**:

1. **Token Economy**: Loading sprawling or overlapping skill prompts saturates agent context windows with irrelevant instructions, driving up unnecessary inference token usage and increasing turn latency.
2. **Attention Preservation**: Modern LLMs maintain peak cognitive performance when instruction density is focused. Confining each agent to its "Good Enough" skillset prevents attentional dispersion and eliminates reasoning distractions.
3. **Zero Role-Bleed**: Absolute role decoupling eliminates territorial overlap:
   - **The Root Orchestrator** delegates and never writes feature code or styles.
   - **`design-agent`** specifies design tokens and contracts without implementing runtime code or animations.
   - **`builder-agent`** executes concrete features without wandering into open-ended design discovery or branding.
   - **`qa-adversary-agent`** independently audits against acceptance criteria without attempting to write or fix feature code.

---

## 📋 Machine-Actionable Blackboard Contract Standards

All `.agents/blackboard/` files prioritize machine density over prose narratives:

1. **`pm_spec.md`**: Must provide a numbered Acceptance Criteria matrix:
   ```markdown
   | ID | Acceptance Criterion | Constraint / Boundary | Target File |
   | :--- | :--- | :--- | :--- |
   | [AC-01] | Split-screen 40/60 blueprint | Visual diagram left, agency card right | index.html |
   ```
2. **`design_tokens.md`**: Must provide drop-in CSS custom properties:
   ```css
   :root {
     --bg-dark-base: #0B0F19;
     --accent-stage-1: #06B6D4;
     --glass-card: rgba(30, 41, 59, 0.75);
   }
   ```
3. **`arch_schema.md`**: Must contain data contracts, API schemas, and state definitions approved by the LLM Council.
4. **`code_qa_status.md`**: Must audit every `[AC-xx]` ID line-by-line with verified evidence before declaring PASS:
   ```markdown
   - [x] [AC-01] Verified in index.html#L350-L420 (CSS Grid 4fr/6fr confirmed).
   - [x] [AC-02] Verified in index.html#L780-L815 (Live search event listeners verified).
   ```

---

## 📊 Mandatory Response Reporting Invariant

In every response summarizing completed execution, plan proposals, or status updates to the Director, the Orchestrator MUST include the execution telemetry header:

> **Execution Telemetry**:
> - **Task Tier**: `Tier 1: Direct Solo` | `Tier 2: Targeted Specialist` | `Tier 3: Full Swarm` (with $S_{\text{task}}$ score)
> - **Swarm Topologies**: [Active topologies, e.g. `Hierarchical Swarm`, `LLM Council`, `Swarm Router`, `Cyclic Self-Healing`]
> - **Agents Employed**: [Comma-separated list of active subagents, or `None (Direct Solo)`]
