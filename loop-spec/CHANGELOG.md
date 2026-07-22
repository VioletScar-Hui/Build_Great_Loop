# Changelog — loop-spec

## 4.1.0 — 2026-07-22

- Added authority-context intake for tenant, channel, principal, connector,
  memory namespace, and permission snapshot when state is shared or persistent.

## 4.0.0 — 2026-07-21

- Added host-neutral PROFILE intake precedence for sourced facts, visible
  preference prefills, labeled inferences, and user-owned decisions.
- Removed host-specific intake and helper-role requirements.

## 3.0.0 — 2026-07-21

- Made intake proportional to risk and lifespan; lite loops avoid ceremonial
  document sets and repeated confirmation.
- Clarified lifecycle handoff and visible reversible defaults.
- Removed stale historical result artifacts from the distributable candidate.

## 2.2 — 2026-07-17

- 修复：正文 4 处 "$数字" 字面量（$0.5 ×2、$0.3、$3）改写为 "x 美元 / USD" 形式。
  带参数调用 `/loop-spec` 时，斜杠命令的位置参数替换会把 `$0`/`$1`/`$3` 换成用户
  参数——本次实测 `$0.5` 被替换成了用户传入的 URL，损坏 lite 判据与 micro-interview
  的预算默认值（正是要展示给用户确认的数字）。
- 新增：文件头维护红线注释（正文禁止「美元符号+数字」）；frontmatter 增加 version 字段。
- evals 2.1 → 2.2：新增 gotcha-2（确定性 grep 检查，记录本次真实故障）。
  同日核查了 loop 家族其余 5 个 SKILL.md，均无同类字面量。
- 回归：core-1 4/4 通过（见 evals/iteration-3/），gotcha-2 grep 零命中。

## 2.1 — 2026-07-15（随套件 v7.2 发布）

- 嵌入 grilling 技巧两条增量：事实查环境不问用户（Profile & prefill 第 2 步）、
  依赖问题拆批（分支追问一次只问一个）。
- evals 2.0 → 2.1：新增 core-3（事实查找）、core-4（依赖拆批）。
  回归见 evals/iteration-2/（旧 5 用例零退步，core-4 由 1/3 → 3/3）。
