---
name: skill-craft
version: "1.1"
description: >
  按《Skill 完整实操指南》执行 skill 全生命周期操作，覆盖：创建、修改加固、
  测试验证、触发/执行诊断、description 与评测优化、合并拆分、删除退役。当用户要
  创建/写一个 skill、改/优化/加固 skill、测一测/验证 skill 好不好用、看看 skill
  为什么没触发或误触发、给 skill 写 description 或评测、合并/拆分/删除/退役
  skill 时调用 —— trigger on creating, writing, editing, improving, testing,
  verifying, reviewing, debugging, merging, splitting, deleting, or retiring any
  Claude/agent skill (SKILL.md), incl. description optimization and evals.
  本 skill 是 skill 工程的唯一方法论前门（writing-skills 已并入；跑基准/评测
  查看器/打包时调用 skill-creator 的脚本机器）。不适用于：调用某个已有 skill
  去完成它的业务任务；撰写 loop/harness 提示词本身（用 loop-engineering 组）。
---

# Skill Craft — Skill 全生命周期操作

依据《Skill 完整实操指南》对 skill 做创建、修改、审查、合并、退役。本文件只做
**路由**；方法细节全部在 `references/`（渐进式披露——这正是指南的要求，本 skill
以身作则）。

> 用**用户的语言**交流与产出；本 skill 的方法论内核是中文的，保持中文。

## 意图路由表

| 用户想做什么 | Task | 按需加载 |
|---|---|---|
| "帮我写/创建一个 skill" | A 创建 | decide-and-design → writing → templates → evals → launch-checklist |
| "改/优化/加固这个 skill" | B 修改 | evals（回归先行）→ writing → lifecycle（版本） |
| "为什么没触发/误触发/不按步骤走" | C 诊断 | troubleshooting → writing §L1 |
| "这两个 skill 要不要合并 / 这个太大了拆一下" | D 合并/拆分 | lifecycle → decide-and-design §粒度 |
| "这个 skill 没人用了/过时了，删了吧" | E 退役 | lifecycle §退役 |

## Task A：创建

**输入**：用户的场景描述（最好有 3–5 个真实 case）。**产出**：完整 skill 目录
（SKILL.md + 按需 references/scripts/examples + evals/evals.json）。
**沉淀通道入口**：请求来自 loop-retro 的沉淀提案时，三判据证据已现成（重复=会
再跑、跑偏=retro findings、交付物=harness 产出），素材即 harness/SPEC/gotchas——
直接从第 2 步开始；薄壳 skill（description + 指向 LOOP-PROMPT 的一页路由）常已足够。

1. **三判据闸门**（`references/decide-and-design.md` §1）：重复出现≥3次 / 每次跑偏
   或要重复解释 / 有可验收交付物。**任一不满足 → 明确劝退，不写**。没有真实 case
   就先让用户裸跑收集，Baseline 先行。过闸后固定问一句**参考物**："有没有现成的
   好例子——满意的产出/喜欢的同类 skill/类似实现？"（一个参考物顶几百字需求描述，
   直接读原件反推规范）；用户对该领域不熟时，先做一轮**盲点扫描**（列出这类 skill
   的经典坑与行家问题）再进设计。
2. 选骨架（4 选 1）+ 叠加工作流模式（6+1），走 §2 的两棵决策树。
3. **评测先行**：先写 `evals/evals.json`（core/edge/gotcha 三类，见
   `references/evals.md`）；**纪律型 skill 另加压力场景基线**（先裸跑记录借口
   原话，见 `references/pressure-testing.md`），再写"让评测通过的最小 skill"。
4. 按 `references/templates.md` 对应模板填空；正文写法遵守
   `references/writing.md`（祈使句、为什么、检查点、防偷懒四武器）。
5. 交付前过 `references/launch-checklist.md` 全表（Description 四原则 + 20 问测试
   + 反模式 11 条 + 四维自测），**任一红项不交付**。

**检查点**（可直接运行）：`python scripts/check-limits.py <skill目录>` → 预期
`"status": "ok"`（core≥5 / description≤1024 / 正文≤500 行 全部达标才 ok）。

## Task B：修改

**铁规**：改动之前先确认 evals 存在（没有就先按 Task A 第 3 步补建），改动之后
**必须回归**——在 `evals/iteration-N+1/` 重跑、不覆盖旧结果、对比通过率（目标问题
改善 + 其他用例无退步）。版本号按 `references/lifecycle.md` §版本控制升级，改动
原因记入 CHANGELOG。遇到的每个真实失败**追加为 gotcha 用例，而不是重写 skill**。

**检查点**：iteration-N+1 结果落盘且无回归；版本号已升。

## Task C：诊断

按 `references/troubleshooting.md` 的排查顺序走（70% 的问题在前两步：加载了吗、
description 对得上用户原话吗）。触发类问题优先动 description（补触发词/加排除
边界）；执行类问题定位跑偏的那一步（加祈使句/借口反驳表/负面指令/为什么）；
多 skill 抢单按"给其中一方加排除说明"处理。修完按 Task B 回归。

## Task D：合并 / 拆分

按 `references/decide-and-design.md` §2.3 粒度信号 判断：正文超 300/500 行、多个
独立工作流、改动频率差异大 → 拆（主 SKILL.md 只留路由表）；两个 skill 触发准确率都 <80% 且
description 语义重叠 → 先试排除边界，仍打架再合并（保留更清晰的那个）。合并/拆分
后 evals 两边都要迁移并回归。

## Task E：退役

对照 `references/lifecycle.md` §退役信号（模型原生已覆盖 / 维护成本超收益 / 场景
已消失 / 与新 skill 大量重叠）。**默认归档而非直接删除**（移出 skills 目录保留
副本），删除前向用户复述该 skill 现状并确认。退役不是失败——是清理路由噪声、
省上下文税。

## 全局安全红线（所有 Task 适用）

1. **没过三判据不写 skill**——写出来就是路由噪声，负收益。
2. **无回归不改 skill**——改了 A 坏了 B 是最常见事故。
3. **不删未归档的 skill**；删除/覆盖第三方 skill 前必须用户确认。
4. **description ≤1024 字符**，必含触发词与排除边界；正文 ≤500 行，超了下沉。
5. **gotcha 只记真实发生过的失败**，不猜。
6. 本 skill 产出的是 skill 工件本身；除非用户明确要求，不代跑目标 skill 的业务。

## 借口反驳表

| 可能的偷懒 | 为什么不行 |
|---|---|
| "场景很清楚，跳过三判据直接写" | 三判据挡掉的是"万能助手 Skill"这种最常见的失败开局。两分钟自查，换一个不进坟场的 skill。 |
| "先写 skill，评测以后补" | 评测先行是写法顺序的根本：skill 是"让评测通过的最小实现"。后补的评测只会迁就已写的实现。 |
| "小改一行，不用跑回归" | 改了 A 坏了 B 恰恰都发生在"小改"上。iteration-N 对比就是为此存在的。 |
| "description 差不多就行" | Description 写好等于成功一半；20 问测试 <85% 的 skill 上线就是误触发制造机。 |
| "直接把这个没用的 skill 删了" | 先归档、先确认。删除不可逆，而"没用"的判断可能来自不完整的观察。 |

## References（引用契约：触发条件 → 预期产出 → 检查点）

| 文件 | 触发条件 | 预期产出 | 检查点 |
|---|---|---|---|
| `references/decide-and-design.md` | Task A 起步 / Task D 粒度判断 | 三判据结论 + 骨架与模式选型（各带理由） | 三判据表已填且全勾才继续 |
| `references/writing.md` | 写/改 description 或正文时 | 符合四原则的 description + 六写法正文 | 20 问测试 ≥85%（新会话跑） |
| `references/templates.md` | 骨架选定后 | 按模板填空的 SKILL.md 初稿 | 无残留 `[...]` 占位符 |
| `references/evals.md` | Task A 第 3 步 / Task B 改前 | evals/evals.json（core/edge/gotcha） | `python scripts/check-limits.py` → core≥5 |
| `references/launch-checklist.md` | 交付前 | 全表勾选记录 | 任一红项不交付 |
| `references/troubleshooting.md` | Task C | 定位到的故障层 + 修复动作 | 修后按 Task B 回归 |
| `references/pressure-testing.md` | 纪律型 skill 的测试/加固；写改 description 时 | 压力场景基线（借口原话）+ 防弹三件套；CSO 合规的 description | 纪律型：最大压力下仍守规；description 无工作流摘要 |
| `references/lifecycle.md` | Task B 版本 / Task D/E | 版本号变更 / 合并方案 / 退役流程记录 | 归档副本存在才可删 |

## Scripts & Examples

- `scripts/check-limits.py` — 确定性核对（description 字数 / 正文行数 / core 用例
  数），输出 JSON。数数的事不让 LLM 干。
- `examples/weekly-report-standard/` — 用本方法论产出的完整小示例（骨架 C 规范型
  skill + evals），写新 skill 时对照它的完成形态。
