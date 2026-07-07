# STANDARDS — <task name>

> Machine-checkable standards approved by the user in Phase 2. Every loop
> iteration verifies against these; the loop may never weaken them — only a human
> edits this file.

## Acceptance standards (done = all pass)
| # | Standard | How to check (command / observation) | Approved |
|---|---|---|---|
| S1 | <e.g. summaries.csv 行数 == notes/ 下 .md 数量> | `<command>` | ✅ |
| S2 | <每条 summary 非空且 ≤50 字> | `<command>` | ✅ |

## Quality bar (per-increment)
| # | Standard | Check |
|---|---|---|
| Q1 | <e.g. 每个增量提交前测试退出 0> | `<command>` |

## Red lines (violating any = stop immediately, human gate)
- R1: <e.g. 不许改动 tests/ 下任何文件>
- R2: <…>

## Budget class
- Per run: <max increments AND max tokens/$> · Rationale: <why this size>
