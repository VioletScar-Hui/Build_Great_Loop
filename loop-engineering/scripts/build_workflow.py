#!/usr/bin/env python3
"""Build a replayable bounded fan-out graph from persisted inputs."""
import argparse, hashlib, json
p=argparse.ArgumentParser(); p.add_argument("inputs"); p.add_argument("--batch-size",type=int,default=20); a=p.parse_args()
items=json.load(open(a.inputs, encoding="utf-8")); nodes=[]
for i in range(0,len(items),a.batch_size):
    batch=items[i:i+a.batch_size]; raw=json.dumps(batch,sort_keys=True,separators=(",",":"))
    nodes.append({"id":f"batch-{i//a.batch_size:05d}","input_digest":"sha256:"+hashlib.sha256(raw.encode()).hexdigest(),"items":batch})
print(json.dumps({"queue_size":len(nodes),"max_context_items":a.batch_size,"nodes":nodes},ensure_ascii=False))
