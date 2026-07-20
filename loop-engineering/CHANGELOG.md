# Changelog — loop-engineering

## 4.1 — 2026-07-17

吸收 Anthropic《AI-driven code migration》（claude.com/blog/ai-code-migration，
Bun 1M 行 Zig→Rust + Mike Krieger Python→TS 迁移）的 5 个实战机制：

1. **Rulebook 分层 + 系统性失败升级**（SKILL.md output contract、quality bar、
   借口反驳表；harness-template / skeleton 的 Docs 与 Guardrails）：STANDARDS
   人签核锁死，RULEBOOK.md 为 loop 自有战术规则、运行中生长；同类失败 ≥3 次
   → 修规则 + 重新生成受影响批次，绝不逐个手补（"fix the process, not the code"）。
2. **规则压测**（shakedown 扩充，SKILL.md + 两份模板）：批量任务（≥50 条目）
   开跑前用 2–3 个代表性条目做"按规则 vs 无约束"双做 + diff，修订 RULEBOOK 后
   **丢弃产物**——买的是规则修正，不是进度。
3. **对抗式双评审 + 按角色分配模型**（sub-agent roles，SKILL.md + 两份模板 +
   checklist）：高风险/大批量时两个独立上下文 VERIFIER、分歧升级第三个；最大
   模型给 verifier/plan-reviewer/写规则者，fan-out 用小模型。
4. **Derive, don't track**（operational rigor #2、context-and-state.md、
   checklist、两份模板）：有产出工件的条目，队列每次启动从磁盘重建（done =
   输出文件存在且过检），账本只记磁盘看不出的东西；自写队列（验证输出直接
   生成任务项）。
5. **按成本放置校验 + loop 流水线**（operational rigor #6；patterns.md 新增
   模式 8 "Pipeline of loops (phase-gated)"，含 build-daemon 序列化）。

其他：principles.md §9 增加来源条目；operational rigor 引言 "Four upgrades" 改为
中性表述（原文即已列 5 项，本次增至 6 项）。

evals 4.0 → 4.1：core-1 新增断言 a6（系统性失败升级路径）。
