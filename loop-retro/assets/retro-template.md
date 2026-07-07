# RETRO — <loop name> · run of <date>

> Evidence-cited post-run retrospective. Proposals only — ratified docs and the
> harness are edited by humans (or on explicit instruction afterwards).

## Summary (3 lines max)
<What ran, headline outcome, the one thing to fix first.>

## Vitals
| Metric | Value | Source |
|---|---|---|
| Increments attempted / completed / failed | | <log lines> |
| Max retries on one item | | |
| Human-gate hits (and outcomes) | | |
| Budget burned vs. cap | | |
| Verifier verdicts (pass/fail counts) | | |
| Resume events (clean?) | | |

## Findings (each with evidence)
### F1 — <failure class>: <one line>
- **Evidence:** `<quoted log line(s)>`
- **Impact:** <what it cost>

## Flywheel triad

### 1. Harness revision proposals
| # | For finding | Current (quote) | Proposed replacement |
|---|---|---|---|
| H1 | F1 | `<line>` | `<line>` |

### 2. Gotcha eval cases (appended to loop-docs/gotchas.json)
```json
{ "id": "gotcha-<n>", "category": "gotcha",
  "note": "<the real failure, one line>",
  "prompt": "<input reproducing the situation>",
  "assertions": [ { "id": "g1", "text": "没有重复<observed failure>" } ] }
```

### 3. SPEC/STANDARDS revision proposals — 需人工签核
| # | Doc | Current | Proposed | Why |
|---|---|---|---|---|
| S1 | STANDARDS.md | | | |

## Non-failure signals
<Standards that never failed · gates never hit · cost per increment vs. expected ·
cap sizing — anything miscalibrated even though nothing "broke".>

## Sedimentation check（retro → skill）
三判据：会重复？<✓/✗ 证据> · 有跑偏风险？<✓/✗> · 有可验收交付物？<✓/✗>
→ <过判：沉淀提案（薄壳 skill 名 + 素材=harness/SPEC/gotchas，交 skill-craft
Task A）/ 不过判：明说跳过，单次工作不沉淀>

## Decision list for the human
- [ ] Apply H1..Hn to the harness? (say the word and they get applied)
- [ ] Ratify S1..Sn?
- [ ] Keep gotcha cases as written?
