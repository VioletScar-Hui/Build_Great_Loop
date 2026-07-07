# Changelog

本项目的版本演进记录。Newest first.

## v7.1 - Final Explainer + 理解测验条件闸门

对照 Thariq Shihipar 三段框架（Before/During/After implementation）查缺：8 要素中
7 个已落地，补齐最后一格「Pitches & explainers + Quizzes (merge only when you pass)」。

### Added
- **Final explainer**（harness 模板 + skeleton，DONE 交付件）：停在 DONE 之前必须
  写一页 EXPLAINER.md——①做了什么/在哪 ②怎么跑/用/验证 ③关键决策 + Deviations
  摘要 ④最可能先坏在哪。只写已验证的声明（是交接稿不是宣传稿）——未读的产出
  就是理解债。
- **loop-retro 证据采集**新增 EXPLAINER.md 对照读取：声明与工件不符 = 发现
  （虚假完成气味）；DONE 却没有 explainer 本身 = 发现（交付线缺失）。
- **理解测验条件闸门**（loop-retro Step 4 + exit conditions + RETRO 模板）：
  merge/ship 类产出（要合并/上线/发布）测验**默认是闸门**——决策清单之前执行，
  不过或跳过则清单以「merge NOT recommended」开头；显式豁免须记录在 RETRO.md
  （记录在案的豁免是决策，静默跳过是理解债）。报告/研究类维持"提议不强制"。
- loop-retro evals 新增 core-2（merge 类测验闸门），版本 1.0 → 1.1。

### Changed
- 回归（evals/iteration-1，runner + 对抗评分，新旧快照各跑 5 用例）：旧 4 用例
  （core-1/edge-1/edge-2/gotcha-1）新旧全部满分持平——**零退步**；新增 core-2
  旧版 1/3（c1 默认执行、c3 不过不建议合并正是缺口）→ 新版 3/3。

## v7.0 - Usage Layer + Unknowns + skill-craft 并入

使用层优化（第一性原理评审驱动）+ Thariq Shihipar《Finding Your Unknowns》应用 + skill 部分入仓。

### Added
- **skill-craft**（新目录）：按《Skill 完整实操指南》的 skill 全生命周期方法论前门——创建
  （三判据闸门/评测先行）、修改（回归+版本控制）、诊断（故障树）、合并拆分、删除退役（先归档）；
  含压力测试法（吸收自 writing-skills）、四模板、check-limits.py 脚本、示例与 evals。
- **画像预填**（loop-spec）：`~/.claude/loop-profile.md` 机制——答过的问题变确认、上下文可推断的
  标「推断」预填；信息只问一次。
- **未知项四象限引出法**（loop-spec references/unknowns-elicitation.md）：盲点扫描（不熟领域先列
  行家陷阱）、样例先行（质量模糊先出 2-4 版微样例）、参考物优先（问题库全族通用问题 U1）。
- **Deviations 协议**（harness）：计划外偏离三路分诊——动摇 SPEC → human gate；无风险偏离 →
  保守选择 + 记录 + 继续；retro 把 Deviations 当头等证据。
- **retro→skill 沉淀通道**：loop-retro 新增三判据沉淀判定，过判则连同 harness/SPEC/gotchas 交
  skill-craft Task A；复盘可选「理解测验」对抗理解债。
- 交付备注固定飞轮入口：「跑完后说『复盘』」。

### Changed
- 硬上限教义修正（真实运行实证）：只用循环**可自测**的量（增量/工具调用数）；$ 预算降级为
  操作者事后核对参考——agent 无法观测自身花费。

## v6.0 - Question Banks + Standards Library + Mid-run Calibration

### Added
- loop-spec `references/question-banks.md`（6 任务族载荷问题，floor-not-ceiling）+
  `standards-library.md`（各族机器可检标准模式 + 反模式自查），接入 Phase 1/2。
- 循环内校准（loop-eval Part 6 + harness Calibration 区块）：黄金集（K≥10 或 2%）、节奏带定量
  理由（默认每 25 或 10% 取小）、漂移破限=暂停+human gate+不许放水；确定性任务显式豁免。

### Changed
- 基准 iteration-6（对抗评分）：v6 90% vs v5 82.5%——六轮最小差距，撰写层收益递减实锤，
  转向使用层优化。评分员抓出 4 处缺陷已修（分轮规则全阶段化、流程去向脚注、轻量默认值数字化、
  skeleton 补 STATUS 行区块）。

## v5.0 - Retro Flywheel + Shakedown + Lite Path

### Added
- 第 6 个 skill **loop-retro**：证据引证复盘 → vitals → 8 类失败分类 → 三件套（harness
  before→after 修订、真实失败 gotcha、需签核标准提案）；铁律「只提案不擅改、只记真实失败」。
- **摇测协议**：自动续跑锁定，直至 监督首增量 + 故意 kill/续跑核验（用户执行）+ verifier
  开工核验 通过并记录 SHAKEDOWN PASSED。
- **轻量通道**：四判据（<20 增量/无不可逆/<$0.5/仅工作区写）全满足且用户确认 → 3 问微访谈 +
  内联 spec；单向棘轮升级；永不豁免 状态/上限/kill 测试/停止条件终问。

### Changed
- 基准 iteration-5：v5 97.5% vs v4 72.5%；复盘场景 8/8 vs 4/8；防逃生门卫兵通过。

## v4.0 - Mandatory Interview + Final Stop-condition Gate + Orchestrated Harness

### Added
- **loop-spec 重写为强制交互访谈**（铁律：不访谈不出规格、不回答不假设）：框架确认 → 澄清+
  头脑风暴 → 标准制定 → 目标树（叶=一增量可验收）→ doc-writer(haiku) 落盘四文档签核。
- **停止条件终问**：loop-engineering 交付前必须让用户最终确认停止条件，不确认不交付。
- harness 内置**子代理编排**（DECOMPOSER/PLAN-REVIEWER/VERIFIER/DOC-WRITER@haiku，动态派生 +
  可选 .claude/agents/ 持久化）+ ./loop-docs/ 脚手架 + 计划迭代（≤2 轮评审后默认自动续跑——
  访谈签核即授权）。

### Changed
- 基准 iteration-4（对抗评分 agent 首次启用）：v4 97.5% vs v3 60%；模糊需求场景 v3 直接猜着
  交付（0/8）、v4 守闸访谈（8/8）。

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
