# Standards Library — proven machine-checkable patterns by task family

Phase 2's drafting source. Don't invent standards from scratch: pull the family's
patterns below, instantiate the `<...>`, then walk the user through each for
approval. Every standard keeps its check — a standard without a check command is
an opinion. Families match `question-banks.md`.

**How to compose a STANDARDS.md**: 2–4 acceptance standards + 1–2 quality-bar
standards + the red lines + one budget line. More than ~7 total usually means the
goal tree needs splitting instead.

---

## 1 · Batch processing

| Pattern | Standard template | Check template |
|---|---|---|
| 数量守恒 | 输出行数 == 输入条目数（或 == 成功数，失败已记录） | `wc -l out.csv` vs `ls in/ \| wc -l`；差值 == blocked 记录数 |
| 枚举成员 | 每行分类 ∈ 冻结的枚举集 | 脚本核对 category 列 ⊆ enum；违例行号列出 |
| 字段完备 | 关键字段非空且格式合法 | 正则/schema 校验，0 违例 |
| 抽检一致（校准锚） | 抽 <k>% 与黄金集/人工判断一致率 ≥ <X>%（默认 5% ≥90%） | 校准增量执行（见 loop-eval 校准协议） |
| 幂等无重 | 幂等键无重复 | `sort keys \| uniq -d` 为空 |

**红线模式**: 输入目录只读；含 PII 条目按约定处理；枚举集跑中冻结。
**预算启发**: 单条成本实测 × 总量 × 1.3，上限取整。

## 2 · Build-until-green

| Pattern | Standard | Check |
|---|---|---|
| 测试全绿 | 测试命令退出 0，无 skip | `npm test` / `pytest` 退出码 + skip 计数为 0 |
| 测试未被动过 | tests/ 无改动 | `git diff --stat <base> -- tests/` 为空 |
| 静态干净 | lint/类型检查退出 0 | `npm run lint` / `tsc --noEmit` |
| 无回归 | 先前通过的测试仍全过 | 全量套件而非单测 |
| 接口稳定 | 公共接口签名未变（若约定） | API diff 工具或导出清单比对 |

**红线**: 绝不改/删/skip 测试；不加未批准依赖。
**预算启发**: 每失败测试 ≈ 1 增量；上限 = 失败数 × 2。

## 3 · Research

| Pattern | Standard | Check |
|---|---|---|
| 来源门槛 | ≥<N> 个真实抓取来源，含 URL+访问日期 | 清点 sources 清单；无 URL 的不算 |
| 关键结论多源 | 每条关键结论 ≥<K> 独立来源 | 结论→来源映射表逐条核对 |
| 无源不落笔 | 每条事实性陈述可溯源 | 抽查 <k> 条陈述均有引注 |
| 时效 | 来源日期 ≤<M> 个月（或显式标注） | 日期字段核对 |
| 缺口显式 | 查不到的问题列入 open questions 而非留白 | 缺口清单存在且用户可见 |

**红线**: 绝不编造来源/URL/数字；付费墙内容不臆测。
**预算启发**: 每来源 1 增量；上限 = 目标来源数 × 1.5。

## 4 · Debug

| Pattern | Standard | Check |
|---|---|---|
| 统计化修复 | 修复后连续 <N> 次全绿（默认 20） | 循环跑 N 次记录退出码 |
| 根因陈述 | RETRO/日志中有可复述的根因（哪行、为什么、为何间歇） | 人读一遍能复述 |
| 复现留档 | 复现脚本入库，修复前能触发、修复后不能 | 跑复现脚本前后对比 |
| 单变量 | 每增量只动一个假设的最小改动 | diff 范围核对 |

**红线**: 测试只读；不许靠加 sleep/重试掩盖；插桩事后清理。

## 5 · Migration

| Pattern | Standard | Check |
|---|---|---|
| 不漏 | 目标条目数 == 源条目数（扣除记录在案的排除项） | 两端 count + 排除清单对账 |
| 不重 | 幂等键在目标端唯一 | 目标端 `GROUP BY key HAVING count>1` 为空 |
| 字段保真 | 抽 <k>% 做字段级比对全等（或哈希比对） | 抽样脚本 0 差异 |
| 可回滚 | 目标端可整批撤销且演练过 | 回滚演练一次成功 |

**红线**: 源端只读；不越窗口不超速率。
**预算启发**: 试跑 100 条实测单价再放量。

## 6 · Recurring ops

规格层标准同上按族取；运营层标准（cadence/预算/denylist/告警）由 **loop-ops**
的 readiness checklist 承接——不要在 STANDARDS.md 里重复一份。

---

## Anti-patterns（评审标准草案时自查）

- "尽量/较好/合理" 出现在标准里 → 打回，换成阈值。
- 标准只有数量没有质量锚（批处理最常见）→ 补抽检一致模式。
- 每条标准都从未失败的可能 → 阈值可能定得毫无约束力，在复盘时验证。
- 红线写成了愿望（"注意安全"）→ 写成可判定动作（"不写 in/ 目录任何文件"）。
