# Question Banks — load-bearing questions by task family

The interview's floor, not its ceiling. In Phase 1, identify the task family,
pull its bank, and make sure every load-bearing question below is either
**answered by the user** or **visibly already answered** in what they said
(confirm, don't re-ask). Then add task-specific questions the bank can't know.
Batching rules still apply: 2–4 per round, options + a recommended default.

**全族通用问题（任何 family 都先问这条）**：

| # | Question | Why it's load-bearing | Options |
|---|---|---|---|
| U1 | 有没有现成的**参考物**——往期满意的产出 / 喜欢的样式或网站 / 实现了类似行为的代码？ | 一个好参考物顶几百字描述；直接读原件（源码优于截图）反推口径，用户只需确认差异点 | 有→给路径/链接（✦） / 没有→进常规问题轮 |

**Family selector** (maps to `../loop-engineering/references/patterns.md`):

| The task smells like… | Family |
|---|---|
| 逐条处理一堆东西（标注/清洗/转换/翻译） | 1 · Batch processing |
| 写代码直到测试/验收全过 | 2 · Build-until-green |
| 查资料、挖到有把握、出报告 | 3 · Research |
| 有个 bug/怪现象要锁根因 | 4 · Debug |
| 把数据从 A 搬到 B，绝不能重/漏 | 5 · Migration |
| 按周期反复跑、无人值守 | 6 · Recurring ops（问完基础后移交 loop-ops） |

---

## 1 · Batch processing

| # | Question | Why it's load-bearing | Typical options (✦ = default) |
|---|---|---|---|
| B1 | 单条失败怎么办？ | 决定 blocked 语义与数据完整性 | ✦跳过并记录 / 重试 N 次后跳过 / 停下等人 |
| B2 | 输出的消费者是谁——人读还是程序读？ | 决定格式的严格程度与 schema | ✦程序（严格 schema） / 人（可读优先） |
| B3 | 质量怎么抽检？比例和一致率线？ | 质量模糊型任务的校准锚点 | ✦5% 抽检 ≥90% 一致 / 10% / 不抽（仅确定性任务） |
| B4 | 分类体系/转换规则从哪来，跑中能改吗？ | 防中途改目标（silent drift） | ✦跑前冻结，缺项归 other / 允许人工中途增补 |
| B5 | 有没有敏感数据（PII）？红线是什么？ | 红线进 STANDARDS，违者进 human gate | ✦脱敏后处理 / 跳过含 PII 条目 / 无 PII |
| B6 | 总量多大？预算/时限接受到多少？ | 硬上限与分批大小的依据 | 按量估算，✦单次 run 上限 = 总量的 1/5 |

## 2 · Build-until-green

| # | Question | Why | Options |
|---|---|---|---|
| G1 | "绿"由什么定义——哪条命令退出 0？ | 唯一可机器核对的 done | ✦现有测试套件 / 先补验收测试再开工 |
| G2 | 测试文件本身能动吗？ | 防 reward hacking 的头号红线 | ✦绝不能动 / 仅可新增不可改删 |
| G3 | 依赖能加吗？现有公共接口能改吗？ | 决定改动半径 | ✦不加依赖不破接口 / 可加需记录 |
| G4 | 一个增量 = 一个接口还是一个失败测试？ | 增量粒度决定可验证性 | ✦一个失败测试 / 一个接口 |
| G5 | 分支/提交策略？ | 崩溃安全与回滚的载体 | ✦专用分支+每增量一 commit / 直接工作区 |

## 3 · Research

| # | Question | Why | Options |
|---|---|---|---|
| R1 | 来源门槛：数量下限？关键结论几个独立源？ | 决定"有把握"的客观定义 | ✦≥10 源、关键结论≥3 独立源 |
| R2 | 来源可信度怎么分级？哪类不算数？ | 防垃圾来源灌水 | ✦官方>权威媒体>论坛（需佐证） |
| R3 | 时效窗口——多旧的资料还可用？ | 过期数据是研究型任务最大暗坑 | ✦≤18 个月 / 不限但标注日期 |
| R4 | 查不到怎么办——标注缺口还是继续深挖？ | 决定 blocked 与收益递减语义 | ✦3 类来源无果即标缺口转下一题 |
| R5 | 产出形态与引用格式？ | 决定 done 的形状 | ✦report.md + 编号引用 + 无源不落笔 |

## 4 · Debug

| # | Question | Why | Options |
|---|---|---|---|
| D1 | 复现方式和频率？有确定性复现吗？ | 无复现即无验证 | ✦先建复现脚本再开工 |
| D2 | "修好"的标准——连续多少次全绿？ | 间歇性 bug 的 done 必须统计化 | ✦连续 20 次通过 / 100 次 |
| D3 | 能改测试吗？能加日志/插桩吗？ | 红线 + 手段边界 | ✦测试只读，插桩允许且事后清理 |
| D4 | 一次只验一个假设可以吗（会慢）？ | 单变量原则的用户预期管理 | ✦可以 / 允许并行假设（需隔离） |
| D5 | 修复半径——只修根因还是顺手重构？ | 防范围蔓延 | ✦只修根因，重构另开任务 |

## 5 · Migration

| # | Question | Why | Options |
|---|---|---|---|
| M1 | 幂等键是什么——重跑靠什么去重？ | 不重不漏的根基 | ✦业务主键 / 内容哈希 |
| M2 | 目标端可以先写后验吗，还是要事务？ | 决定原子记录的实现 | ✦写后验+对账 / 逐批事务 |
| M3 | 对账标准——数量之外还核对什么？ | 只对数量是迁移最常见假完成 | ✦行数+抽样字段级比对 / 全量哈希 |
| M4 | 源数据只读吗？回滚方案？ | 红线 + 事故预案 | ✦源只读，目标可整批回滚 |
| M5 | 窗口与速率限制？ | 硬上限依据（别打挂生产库） | 按环境定，✦夜间低峰+限速 |

## 6 · Recurring ops

先问 B/G 族适用的基础问题，再加：

| # | Question | Why | Options |
|---|---|---|---|
| O1 | 节奏多密？错过一轮要紧吗？ | cadence 与告警语义 | 按任务定 |
| O2 | 起步自治级别接受 L1 只报告吗？ | 分级放权的起点共识 | ✦L1 一周再升 |
| O3 | 绝不能自动做的动作清单？ | denylist 源头 | 必答，无默认 |
| O4 | 每天预算上限？ | 周期任务成本最易爆 | 必答 |

→ 答完移交 **loop-ops** 做运营方案；本 bank 只负责规格层。
