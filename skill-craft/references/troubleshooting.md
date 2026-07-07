# 故障诊断（指南第七部分）

## 通用排查顺序（70% 的问题在前两步）

1. **确认加载**：路径对吗？YAML 格式错没（缺 `---` / 缩进）？
   快验：问 Agent "What Skills are available?"，或 `head -10 SKILL.md`。
2. **确认 description 触发**：用**用户实际说的话**测，不是自己预想的触发词。
3. 逐条对比 AI 输出与 SKILL.md 指令的偏差，定位跑偏点。
4. 确认脚本可执行（权限/依赖/路径/平台）。
5. 关键步骤间插检查点缩小范围。
6. 有/无 skill 对比测试看差异。

## 触发问题

```
该触发没触发？
├─ 没加载 → 查路径/YAML
├─ description 太窄或关键词缺失 → 对比用户原话，补触发词（含口语）
├─ 被其他 skill 抢单 → 查语义重叠 → 给其中一方加排除说明
│    经验：对方 description 若带全类目 MUST（"MUST use before any…"），
│    仅加强己方大概率赢不了——正解是给对方加排除行（第三方 skill 须用户
│    批准），或接受绕路并教用户点名调用
└─ 用户提问太模糊 → 非 skill 问题，引导用户具体化

不该触发却触发？
├─ description 太宽 → 末尾加"不适用于[场景]"
└─ 与其他 skill 重叠 → 给误触发方加排除；或合并
```

**经验法则**：两个 skill 触发准确率都 <80% → 先查 description 冲突。
"写清不做什么"往往比"写清做什么"更有效。

## 执行问题

```
触发了但不按步骤走？
├─ 定位跑偏的那一步 → 加明确祈使句 + 判断条件
├─ 跳步偷懒 → 借口反驳表 / 强硬语气 / 量化阈值（"Delete it. Start over."）
├─ 自作主张加步骤 → 负面指令"不要自动执行 X / 不要修改 Y"
└─ 不理解为什么、换场景就傻 → 给规则补"为什么"
```

## 脚本报错速查

| 报错 | 解法 |
|---|---|
| Permission denied | `chmod +x scripts/xxx.sh` |
| bad interpreter | 查 shebang：`#!/bin/bash` |
| command not found / ModuleNotFoundError | 前置条件里列依赖和安装命令 |
| No such file or directory | 用相对 skill 目录路径，或开头 cd 到位 |
| 平台不兼容 | `sed -E` 非 `-r`；`set -euo pipefail`；先 check 命令存在。Windows 注意：`.ps1` 含非 ASCII 需 UTF-8 BOM，否则 PowerShell 5.1 按 ANSI 误读——中文内容优先放 JSON/由 Python 驱动 |

## 规模问题

```
越写越大控制不住？
├─ 正文超 300 行 → 细节下沉 references/
├─ 某 Step 超 100 行 → 提取为独立子 skill
├─ 多分支都很长 → 拆子 skill，主文件只做路由
└─ 多 skill 重复前置 → 提取通用前置 skill
```
