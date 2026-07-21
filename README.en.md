# Build Great Loop · Composable Agent Loop Skills

[中文](README.md) | [English](README.en.md)

![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827)
![Claude Compatible](https://img.shields.io/badge/Claude-Compatible-6B46C1)
![Loop Skills](https://img.shields.io/badge/Loop%20Skills-6-0E7490)
![Component Tests](https://img.shields.io/badge/Component%20Tests-38%2F38-success)
![License](https://img.shields.io/github/license/VioletScar-Hui/Build_Great_Loop)

A Loop Engineering skill suite for both Codex and Claude Code. It turns an unsettled goal into an executable, resumable, verifiable agent loop, then supports evaluation, review, operation, and post-run learning.

This release synchronizes both hosts from one canonical source. The six formal loop-skill directories are byte-identical across Codex and Claude.

## Highlights

- Six-skill lifecycle: `spec → engineering → eval → review → ops → retro`.
- CORE stays small; optional components appear only when their triggers are present.
- `PROFILE` reads task-relevant stable preferences and discoverable facts without treating inference as authorization.
- `RULES` revises tactical rules after repeated failure classes and revalidates affected work.
- `DEVIATIONS` persists material plan mismatches with evidence without expanding scope.
- `EXPLAIN` adds evidence-bound handoff and recorded comprehension or waiver before substantial merge/ship actions.
- Environment-first L3 containment, independent verification, crash recovery, and machine-checkable stop conditions.
- Host-neutral behavior: no mandatory fixed model, Claude agent path, `/loop`, Git, or proprietary question tool.

## Skills

| Skill | Current version | Responsibility |
|---|---:|---|
| `loop-spec` | 4.0.0 | Decide whether a loop is justified; settle goals, boundaries, risks, and success criteria |
| `loop-engineering` | 7.0.1 | Emit the smallest sufficient runnable harness; includes the component catalog and validators |
| `loop-eval` | 3.0.0 | Design success criteria, eval sets, and graders |
| `loop-review` | 4.0.0 | Audit an existing harness for missing, dead, triggerless, or unevidenced components |
| `loop-ops` | 3.0.1 | Operate recurring or unattended loops with budgets, permissions, and kill controls |
| `loop-retro` | 4.0.0 | Learn from real run artifacts and propose rule, standard, and harness revisions |
| `skill-craft` | Companion | Methodology for creating, modifying, diagnosing, merging, and retiring skills |

## Installation

Run these commands in a terminal. Use PowerShell on Windows and Terminal on macOS/Linux.

### macOS / Linux: install for both Codex and Claude

```bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git clone --depth 1 https://github.com/VioletScar-Hui/Build_Great_Loop.git "$tmp"
for dest in "$HOME/.codex/skills" "$HOME/.claude/skills"; do
  mkdir -p "$dest"
  for skill in loop-spec loop-engineering loop-eval loop-review loop-ops loop-retro skill-craft; do
    rsync -a --delete "$tmp/$skill/" "$dest/$skill/"
  done
done
```

### Windows PowerShell: install for both Codex and Claude

```powershell
$ErrorActionPreference = "Stop"
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("build-great-loop-" + [guid]::NewGuid())
try {
  git clone --depth 1 https://github.com/VioletScar-Hui/Build_Great_Loop.git $tmp
  if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
  $skills = "loop-spec","loop-engineering","loop-eval","loop-review","loop-ops","loop-retro","skill-craft"
  "$env:USERPROFILE\.codex\skills","$env:USERPROFILE\.claude\skills" | ForEach-Object {
    New-Item -ItemType Directory -Force $_ | Out-Null
    $dest = $_
    $skills | ForEach-Object {
      $target = Join-Path $dest $_
      if (Test-Path $target) { Remove-Item -Recurse -Force $target }
      Copy-Item -Recurse "$tmp\$_" $target
    }
  }
} finally {
  if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
}
```

Remove the destination for the host you do not use. Rerun the same command to update matching directories.

## Usage

Start a new session after installation and ask naturally:

```text
Turn this vague automation idea into a settled loop specification first.
```

```text
Write a resumable agent-loop harness that stops only after the tests pass.
```

```text
Audit this loop prompt for false completion, runaway retrying, and lost restart state.
```

```text
The loop finished. Retro it from the run log and state artifacts.
```

The suite routes automatically. You can also name `loop-spec`, `loop-engineering`, or another skill explicitly when your host supports it.

## Component model

`loop-engineering` starts with `CORE` and selects components proportionally:

| Trigger | Component |
|---|---|
| State must survive restart | `STATE` |
| Executable verification is required | `VERIFY` |
| High-risk or unattended boundary | `CONTAIN` |
| Quality can drift | `CALIBRATE` |
| Recovery must be rehearsed before launch | `SHAKEDOWN` |
| Independent work can fan out | `FANOUT` |
| Stable preferences or discoverable facts exist | `PROFILE` |
| A failure class repeats | `RULES` |
| Evidence shows a material plan mismatch | `DEVIATIONS` |
| A substantial merge/ship needs comprehension handoff | `EXPLAIN` |

See `loop-engineering/references/component-catalog.md` for complete triggers, dependencies, and acceptance rules.

## Verification

This synchronized release passes:

- Optional-component and adversarial effects: 38/38.
- Legacy behavior regression: 18/18.
- Cross-root sync-validator tests: 35/35.
- Suite-validator tests: 5/5.
- Paired model eval: candidate 31/33 versus previous baseline 27/33; the discriminating gains are explicit selection of the four new components.

Run from the repository root:

```bash
python3 loop-engineering/scripts/test_validate_suite.py
python3 loop-engineering/scripts/validate_suite.py .
python3 loop-engineering/scripts/run_component_fixtures.py
python3 loop-engineering/scripts/run_component_fixtures.py --legacy
python3 loop-engineering/scripts/select_components.py loop-engineering/evals/fixtures/simple.json
```

## Repository structure

```text
Build_Great_Loop/
├── loop-spec/
├── loop-engineering/
│   ├── assets/components/
│   ├── evals/fixtures/
│   ├── references/component-catalog.md
│   └── scripts/
├── loop-eval/
├── loop-review/
├── loop-ops/
├── loop-retro/
├── skill-craft/
├── README.md
├── README.en.md
└── CHANGELOG.md
```

## Changelog

- 2026-07: synchronized the six-skill canonical suite across hosts; added `PROFILE / RULES / DEVIATIONS / EXPLAIN`; hardened modular harnesses, environment containment, state schemas, validators, and adversarial fixtures; added normalized containment paths and cross-platform atomic quota reservations.
- See [CHANGELOG.md](CHANGELOG.md) and each skill's own `CHANGELOG.md` for details and historical releases.

## Sources and credits

The design draws on Anthropic's Agent Skills, long-running agent harness, context-engineering, evaluation, and containment practices, adapted into a host-neutral implementation for Codex and Claude.

## License

[MIT](LICENSE)
