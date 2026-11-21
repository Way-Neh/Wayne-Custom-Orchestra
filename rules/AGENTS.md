# Wayne Custom Swarm — Universal Core Directives

## 1. Dynamic Task Sizing Protocol ($S_{\text{task}}$)
The swarm activates dynamically based on the 5-factor complexity score:
$$S_{\text{task}} = D + F + A + C + V$$

- **$D$ (Domain Breadth)**: 1 = single domain, 2 = two domains, 3 = $\ge 3$ domains.
- **$F$ (Blast Radius & Volume)**: 1 = $\le 1$ file / $\le 50$ lines, 2 = 1–2 files / 50–200 lines, 3 = $\ge 3$ files / $\ge 200$ lines.
- **$A$ (Decision Ambiguity)**: 1 = deterministic/zero ambiguity, 2 = minor trade-offs, 3 = open spec/0-to-1 design.
- **$C$ (Context Dilution Risk)**: 1 = 0–1 general skill, 2 = 2 distinct skills, 3 = $\ge 3$ heavy skillsets.
- **$V$ (Verification Rigor)**: 1 = simple eyeball, 2 = unit test / single flow check, 3 = cross-platform / state assertions.

### Execution Tiers:
- **Tier 1 ($S_{\text{task}} \le 7$)**: `Direct Solo`. Auto-bypass Grill-Me and approval gates. Fast, direct single-agent execution without subagent overhead.
- **Tier 2 ($S_{\text{task}} = 8 - 10$)**: `Targeted Specialist`. Conditional 1-question micro-grill if UX/arch fork exists. Dispatches single domain specialist.
- **Tier 3 ($S_{\text{task}} \ge 11$)**: `Wayne Custom Swarm`. Full multi-agent swarm. Root Orchestrator enforces **Zero Direct Labor**.

---

## 2. Machine Blackboard Contracts & Autonomous Onboarding (`.agents/blackboard/`)
- **Autonomous Project Onboarding**: Whenever beginning work in any project where `.agents/blackboard/` does not yet exist or is incomplete, the Orchestrator MUST autonomously bootstrap `.agents/blackboard/` (and ensure Git is initialized) before planning or staging specs. Never require the user to run manual setup commands.
- All cross-agent collaboration operates strictly via structured files in `.agents/blackboard/`:
- **`research_dossier.md`**: Upstream technical, market, and competitive intelligence with numbered findings (`[RES-01]`, `[RES-02]`), cross-lingual query matrix, platform provenance matrix, multimodal video/comment extracts, and impact recommendations.
- **`pm_spec.md`**: Numbered Acceptance Criteria (`[AC-01]`, `[AC-02]`), Edge Cases (`[AC-10]`), Failure Modes (`[AC-20]`), Negative Acceptance Criteria (`[NAC-01]`), finite state tables, and explicit non-goals.
- **`design_tokens.md`**: 3-tier CSS custom property blocks (`primitive` &rarr; `semantic` &rarr; `component`), OKLCH scales, and clamp typography. No runtime code.
- **`arch_schema.md`**: Machine-enforceable types (TypeScript / Zod), DB schemas, mutation lifecycles, and STRIDE threat models.
- **`code_qa_status.md`**: Line-by-line verification matrix against every `[AC-xx]` ID with concrete reproduction proofs and diff telemetry.
- **Contract Parity Validation**: Before builder hand-off, the blackboard MUST be validated using `scripts/validate_blackboard.py`.

---

## 3. Worker Worktree Isolation & Re-Sync Invariant
- Concurrent builders MUST implement features strictly inside dedicated Git worktrees managed via `scripts/worktree_helper.sh {add|sync|merge|remove}`: `.worktrees/worker-<id>` on branch `swarm/worker-<id>`.
- Never commit directly to `main`, `master`, or unmerged integration branches (`feat/<task>`).
- **Self-Healing Re-Sync Protocol (Iterations 2 & 3)**:
  Before applying fixes in Iteration $N$, `builder-agent` MUST re-synchronize its worktree branch with the local integration branch:
  ```bash
  bash scripts/worktree_helper.sh sync <worker-id> feat/<task>
  # Fallback:
  git merge --ff-only feat/<task> || git rebase feat/<task>
  ```
  This ensures the builder develops fixes against the exact integrated codebase audited by QA.

---

## 4. Adversarial Verification & Cognitive Parity Invariant
- **Zero Self-Auditing**: Under no circumstances may the agent that authored the code audit its own implementation. `builder-agent` and `qa-adversary-agent` are strictly decoupled.
- **Cognitive Parity**: On Tier 3 Swarms ($S_{\text{task}} \ge 11$), `qa-adversary-agent` MUST operate on cognitive parity with `builder-agent` (`Model: "pro"`, High thinking) to prevent shallow verification and unverified self-healing loops.
- **Independent Evidence**: The adversary must execute deterministic reproduction commands and confirm line-by-line evidence before marking any `[AC-xx]` as passed.

---

## 5. Bounded Cyclic Self-Healing & Escalation Gate
- Automated feedback loop (`qa-adversary-agent` $\rightleftharpoons$ `builder-agent`): maximum **3 repair iterations**, tracked deterministically via `scripts/healing_tracker.py`.
- **Regression Lock Rule**: Criteria verified as PASS (`[x]`) in iteration $N$ are permanently locked. Any subsequent fix breaking a passing criterion is flagged by `healing_tracker.py` as a `REGRESSION_VIOLATION`.
- **Architectural Escalation Gate**: If the same criterion fails across 2 consecutive iterations, `healing_tracker.py` flags an architectural escalation. The Orchestrator pauses `builder-agent` and dispatches `architect-agent` to evaluate whether `arch_schema.md` or API contracts require revision before attempting iteration 3.
- If issues remain unresolved after 3 iterations, execution cleanly halts and escalates to the Director with complete diagnostic telemetry.

---

## 6. Mandatory Telemetry Reporting Protocol
Upon completing an assigned task, every subagent MUST report its assigned model and token consumption metrics in its final completion message to the caller via `send_message`:
- **Model Used**: Actual assigned model identifier (e.g. `Gemini 3.8 Pro (High)`, `Gemini 3.8 Flash (High)`).
- **Token Metrics**: `Input Tokens`, `Output Tokens`, `Cache Read Tokens`, `Total Tokens`.

---

## 7. Hybrid Research Cluster & Multimodal Protocol
When exploratory, competitive, or cross-domain research is required:
- **`research-agent` (Cognitive Lead: `pro`)**: Formulates the cross-lingual query matrix (EN, ZH, JA, KO, RU), coordinates platform investigations, calibrates bias, and stages `research_dossier.md`.
- **`social-forum-agent` (Specialist: `flash`)**: Extracts community sentiment, edge cases, and practitioner experiences from Reddit, Hacker News, X/Twitter, Telegram, and non-English developer forums.
- **`media-intel-agent` (Specialist: `flash`/`pro`)**: Ingests short-form video (TikTok, YouTube Shorts, Reels, Bilibili, Douyin), extracts deduplicated multi-lingual subtitles, mines top comments, and samples keyframes with `ffmpeg` for visual architecture/code inspection.

---

## 8. Unattended Execution Safety Ceiling
- For background scheduled/timer automations (cron jobs), the Director approval gate is bypassed ONLY if $S_{\text{task}} \le 10$ (Tier 1 or Tier 2).
- Any unattended Tier 3 swarm ($S_{\text{task}} \ge 11$) is strictly capped at a **50,000 total token spend limit** and a **maximum of 1 self-healing repair cycle** before halting and demanding Director authorization.

---

## 9. Programmatic vs. Heuristic Architecture Taxonomy (Code-Enforced vs. Prompt-Guided)
To prevent conflating prompt guidance with deterministic guarantees, all swarm mechanisms are strictly classified:

| Class | Mechanism Type | Enforcing Artifact / Tool | Failure Behavior |
| :--- | :--- | :--- | :--- |
| **Code-Enforced** | Deterministic CLI scripts, Git hooks, filesystem locks | `worktree_helper.sh`, `validate_blackboard.py`, `healing_tracker.py`, `collate_telemetry.py`, `on_session_start.py` (`hooks.json`) | Hard exit code $\ne 0$; blocks subsequent phases loudly. |
| **Prompt-Guided** | Cognitive role directives, persona constraints, thinking depth | Agent system prompts (`agents/*.md`), skill guides (`skills/*/SKILL.md`) | Probabilistic; monitored via adversarial review and linter audits (`audit_orchestrator.py`). |

