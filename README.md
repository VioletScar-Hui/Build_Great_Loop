# Build Great Loop · Loop Engineering Skills

[中文](README.md) | [English](README.en.md)

![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827)
![Claude Compatible](https://img.shields.io/badge/Claude-Compatible-6B46C1)
![Skills](https://img.shields.io/badge/Skills-6%20loop%20%2B%20skill--craft-0E7490)
![Benchmarked](https://img.shields.io/badge/Benchmark-6%20rounds%20adversarial-success)
![Component Tests](https://img.shields.io/badge/Component%20Tests-38%2F38-success)
![Field Tested](https://img.shields.io/badge/Field%20Tested-real%20run%202026--07-8B5CF6)
![Language](https://img.shields.io/badge/Language-ZH%20%2B%20EN-blue)
![License](https://img.shields.io/github/license/VioletScar-Hui/Build_Great_Loop)
![Status](https://img.shields.io/badge/Status-Active-success)

一个**可组合的「循环工程（Loop Engineering）」技能组**，同时支持 Codex 和 Claude Code。
当你需要让 AI **自己跑、跑到完成、中途被打断也能续上、还不假装做完**时，触发它——它会
访谈你的任务，然后产出一份**可直接粘贴的顶级循环提示词（harness）**。

> 模型是发动机，循环是发动机外面的整个底盘：它要朝目标走的方向、它记得住的状态、让它
> 诚实的验证、以及告诉它何时该停的规矩。这套技能把「老手才会下意识做的事」变成提示词里
> 的默认动作。

![Build Great Loop — 六技能工作流与 skill-craft 沉淀飞轮](assets/workflow.svg)

---

## 这是什么

`Build Great Loop` 不是一个单体技能，而是 **6 个各司其职、可独立触发、也能串起来用的正式 loop skill**，外加一个负责把经验沉淀为可复用资产的 `skill-craft` 伴侣：

| 技能 | 当前版本 | 作用 | 什么时候触发 |
|---|---:|---|---|
| **loop-spec** | 4.0.0 | 访谈式把模糊任务变成一份可执行的 `SPEC.md` | 任务还没想清、需要先定目标/成功标准/停止条件 |
| **loop-engineering**（核心） | 7.0.1 | 访谈 → 产出**可粘贴的循环提示词本体** | 「帮我写个能一直跑到完成的 agent / 循环 / harness」 |
| **loop-eval** | 3.0.0 | 设计成功标准 + 小评测集 + 评分器（pass@k vs pass^k） | 「怎么知道这循环靠不靠谱 / 给 agent 写评测」 |
| **loop-review** | 4.0.0 | 体检并加固一份**已有**的循环提示词 | 「我的 agent 老是停不下来 / 说完成了其实没有 / 重启丢进度」 |
| **loop-ops** | 3.0.1 | 把循环跑成周期性/无人值守的自动化（调度·成本·安全门·分级放权） | 「每天/每个 PR/每晚跑这个 agent」「无人值守怎么跑不出事」「babysit 我的 PR」「自动 triage issue」 |
| **loop-retro** | 4.0.0 | 跑完复盘：证据引证诊断 → harness 修订提案 + 真实失败 gotcha + 标准提案 + **沉淀判定** | 「loop 跑完了帮我复盘」「看看 run log 哪里出问题」「为什么超预算/thrash」 |
| **skill-craft** | 独立伴侣 | skill 全生命周期方法论前门：创建/修改/诊断/合并/退役（含三判据闸门、评测先行、压力测试法） | 「帮我写个 skill」「skill 为什么没触发」「这两个 skill 要不要合并」「把旧 skill 退役」 |

设计与最佳实践来自 Anthropic、GitHub、Sourcegraph、OpenAI 的官方工程文章（见[来源](#来源与致谢)）。

---

## 适用场景

- 自主编码 / build-until-green：逐个实现接口或功能，直到测试全过。
- 批量处理：通宵给上千条数据打标 / 清洗 / 翻译，可中断续跑。
- 自主研究：查权威资料、挖到有把握、带来源出报告。
- 调试循环：复现 → 假设 → 验证 → 修复，直到锁定根因。
- 数据迁移等「跑数小时、必被打断、绝不能重复或漏」的长任务。
- 以及——**给一份已有的循环提示词做体检**，告诉你它会在哪翻车、怎么修。

---

## 安装

### 最简单方式：让 AI Agent 按 URL 安装

直接对你的 Codex / Claude Code 说：

> 帮我安装这个 skill 组：`https://github.com/VioletScar-Hui/Build_Great_Loop`
> 把仓库里的 `loop-spec` / `loop-engineering` / `loop-eval` / `loop-review` /
> `loop-ops` / `loop-retro` / `skill-craft` 七个目录同步到 Codex 和 Claude 的
> skills 目录下，并验证两边一致。

> 以下命令**在终端中执行**（Windows 用 PowerShell，macOS/Linux 用 Terminal）。
> 可选搭档：skill-craft 的基准评测机器复用 Anthropic 的 `skill-creator`（本仓库
> 不含它，不装也不影响方法论使用）。

### macOS / Linux：同时同步到 Codex 与 Claude

```bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git clone --depth 1 https://github.com/VioletScar-Hui/Build_Great_Loop.git "$tmp"
for dest in "$HOME/.codex/skills" "$HOME/.claude/skills"; do
  mkdir -p "$dest"
  for skill in loop-spec loop-engineering loop-eval loop-review loop-ops loop-retro skill-craft; do
    rsync -a --delete "$tmp/$skill/" "$dest/$skill/"
  done
done
```

### Windows PowerShell：同时同步到 Codex 与 Claude

```powershell
$ErrorActionPreference = "Stop"
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("build-great-loop-" + [guid]::NewGuid())
try {
  git clone --depth 1 https://github.com/VioletScar-Hui/Build_Great_Loop.git $tmp
  if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
  $skills = "loop-spec","loop-engineering","loop-eval","loop-review","loop-ops","loop-retro","skill-craft"
  "$env:USERPROFILE\.codex\skills","$env:USERPROFILE\.claude\skills" | ForEach-Object {
    New-Item -ItemType Directory -Force $_ | Out-Null
    $dest = $_
    $skills | ForEach-Object {
      $target = Join-Path $dest $_
      if (Test-Path $target) { Remove-Item -Recurse -Force $target }
      Copy-Item -Recurse "$tmp\$_" $target
    }
  }
} finally {
  if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
}
```

如只使用一个宿主，删除另一条目标路径即可。更新时重新运行同一命令；它会以仓库内容为
canonical 源覆盖同名技能目录，避免两边逐渐漂移。

### 快速安装检查

```bash
for root in "$HOME/.codex/skills" "$HOME/.claude/skills"; do
  for skill in loop-spec loop-engineering loop-eval loop-review loop-ops loop-retro skill-craft; do
    test -f "$root/$skill/SKILL.md" && echo "OK  $root/$skill" || echo "MISSING  $root/$skill"
  done
done
```

十四行都是 `OK` 即两个宿主均安装成功；只安装一个宿主时应看到七行。

---

## 第一次成功运行

装好后，新开一个会话，直接用自然语言描述一个**需要反复跑**的任务，例如：

> 帮我写一个能可靠运行的循环：把 `notes/` 下每个 `.md` 生成一句话摘要、写进
> `summaries.csv`，要能中断后续跑、不重复、不漏。

`loop-engineering` 会被触发，先问你一两个关键问题（目标怎么算完成、什么时候该停），
然后产出一份**可直接粘贴**的循环提示词——含成功标准、停止条件（带硬上限）、五拍循环、
外置状态、崩溃安全续跑、验证与护栏、以及一行能让你一眼看健康度的状态。

---

## 工作流

六个正式 loop skill 可以单独用，也可以覆盖完整生命周期：

```
loop-spec ──► loop-engineering ──► loop-eval ──► loop-ops
  定目标          产出 harness          设计评测        安全运营
                     ▲                                  │
                     └──── loop-review                  ▼
                           审计/加固               loop-retro
                                                    证据复盘
                                                        │
                                                        ▼
                                                   skill-craft
                                                   沉淀复用资产
```

---

## 核心方法

![五拍循环 Orient → Plan → Act → Verify → Record](assets/five-beats.svg)

- **五拍循环**：`Orient`（先读状态）→ `Plan`（选一个最小增量）→ `Act`（只做这一个）→
  `Verify`（像用户那样真验）→ `Record`（写进耐久状态，保持干净可交接）。
- **七个设计维度**：目标与可验证的成功标准、停止条件、循环骨架、状态与记忆、上下文纪律、
  工具、验证与护栏。
- **两大失败模式**：贪多冒进（一口气做完→上下文爆）与虚假完成（没测就说做完）——每份产出
  都要点名防御这两个。
- **四条「操作级严谨度」**（把「合格」抬到「顶级」）：成功标准机器可检、崩溃安全 + 幂等续跑、
  按任务规模设上限、给运维者一行可一眼扫到的状态。
- **交互式访谈前置**（v4+）：强制需求澄清 → 标准制定 → 目标树拆解 → 文档签核；交付前必做
  **停止条件终问**；微任务走 3 问轻量通道（四判据全满足才可）。
- **画像预填 + 未知项四象限**（v7）：答过的问题不再问（`~/.claude/loop-profile.md`）；
  领域不熟先**盲点扫描**、质量目标模糊先**样例先行**、有参考物直接读原件。
- **摇测 + 校准 + Deviations**：自动续跑锁定直到通过 kill 测试；质量模糊型循环带黄金集
  校准增量防漂移；计划外偏离走「保守选择 + 记录 + 继续」协议。
- **复盘飞轮**（loop-retro）：真实失败 → gotcha 用例；跑得好的 loop → 三判据沉淀判定 →
  交 skill-craft 变成可复用 skill——一次性工作变复利资产。

详见 `loop-engineering/references/`（`principles` / `patterns` / `harness-template` /
`context-and-state` / `checklist`）。

### 组件模型

当前版本把 harness 拆成一个始终存在的 `CORE` 和按证据触发的可选组件。简单任务保持简单；
只有任务确实需要时才增加状态、隔离、校准或交接机制。

| 触发条件 | 组件 |
|---|---|
| 状态需要跨重启保存 | `STATE` |
| 需要可执行、独立的完成验证 | `VERIFY` |
| 高风险或无人值守边界 | `CONTAIN` |
| 主观质量可能随批次漂移 | `CALIBRATE` |
| 自动续跑前必须演练恢复 | `SHAKEDOWN` |
| 工作项可独立并行 | `FANOUT` |
| 存在稳定偏好或可发现的环境事实 | `PROFILE` |
| 同类失败反复出现 | `RULES` |
| 证据表明执行与计划发生实质偏离 | `DEVIATIONS` |
| 重大 merge/ship 需要理解交接 | `EXPLAIN` |

完整触发条件、依赖关系和验收规则见
[`component-catalog.md`](loop-engineering/references/component-catalog.md)。组件必须同时满足
“有触发证据、进入执行路径、留下可验证工件”；否则 loop-review 会把它判为缺失、空壳或死亡组件。

---

## 为什么相信它

不是凭感觉——六轮快照对照基准（第 4 轮起由对抗性评分 agent 逐条引证评分），外加一次真实
野外运行：

| 轮次 | 对比（新 vs 旧快照） | 结果 |
|---|---|---|
| 1 | 带技能 vs 裸跑 | **100% vs 69%** |
| 2 | 操作级严谨度 | **100% vs 70%** |
| 3 | 自治级别/human gate/成本预算 | **100% vs 67.5%** |
| 4 | 强制访谈/停止条件终问/子代理编排 | **97.5% vs 60%** |
| 5 | 复盘飞轮/摇测/轻量通道 | **97.5% vs 72.5%** |
| 6 | 问题库/标准库/校准 | **90% vs 82.5%**（收益递减，转向使用层优化） |

**野外实证**（2026-07-06，法律 AI 行业调研 loop）：VERIFIER 子代理真实拦下「转载源冒充
独立交叉验证源」并促成 2 处修正——maker/checker 分离值回成本；复盘同时发现「$ 预算
agent 无法自测」的设计缺陷并已修入教义（硬上限只用可自测量）。触发路由实测：12 技能
面板 36/36，全量真实环境 7/8（≥85% 达标线）。

**当前同步版本验证**（2026-07-22）：可选组件与对抗效果 38/38、旧功能回归 18/18、
跨目录同步验证器 35/35、suite validator 5/5。配对模型评测为候选 31/33、旧基线 27/33；
可区分增益集中在四个新增组件的显式选择，未把无区分度用例包装成收益。

在仓库根目录可复跑：

```bash
python3 loop-engineering/scripts/test_validate_suite.py
python3 loop-engineering/scripts/validate_suite.py .
python3 loop-engineering/scripts/run_component_fixtures.py
python3 loop-engineering/scripts/run_component_fixtures.py --legacy
python3 loop-engineering/scripts/select_components.py loop-engineering/evals/fixtures/simple.json
```

---

## 版本亮点

| 版本 | 要点 |
|---|---|
| v1 | 初版：五拍循环 + 七维度 + 两大失败模式；4 技能组合；6 篇参考资料蒸馏 |
| v2 | 操作级严谨度：机器可检标准、崩溃安全幂等续跑、按规模设上限、可一眼扫到的状态（评测 v2 100% vs v1 70%） |
| v2.1 | 参照「工作流 Skill 最佳实践」加固：`Rationalizations` 反驳表（堵住作者偷懒）+ Weak-vs-strong 对比教学 |
| v2.2 | 交付边界护栏：用本组时产出是「可粘贴的循环提示词本体」，不替你执行任务（除非你明确要求） |
| v3.0 | 参照 cobusgreyling/loop-engineering：新增第 5 个 skill **loop-ops**（运维层）+ 把 自治级别(L1/L2/L3)·human gate·成本预算·comprehension-debt 融进 loop-engineering（基准 v3 100% vs v2.2 67.5%） |
| v4.0 | 按《Skill 完整实操指南》重构：**强制交互访谈**（loop-spec 五阶段）、**停止条件终问**硬闸门、harness 内置子代理编排（decomposer/plan-reviewer/verifier/doc-writer@haiku）+ 文档脚手架 + 计划迭代默认自动续跑 |
| v5.0 | 新增第 6 个 skill **loop-retro**（复盘飞轮：证据诊断→修订提案→真实 gotcha）+ **摇测协议**（kill 测试通过才解锁自动续跑）+ **轻量通道**（四判据微任务 3 问微访谈） |
| v6.0 | **问题库/标准库**（6 任务族弹药）+ **循环内校准**（黄金集防漂移，确定性任务显式豁免） |
| v7.0 | 使用层 + 未知项：**画像预填**（信息只问一次）、**盲点扫描/样例先行/参考物优先**（四象限引出法）、**Deviations 协议**、复盘测验、**retro→skill 沉淀通道** + 并入 **skill-craft**（skill 全生命周期方法论，据《Skill 完整实操指南》） |
| v7.1 | 补齐 Shihipar 三段框架最后一格：**Final explainer**（DONE 必须产出一页 EXPLAINER.md 交接稿，retro 拿它对照工件）+ **理解测验条件闸门**（merge/ship 类产出默认「不过测验不建议合并」，豁免须记录；报告类维持提议制）。回归：旧 4 用例零退步，新增 core-2 由 1/3 → 3/3 |
| v7.2 | 引入第三方 **grilling** 技巧（mattpocock/skills，57 万+安装）并甄别出两条不重叠的增量：loop-spec 加 **事实查环境不问用户**（真事实直接查，只有真决策才问）+ **依赖问题拆批**（有分支的追问一次只问一个，不硬凑进 2-4 题打包）；loop-eval **首次建立 evals.json** 并加入边界用例的事实/决策分流（模糊行为不许替用户发明）。回归诚实披露：依赖拆批用例 1/3→3/3 是唯一有区分度的证据；另两条新用例新旧同分（用例设计未能隔离新技巧，非技巧无效）；发现一处新旧一致的既有缺口（边界用例未显式引用 STANDARDS 来源）留待后续 |
| v7.3 | 对照 Anthropic《**AI-driven code migration**》（Bun 1M 行 Zig→Rust 两周迁移）补上五个实战机制：**RULEBOOK 分层 + 系统性失败升级**（同类失败 ≥3 改规则并重新生成整批，绝不逐个手补——"fix the process, not the code"）、**丢弃式规则压测**（开跑前「按规则 vs 无约束」双做 diff，产物即弃）、**对抗式双评审 + 模型按角色分层**（最大模型给 verifier 和写规则者，fan-out 用小模型）、**Derive don't track**（队列从磁盘重建，done = 输出存在且过检；验证输出自写队列）、**按成本放置校验 + Pipeline of loops 模式**（patterns 第 8 式，含 build-daemon 序列化）。另修真实触发的 loop-spec bug：正文「美元符号+数字」字面量被斜杠命令位置参数替换成用户参数（实测预算默认值渲染成了 URL）——金额改写 + 维护红线 + 确定性 gotcha 检查。回归：loop-spec core-1 4/4、loop-engineering core-1 5/5 |
| 2026-07-22 | **六技能 canonical 跨宿主同步 + 可选组件架构**：正式版本更新为 loop-spec 4.0.0、loop-engineering 7.0.1、loop-eval 3.0.0、loop-review 4.0.0、loop-ops 3.0.1、loop-retro 4.0.0；新增 `PROFILE / RULES / DEVIATIONS / EXPLAIN`，并加固环境优先 containment、状态 schema、验证器、对抗 fixture、路径规范化与跨平台原子 quota 控制。完整细节见 [CHANGELOG.md](CHANGELOG.md)。 |

---

## 仓库结构

```
Build_Great_Loop/
├── README.md / README.en.md
├── CHANGELOG.md
├── LICENSE
├── loop-engineering/        # 核心：产出循环提示词
│   ├── SKILL.md
│   ├── references/          # 原理、模式、模板、组件目录与审计清单
│   ├── assets/
│   │   ├── harness-core.md / harness-skeleton.md
│   │   └── components/      # 按触发条件装配的可选组件
│   ├── evals/               # 示例评测集、路由集、对抗与回归 fixtures
│   └── scripts/             # 组件选择、状态、containment、quota 与 suite 验证器
├── loop-spec/               # 访谈 → SPEC.md（assets/spec-template.md）
├── loop-eval/               # 成功标准 + 评测 + 校准协议（黄金集防漂移）
├── loop-review/             # 审计/加固已有循环
├── loop-ops/                # 运营周期性/无人值守循环（调度·成本·安全·7 个周期模式）
├── loop-retro/              # 跑后复盘：证据诊断 + gotcha + 沉淀判定
└── skill-craft/             # skill 全生命周期：创建/修改/诊断/合并/退役（含压力测试法、模板、check-limits 脚本）
```

---

## 更新方式

重新跑一遍上面的安装脚本即可（`git clone` 拉最新，覆盖同名目录）。

---

## 常见问题

- **Q：和 Claude Code 自带的 `/loop` 是一回事吗？** 不是。`/loop` 是「按间隔重复跑一条命令」；
  这套技能是**设计循环本身**——目标、状态、验证、停止条件，产出的是提示词/harness。
- **Q：只想用其中一个技能行吗？** 行。六个正式 loop skill 都能独立触发；`skill-craft` 也是可选伴侣，不想要的目录不复制即可。
- **Q：产出的提示词是中文还是英文？** 跟随你对话的语言；技能内部说明是英文（触发更稳、对齐源文章）。
- **Q：能在 Cursor / 其他 agent 里用吗？** 技能本质是「知识注入」的 Markdown，任何能读
  `SKILL.md` 的 agent 都能用；安装路径按各家约定调整。

---

## 来源与致谢

方法蒸馏自以下官方工程文章：

- Anthropic — Agent Skills / Effective harnesses for long-running agents /
  Effective context engineering for AI agents / Writing effective tools for AI agents /
  Demystifying evals for AI agents / AI-driven code migration / agent containment practices
- GitHub — Spec-driven development / Agentic primitives & context engineering / Continuous AI（agentic CI）
- Sourcegraph — Agentic Coding in 2026
- OpenAI — Codex best practices
- 技能写作模式参考：青斧《工作流的 Skill 怎么写？从 7 个顶级 Skill 中提炼的模式与最佳实践》

---

## License

MIT，见 [LICENSE](LICENSE)。
