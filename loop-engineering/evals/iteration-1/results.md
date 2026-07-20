# loop-engineering 回归 — iteration-1（v4.1，2026-07-17）

改动背景：吸收 AI code migration 文章 5 个机制（见 CHANGELOG 4.1）。
跑 core-1 验证旧断言无退步 + 新断言 a6 生效。

## core-1（签核 spec → 产出 harness）— PASS 5/5

跑法：子代理读 SKILL.md + references 后模拟交付（500 工单分类，停止条件已确认）。

| 断言 | 判定 | 证据 |
|---|---|---|
| a1 四子代理角色，doc-writer@haiku | ✅ | DECOMPOSER / PLAN-REVIEWER / VERIFIER / DOC-WRITER(haiku) |
| a2 首步校验/创建 ./loop-docs/ | ✅ | 首次动作 #1，缺失由 DOC-WRITER 补建 |
| a3 计划迭代 ≤2 轮默认自动续跑 | ✅ | "至多 2 轮 → 默认自动继续（访谈已买断逐轮审批）" |
| a4 核心保留 | ✅ | 机器可检标准×4 / derive-from-disk + 原子追加 / 一批一增量 / 100 增量硬上限（美元作操作者对照，符合 2026-07-06 教训）/ 状态行 |
| a6（新）系统性失败升级 | ✅ | 护栏："同类失败 ≥3 单 → 修订 RULEBOOK 并重新生成受影响工单，绝不手工改旧输出" |

v4.1 新机制在产出中的落点（全部出现，且用得有判断）：
- RULEBOOK 层：STANDARDS 冻结 / RULEBOOK 运行中生长，复盘收割。
- 规则压测：Shakedown 第 4 步，3 个代表工单双做 + diff，产物明确丢弃。
- 对抗双 VERIFIER + 模型分层：**只**在校准与终检启用双评审（预算下的
  火力集中——正确的裁量而非机械照抄），fan-out 允许小模型，规则裁定权在 VERIFIER。
- Derive, don't track：队列 = 500 − results − skipped，"完成 = 输出行存在且过检"；
  attempts.json 只记磁盘看不出的尝试数。
- 交付说明含 flywheel 行。

## 未跑

core-2 / edge-1 / edge-2 / gotcha-1：门控逻辑（访谈前置、终问）未被本次改动
触及，判定低风险跳过。下次触及工作流门控时应全量跑。
