# Changelog

本项目的版本演进记录。Newest first.

## v3.0 - Loop Ops + Autonomy / Human Gate / Cost Budget

参照 **Cobus Greyling 的 loop-engineering 仓库**（github.com/cobusgreyling/loop-engineering）
做的一轮扩展——把「运营周期性/无人值守循环」这一层补齐。

### Added
- 第 5 个 skill **`loop-ops`** —— 运营层：调度与节奏、五积木 + 记忆、**L1→L2→L3 分级放权**、
  maker/checker + **human gate**、**成本/token 预算 + 运行日志**、denylist / auto-merge 闸门 /
  MCP 权限 / 多循环协调 / failure modes / kill 开关、就绪检查表，以及 7 个真实周期模式
  （PR babysitter、daily triage、CI sweeper、dependency sweeper、changelog drafter、
  post-merge cleanup、issue triage）。含 `ops-plan` / `STATE` / `run-log` 模板。
- `loop-engineering` 融入四个概念（写进 `harness-template` / `principles` / `checklist`，
  产出的提示词与 `loop-review` 审查同步生效）：**自治级别 L1/L2/L3**（新循环默认 L1）、
  **human gate**（高危/不可逆/模糊 → 带完整上下文升级）、**成本/token 预算**（硬上限不再只是
  计数）、**comprehension-debt** 警示（循环放大判断力，好坏都放大）。

### Changed
- 基准（iteration-3，v3 vs v2.2 快照，更高的断言）：**100% vs 67.5%（+32.5 分）**，代价
  +10.6s / +1.5k tokens。提升集中在 自治级别 / 成本预算（v2.2 各 0/5）+ human gate（v2.2 2/5，
  只在任务「明喊风险」时才有）；核心 5 项两边都过，**无退化**。

## v2.2 - Deliverable Guardrail: emit the prompt, not the executed task

### Changed
- `loop-engineering` 明确交付边界：用本 skill 时，产出是**可直接粘贴的 loop 提示词本体**，
  不是替用户把任务做掉（写文章、建应用、跑研究）。`SKILL.md` 的「Your job」段写清这点，
  Rationalizations 表新增一条护栏（"Fastest way to help is to just build the thing they
  described" → 只交付提示词，除非用户明确说"跑一遍/执行"），并标为最常见的跑偏、重点防。

## v2.1 - Workflow-Skill Best-Practice Hardening

参照《工作流的 Skill 怎么写？从 7 个顶级 Skill 中提炼的模式与最佳实践》对设计做的加固。

### Added
- `loop-engineering/SKILL.md` 新增 **`Rationalizations to refuse`** 反驳表 —— 预判并堵住
  *撰写者自己* 的偷懒路径（「描述够细了，跳过 spec」「循环简单，不用硬上限」「只讲思路不写
  提示词」等），每条都给出为什么错。灵感来自 TDD / audit 等顶级 skill 的「借口反驳表」模式。
- `loop-engineering/references/harness-template.md` 新增 **Weak-vs-strong contrast** ——
  先给一个「看似完整、实则全是坑」的弱提示词，逐条点破缺了哪六样，再引出强模板（对比教学）。

### Changed
- 明确 **跳过** 了非标准 frontmatter 字段（`best_for` / `scenarios` / `estimated_time` /
  `references`）—— 加载器并不读取它们，加进去只是噪音。`name` + `description` 才决定加载。

## v2.0 - Operational Rigor and the v2-vs-v1 Benchmark

把「结构合格」抬到「真正顶级」的一轮迭代。

### Added
- loop-engineering 新增 **四条操作级严谨度**：成功标准 **机器可检**；**崩溃安全 + 幂等续跑**
  （claim-before-act / 原子记录）；**按任务规模设上限** 并说明理由；给运维者一行 **可一眼扫到
  的状态**。
- `references/context-and-state.md` 增补 `Crash-safety & idempotent resume` 小节；
  `references/checklist.md` 增补 机器可检 / 崩溃安全 / 上限定量 / 可运维 等审计项。

### Changed
- 基准评测（v2 vs v1，更高的质量断言）：**100% vs 70%（+30 分）**，代价约 +18s / +2k tokens。
  提升集中在 **上限设定 / 崩溃安全 / 可运维状态** —— 基线在「隐含要求」下最常漏掉的三处。

## v1.0 - First Release: The 4-Skill Loop Engineering Group

### Added
- 四个可组合技能：`loop-spec`（intake → `SPEC.md`）、`loop-engineering`（产出循环提示词）、
  `loop-eval`（成功标准 + 评测）、`loop-review`（审计 / 加固已有循环）。
- `loop-engineering` 参考文档：`principles` / `patterns` / `harness-template` /
  `context-and-state` / `checklist`；模板资源 `assets/harness-skeleton.md`；示例 `evals/evals.json`。
- 核心方法：**五拍循环**（Orient → Plan → Act → Verify → Record）、**七个设计维度**、
  **两大失败模式**（over-ambition 贪多 / false completion 虚假完成）。
- 方法蒸馏自 Anthropic / GitHub / Sourcegraph / OpenAI 的官方工程文章。
- Round-1 benchmark（with-skill vs no-skill，8 条结构性断言）：**100% vs 69%**。
