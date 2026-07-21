#!/usr/bin/env python3
"""Atomic lifecycle transitions for the reference STATE component."""
import argparse, hashlib, json, os, tempfile
from pathlib import Path

def save(path, data):
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f: json.dump(data, f, indent=2); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

p=argparse.ArgumentParser(); p.add_argument("state"); p.add_argument("action", choices=["claim","effect","reconcile","complete"]); p.add_argument("item"); p.add_argument("--run-id"); p.add_argument("--output-ref"); p.add_argument("--receipt")
a=p.parse_args(); path=Path(a.state); data=json.loads(path.read_text()); item=next(x for x in data["items"] if x["id"]==a.item)
if a.action=="claim":
    if item["status"] not in {"pending","blocked"}: raise SystemExit("INVALID transition")
    item["attempt"] += 1; item["status"]="in_progress"; item["claim"]={"run_id":a.run_id}
    raw=f'{data["loop_id"]}:{item["id"]}:{item["input_digest"]}:{item["attempt"]}'
    item["idempotency_key"]="sha256:"+hashlib.sha256(raw.encode()).hexdigest()
elif a.action=="effect":
    if item["status"]!="in_progress" or not item["idempotency_key"]: raise SystemExit("CLAIM REQUIRED")
    item["output_ref"]=a.output_ref
elif a.action=="reconcile":
    if item["status"]!="in_progress": raise SystemExit("NOT IN PROGRESS")
    print("VERIFY_EXISTING_EFFECT" if item.get("output_ref") else "RETRY_WITH_SAME_IDEMPOTENCY_KEY")
    raise SystemExit(0)
else:
    receipt=json.loads(Path(a.receipt).read_text()) if a.receipt else {}
    if item["status"]!="in_progress" or not item.get("output_ref") or receipt.get("result")!="pass" or not receipt.get("evidence_ref"):
        raise SystemExit("EVIDENCE REQUIRED")
    item["verification"]=receipt; item["status"]="done"
save(path,data); print("OK")
