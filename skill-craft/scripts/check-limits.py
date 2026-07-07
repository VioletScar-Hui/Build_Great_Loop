#!/usr/bin/env python3
"""skill-craft 确定性核对脚本。用法: python check-limits.py <skill目录>
输出 JSON: description 字数 / SKILL.md 行数 / core 用例数 / 各限额判定。
遵守脚本四原则：自愈（异常也输出 JSON 正常退出）、结构化输出、幂等、只读不写。"""
import json
import re
import sys
from pathlib import Path

# 限额来源：《Skill 完整实操指南》§3.1（description ≤1024 字符）、§2.3（正文
# ≤500 行硬上限）、§5.5（core 5–10）。可用环境按需覆盖，但需记录理由。
LIMITS = {"desc_chars_max": 1024, "skill_lines_max": 500, "evals_core_min": 5}


def main():
    try:
        root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
        skill_md = root / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")

        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        fm = m.group(1) if m else ""
        desc_lines, in_desc = [], False
        for ln in fm.split("\n"):
            if ln.startswith("description:"):
                in_desc = True
                rest = ln[len("description:"):].strip()
                if rest not in (">", ">-", "|"):
                    desc_lines.append(rest)
                continue
            if in_desc:
                if ln.startswith(" ") or not ln.strip():
                    desc_lines.append(ln.strip())
                else:
                    break
        desc = " ".join(x for x in desc_lines if x)

        body_lines = len(text.split("\n"))
        core = 0
        evals_path = root / "evals" / "evals.json"
        if evals_path.exists():
            data = json.loads(evals_path.read_text(encoding="utf-8"))
            core = sum(1 for e in data.get("evals", []) if e.get("category") == "core")

        checks = {
            "desc_chars": len(desc),
            "desc_ok": len(desc) <= LIMITS["desc_chars_max"],
            "skill_lines": body_lines,
            "lines_ok": body_lines <= LIMITS["skill_lines_max"],
            "evals_core": core,
            "core_ok": core >= LIMITS["evals_core_min"],
            "has_version": "version:" in fm,
            "has_exclusion": ("不适用" in desc) or ("Not for" in desc) or ("不支持" in desc),
        }
        checks["status"] = "ok" if all(
            checks[k] for k in ("desc_ok", "lines_ok", "core_ok", "has_version", "has_exclusion")
        ) else "fail"
        print(json.dumps(checks, ensure_ascii=False))
    except Exception as e:  # 自愈：任何异常都输出结构化错误
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
