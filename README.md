# Build Great Loop · 可组合的 Agent Loop 技能组

[中文](README.md) | [English](README.en.md)

![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827)
![Claude Compatible](https://img.shields.io/badge/Claude-Compatible-6B46C1)
![Loop Skills](https://img.shields.io/badge/Loop%20Skills-6-0E7490)
![Component Tests](https://img.shields.io/badge/Component%20Tests-38%2F38-success)
![License](https://img.shields.io/github/license/VioletScar-Hui/Build_Great_Loop)

一套同时支持 Codex 与 Claude Code 的 Loop Engineering 技能组：先澄清目标，再生成可运行、可恢复、可验证、会停止的 agent loop，并覆盖评测、审查、运营与复盘。

本次版本以同一份 canonical 源同步到 Codex 和 Claude，六个正式 loop skill 的目录字节完全一致。

## 核心亮点

- 六技能生命周期：`spec → engineering → eval → review → ops → retro`。
- CORE 默认保持精简；只有触发条件成立时才加入可选组件。
- `PROFILE`：读取任务相关的稳定偏好和可发现环境事实，不把推断冒充授权。
- `RULES`：同类失败反复出现时修订战术规则，并重新验证受影响工作。
- `DEVIATIONS`：把会实质影响计划的偏差连同证据持久化，不借机扩权。
- `EXPLAIN`：重大 merge/ship 前生成证据约束的说明，并记录理解或显式豁免。
- 环境层优先的 L3 containment、独立验证、崩溃恢复和机器可检停止条件。
- 宿主中立：不强制固定模型、Claude 专用代理路径、`/loop`、Git 或专有问答工具。

## 技能一览

| 技能 | 当前版本 | 作用 |
|---|---:|---|
| `loop-spec` | 4.0.0 | 判断任务是否值得建 loop，并澄清目标、边界、风险和成功标准 |
| `loop-engineering` | 7.0.1 | 生成最小充分、可直接运行的 harness；包含组件目录与验证脚本 |
| `loop-eval` | 3.0.0 | 设计成功标准、评测集和 grader |
| `loop-review` | 4.0.0 | 审计已有 harness，检查缺失、死亡或无证据组件 |
| `loop-ops` | 3.0.1 | 安全运行周期性或无人值守 loop，管理预算、权限与停止机制 |
| `loop-retro` | 4.0.0 | 根据真实运行工件复盘，并提出规则、标准和 harness 修订 |
| `skill-craft` | 独立伴侣 | skill 创建、修改、诊断、合并与退役的方法论 |

## 安装

以下命令均在终端中执行；Windows 使用 PowerShell，macOS/Linux 使用 Terminal。

### macOS / Linux：同时安装到 Codex 与 Claude

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

### Windows PowerShell：同时安装到 Codex 与 Claude

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

如只使用一个宿主，删除另一条目标路径即可。更新时重新运行安装命令，覆盖同名目录。

## 使用

安装后新开会话，直接用自然语言提出需求：

```text
把这个模糊的自动化想法先整理成 loop 规格。
```

```text
帮我写一个可以中断续跑、直到测试通过才停止的 agent loop harness。
```

```text
审查这份 loop prompt，重点检查虚假完成、失控重试和重启丢状态。
```

```text
这个 loop 已经跑完了，请根据 run log 和状态文件做复盘。
```

技能会自动路由；也可以在宿主支持时显式点名 `loop-spec`、`loop-engineering` 等技能。

## 组件模型

`loop-engineering` 总是从 `CORE` 开始，再根据复杂度选择组件：

| 触发 | 组件 |
|---|---|
| 跨重启状态 | `STATE` |
| 可执行验证 | `VERIFY` |
| 高风险或无人值守边界 | `CONTAIN` |
| 质量会漂移 | `CALIBRATE` |
| 启动前需要恢复演练 | `SHAKEDOWN` |
| 并行任务可独立拆分 | `FANOUT` |
| 稳定偏好或可发现事实 | `PROFILE` |
| 同类失败反复出现 | `RULES` |
| 证据显示计划出现实质偏差 | `DEVIATIONS` |
| 重大 merge/ship 需要理解交接 | `EXPLAIN` |

完整触发、依赖与验收规则见 `loop-engineering/references/component-catalog.md`。

## 验证

本次同步发布通过：

- 可选组件与对抗效果：38/38。
- 旧功能回归：18/18。
- 跨目录同步验证器：35/35。
- suite validator：5/5。
- 配对模型评测：候选 31/33，旧基线 27/33；优势集中在四个新增组件的显式选择。

在仓库根目录运行：

```bash
python3 loop-engineering/scripts/test_validate_suite.py
python3 loop-engineering/scripts/validate_suite.py .
python3 loop-engineering/scripts/run_component_fixtures.py
python3 loop-engineering/scripts/run_component_fixtures.py --legacy
python3 loop-engineering/scripts/select_components.py loop-engineering/evals/fixtures/simple.json
```

## 目录结构

```text
Build_Great_Loop/
├── loop-spec/
├── loop-engineering/
│   ├── assets/components/
│   ├── evals/fixtures/
│   ├── references/component-catalog.md
│   └── scripts/
├── loop-eval/
├── loop-review/
├── loop-ops/
├── loop-retro/
├── skill-craft/
├── README.md
├── README.en.md
└── CHANGELOG.md
```

## 更新日志

- 2026-07：六技能跨宿主 canonical 同步；新增 `PROFILE / RULES / DEVIATIONS / EXPLAIN`；组件化 harness、环境 containment、状态 schema、验证器和对抗 fixture 全面加固；补充路径规范化与跨平台原子 quota 控制。
- 历史版本与详细变更见 [CHANGELOG.md](CHANGELOG.md) 及各 skill 自己的 `CHANGELOG.md`。

## 来源与致谢

设计参考 Anthropic 的 Agent Skills、长时运行 agent harness、context engineering、eval 和 containment 实践，并结合 Codex/Claude 的本地技能加载方式做成宿主中立实现。

## License

[MIT](LICENSE)
