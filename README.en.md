# Build Great Loop · Loop Engineering Skills

[中文](README.md) | [English](README.en.md)

![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827)
![Claude Compatible](https://img.shields.io/badge/Claude-Compatible-6B46C1)
![Skills](https://img.shields.io/badge/Skills-6%20loop%20%2B%20skill--craft-0E7490)
![Benchmarked](https://img.shields.io/badge/Benchmark-6%20rounds%20adversarial-success)
![Field Tested](https://img.shields.io/badge/Field%20Tested-real%20run%202026--07-8B5CF6)
![Language](https://img.shields.io/badge/Language-ZH%20%2B%20EN-blue)
![License](https://img.shields.io/github/license/VioletScar-Hui/Build_Great_Loop)
![Status](https://img.shields.io/badge/Status-Active-success)

A **composable "Loop Engineering" skill group** for both Codex and Claude Code.
Trigger it whenever you need an AI to **run on its own, run until done, survive being
interrupted, and not fake completion** — it interviews your task and emits a
**ready-to-paste, top-tier loop prompt (harness)**.

> The model is the engine; the loop is the whole chassis around it: the goal it
> steers by, the state it remembers, the verification that keeps it honest, and the
> conditions that tell it to stop. This skill group turns "what a senior engineer does
> instinctively" into default instructions inside the prompt.

![Build Great Loop — the 4-skill workflow](assets/workflow.svg)

---

## What it is

`Build Great Loop` isn't one monolithic skill — it's **4 skills, each with its own job,
independently triggerable, and composable**:

| Skill | What it does | When it triggers |
|---|---|---|
| **loop-spec** | Interview a fuzzy task into a runnable `SPEC.md` | Task isn't pinned down yet — need goal / success criteria / stop conditions first |
| **loop-engineering** (core) | Interview → emit the **paste-ready loop prompt itself** | "Write me an agent / loop / harness that keeps going until it's done" |
| **loop-eval** | Design success criteria + a small eval set + graders (pass@k vs pass^k) | "How do I know this loop is reliable / write evals for my agent" |
| **loop-review** | Audit and harden an **existing** loop prompt | "My agent never stops / says done when it isn't / loses progress on restart" |
| **loop-ops** | Operate a loop as a recurring / unattended automation (scheduling · cost · safety gates · rollout) | "Run this agent daily / on every PR / nightly", "babysit my PRs", "auto-triage issues", "how do I run it unattended safely" |
| **loop-retro** | Post-run retrospective: evidence-cited diagnosis → harness revisions + real-failure gotchas + standards proposals + **sedimentation check** | "My loop finished — retro it", "why did it thrash / overspend", "analyze the run log" |
| **skill-craft** | Full skill-lifecycle methodology front door: create / modify / diagnose / merge / retire (three-criteria gate, evals-first, pressure testing) | "Write me a skill", "why doesn't my skill trigger", "should these two skills merge", "retire this old skill" |

The method is distilled from official engineering writing by Anthropic, GitHub,
Sourcegraph, and OpenAI (see [Sources](#sources--credits)).

---

## Use cases

- Autonomous coding / build-until-green: implement endpoints/features one at a time until tests pass.
- Batch processing: label / clean / translate thousands of items overnight, resumable.
- Autonomous research: gather authoritative sources, dig until confident, write up with citations.
- Debug loops: reproduce → hypothesize → verify → fix, until the root cause is nailed.
- Long jobs (data migration, etc.) that "run for hours, will be interrupted, must never double-write or skip."
- And — **auditing an existing loop prompt** to tell you exactly where it'll break and how to fix it.

---

## Installation

### Easiest: let your AI agent install it from the URL

Just tell your Codex / Claude Code:

> Install this skill group: `https://github.com/VioletScar-Hui/Build_Great_Loop`
> Copy the seven folders `loop-spec` / `loop-engineering` / `loop-eval` / `loop-review` /
> `loop-ops` / `loop-retro` / `skill-craft` into my skills directory.

> Run the commands below **in a terminal** (PowerShell on Windows; Terminal on
> macOS/Linux). Optional companion: skill-craft's benchmark machinery reuses
> Anthropic's `skill-creator` (not bundled here; the methodology works without it).

### Codex (Windows PowerShell)

```powershell
$tmp = Join-Path $env:TEMP "build_great_loop"
git clone --depth 1 https://github.com/VioletScar-Hui/Build_Great_Loop $tmp
$dest = "$env:USERPROFILE\.codex\skills"
New-Item -ItemType Directory -Force $dest | Out-Null
"loop-spec","loop-engineering","loop-eval","loop-review","loop-ops","loop-retro","skill-craft" | ForEach-Object {
  Copy-Item -Recurse -Force "$tmp\$_" $dest
}
Remove-Item -Recurse -Force $tmp
```

### Claude Code (Windows PowerShell)

```powershell
$tmp = Join-Path $env:TEMP "build_great_loop"
git clone --depth 1 https://github.com/VioletScar-Hui/Build_Great_Loop $tmp
$dest = "$env:USERPROFILE\.claude\skills"
New-Item -ItemType Directory -Force $dest | Out-Null
"loop-spec","loop-engineering","loop-eval","loop-review","loop-ops","loop-retro","skill-craft" | ForEach-Object {
  Copy-Item -Recurse -Force "$tmp\$_" $dest
}
Remove-Item -Recurse -Force $tmp
```

### macOS / Linux (bash)

```bash
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/VioletScar-Hui/Build_Great_Loop "$tmp"
dest="$HOME/.claude/skills"          # for Codex use "$HOME/.codex/skills"
mkdir -p "$dest"
for s in loop-spec loop-engineering loop-eval loop-review loop-ops loop-retro skill-craft; do cp -R "$tmp/$s" "$dest/"; done
rm -rf "$tmp"
```

### Quick install check for agents

```powershell
"loop-spec","loop-engineering","loop-eval","loop-review","loop-ops","loop-retro","skill-craft" | ForEach-Object {
  $p = "$env:USERPROFILE\.claude\skills\$_\SKILL.md"   # .codex for Codex
  if (Test-Path $p) { "OK  $_" } else { "MISSING  $_" }
}
```

Four `OK` lines means you're installed.

---

## First successful run

After installing, open a fresh session and describe — in natural language — any task that
**needs to run repeatedly**, for example:

> Write me a reliable loop: for each `.md` in `notes/`, generate a one-sentence summary
> and append it to `summaries.csv`; it must resume after an interruption, never duplicate,
> never skip.

`loop-engineering` triggers, asks one or two key questions (what counts as done, when to
stop), then emits a **paste-ready** loop prompt — with verifiable success criteria, stop
conditions (incl. a hard cap), the five-beat loop, externalized state, crash-safe resume,
verification + guardrails, and a one-line glanceable status.

---

## Workflow

The four skills work standalone, or chained:

```
loop-spec  ──►  loop-engineering  ──►  loop-eval
(set goal)      (emit the loop prompt)  (design verification/evals)
                       ▲
                       │
                  loop-review   (bring an existing prompt to audit & harden)
```

---

## The core method

![The five-beat loop: Orient → Plan → Act → Verify → Record](assets/five-beats.svg)

- **Five beats**: `Orient` (read state first) → `Plan` (pick one smallest increment) →
  `Act` (do only that) → `Verify` (test it like a user would) → `Record` (write durable
  state, leave it clean and handoff-ready).
- **Seven design dimensions**: goal & verifiable success criteria, stop conditions, the
  loop skeleton, state & memory, context discipline, tools, verification & guardrails.
- **Two killer failure modes**: over-ambition (one-shotting → context blows up) and false
  completion (declaring done untested) — every output must defend against both by name.
- **Four "operational rigor" upgrades** (good → top-tier): machine-checkable success
  criteria, crash-safe + idempotent resume, deliberately sized caps, a glanceable operator
  status.
- **Mandatory interactive intake** (v4+): clarify → standards → goal tree → sign-off;
  a hard **final stop-condition confirmation** before delivery; tiny tasks take a
  3-question lite path (all four lite criteria required).
- **Profile prefill + the unknowns quadrant** (v7): answered questions are never re-asked
  (`~/.claude/loop-profile.md`); unfamiliar domains get a **blindspot pass**, fuzzy quality
  targets get **samples-first** elicitation, and references beat descriptions.
- **Shakedown + calibration + Deviations**: auto-continue stays locked until a deliberate
  kill/resume test passes; quality-fuzzy loops carry golden-set calibration increments;
  off-plan surprises follow conservative-choice + log + continue.
- **The retro flywheel** (loop-retro): real failures become gotcha evals; loops that ran
  well get a three-criteria sedimentation check → handed to skill-craft to become a
  reusable skill — one-off work turns into compounding assets.

See `loop-engineering/references/` (`principles` / `patterns` / `harness-template` /
`context-and-state` / `checklist`).

---

## Why trust it

Not vibes — six rounds of snapshot-vs-snapshot benchmarking (adversarially graded by
independent grader agents from round 4 on), plus one real field run:

| Round | New capability under test | Result (new vs old) |
|---|---|---|
| 1 | with-skill vs no-skill | **100% vs 69%** |
| 2 | operational rigor | **100% vs 70%** |
| 3 | autonomy / human gate / cost budget | **100% vs 67.5%** |
| 4 | mandatory interview / final stop-condition gate / orchestration | **97.5% vs 60%** |
| 5 | retro flywheel / shakedown / lite path | **97.5% vs 72.5%** |
| 6 | question banks / standards library / calibration | **90% vs 82.5%** (diminishing returns → pivot to usage layer) |

**Field evidence** (2026-07-06, legal-AI industry research loop): the VERIFIER sub-agent
genuinely rejected a "reprint posing as an independent cross-validation source" and forced
two more fixes — the maker/checker split earning its keep in the wild. The retro also
exposed a real design flaw (agents can't self-measure $ spend), now folded into doctrine
(hard caps use self-measurable quantities only). Trigger routing measured: 36/36 on a
12-skill panel, 7/8 in the full real environment (≥85% bar).

---

## Version highlights

| Version | Highlights |
|---|---|
| v1 | First release: five-beat loop + seven dimensions + two failure modes; 4-skill group; distilled from 6 references |
| v2 | Operational rigor: machine-checkable criteria, crash-safe idempotent resume, sized caps, glanceable status (benchmark v2 100% vs v1 70%) |
| v2.1 | Hardened per a "workflow-skill best practices" article: a `Rationalizations` table (closes the author's own shortcuts) + a Weak-vs-strong teaching contrast |
| v2.2 | Deliverable guardrail: using the group yields the paste-ready loop prompt itself, not the executed task (unless you explicitly ask) |
| v3.0 | Per cobusgreyling/loop-engineering: added a 5th skill **loop-ops** (operating layer) + folded autonomy levels (L1/L2/L3), human gate, cost budget, comprehension-debt into loop-engineering (benchmark v3 100% vs v2.2 67.5%) |
| v4.0 | Restructured per the user's skill-writing handbook: **mandatory interactive intake** (5-phase loop-spec), the **final stop-condition confirmation** gate, in-harness sub-agent orchestration (decomposer / plan-reviewer / verifier / doc-writer@haiku) + docs scaffolding + plan iteration with default auto-continue |
| v5.0 | 6th skill **loop-retro** (the flywheel: evidence diagnosis → revisions → real gotchas) + **shakedown protocol** (kill-test gates auto-continue) + **lite path** (3-question micro-interview for tiny tasks) |
| v6.0 | **Question banks / standards library** (6 task families) + **mid-run calibration** (golden-set drift detection; deterministic loops explicitly waived) |
| v7.0 | Usage layer + unknowns: **profile prefill** (ask once, ever), **blindspot pass / samples-first / reference-first** (four-quadrant elicitation), **Deviations protocol**, retro quiz, **retro→skill sedimentation channel** + **skill-craft** merged in (full skill-lifecycle methodology) |
| v7.1 | Closes the last cell of Shihipar's three-phase frame: **Final explainer** (DONE must ship a one-page EXPLAINER.md handoff; retro reads it against the artifacts) + **comprehension-quiz gate** (merge/ship-class output defaults to "merge only when you pass", waivers logged; report-class stays offer-only). Regression: 4 legacy cases zero regression, new core-2 1/3 → 3/3 |

---

## Repository structure

```
Build_Great_Loop/
├── README.md / README.en.md
├── LICENSE
├── loop-engineering/        # core: emits the loop prompt
│   ├── SKILL.md
│   ├── references/          # principles / patterns / harness-template / context-and-state / checklist
│   ├── assets/              # harness-skeleton.md (blank template)
│   └── evals/evals.json     # example eval set
├── loop-spec/               # interview → SPEC.md (assets/spec-template.md)
├── loop-eval/               # success criteria + evals + calibration protocol (golden-set drift detection)
├── loop-review/             # audit/harden an existing loop
├── loop-ops/                # operate recurring/unattended loops (scheduling · cost · safety · 7 patterns)
├── loop-retro/              # post-run retrospective: evidence → gotchas → sedimentation check
└── skill-craft/             # full skill lifecycle: create/modify/diagnose/merge/retire (pressure testing, templates, check-limits script)
```

---

## Updating

Re-run the install script above (`git clone` pulls the latest and overwrites the
same-named folders).

---

## FAQ

- **Is this the same as Claude Code's built-in `/loop`?** No. `/loop` re-runs one command on
  an interval; this skill group **designs the loop itself** — goal, state, verification, stop
  conditions — and its output is a prompt/harness.
- **Can I use just one of the skills?** Yes. All four trigger independently; just don't copy
  the folders you don't want.
- **What language is the generated prompt in?** It follows your conversation language; the
  skill internals are English (more reliable triggering, aligned with the source articles).
- **Can I use it in Cursor / other agents?** A skill is essentially knowledge-injection
  Markdown; any agent that can read `SKILL.md` can use it — adjust the install path to that
  tool's convention.

---

## Sources & credits

Method distilled from these official engineering articles:

- Anthropic — Effective harnesses for long-running agents / Effective context engineering for AI agents /
  Writing effective tools for AI agents / Demystifying evals for AI agents
- GitHub — Spec-driven development / Agentic primitives & context engineering / Continuous AI (agentic CI)
- Sourcegraph — Agentic Coding in 2026
- OpenAI — Codex best practices
- Skill-writing patterns: Qingfu, "How to write workflow Skills — patterns & best practices from 7 top Skills"

---

## License

MIT — see [LICENSE](LICENSE).
