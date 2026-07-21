#!/usr/bin/env python3
"""Atomic file-backed reference quota controller for a single host."""

import argparse
import json
import os
from contextlib import contextmanager
from pathlib import Path


def deny(reason: str) -> None:
    print("DENY", reason)
    raise SystemExit(2)


@contextmanager
def exclusive_lock(path: Path):
    """Hold a one-byte cross-platform lock in a sidecar file."""
    with path.open("a+b") as lock_file:
        if os.name == "nt":
            import msvcrt

            lock_file.seek(0, os.SEEK_END)
            if lock_file.tell() == 0:
                lock_file.write(b"\0")
                lock_file.flush()
            lock_file.seek(0)
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file, fcntl.LOCK_UN)


parser = argparse.ArgumentParser()
parser.add_argument("ledger")
parser.add_argument("run_id")
parser.add_argument("amount", type=int)
parser.add_argument("--max", type=int, required=True)
args = parser.parse_args()

if args.amount <= 0:
    deny("amount must be positive")
if args.max <= 0:
    deny("max must be positive")

ledger_path = Path(args.ledger)
ledger_path.parent.mkdir(parents=True, exist_ok=True)
with exclusive_lock(Path(str(ledger_path) + ".lock")):
    if ledger_path.exists():
        raw = ledger_path.read_text(encoding="utf-8")
        data = json.loads(raw) if raw else {"reserved": 0, "runs": {}}
    else:
        data = {"reserved": 0, "runs": {}}

    runs = data.get("runs")
    reserved = data.get("reserved")
    if (
        not isinstance(runs, dict)
        or not isinstance(reserved, int)
        or reserved < 0
        or any(not isinstance(value, int) or value <= 0 for value in runs.values())
        or sum(runs.values()) != reserved
    ):
        deny("invalid ledger")

    if args.run_id in runs:
        if runs[args.run_id] != args.amount:
            deny("run reservation mismatch")
        print("ALLOW already reserved")
        raise SystemExit(0)

    if reserved + args.amount > args.max:
        deny("quota exceeded")

    runs[args.run_id] = args.amount
    data["reserved"] = reserved + args.amount
    temporary = ledger_path.with_name(ledger_path.name + f".tmp-{os.getpid()}")
    with temporary.open("w", encoding="utf-8") as output:
        json.dump(data, output)
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, ledger_path)

print("ALLOW reserved")
