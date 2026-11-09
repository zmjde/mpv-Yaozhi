#!/usr/bin/env python3
"""维护 .github/sync-state.json（同步状态 / 月初保活）。

用法: python3 sync_state.py sync|heartbeat
依赖环境变量: UPSTREAM, UPSTREAM_BRANCH, TARGET_BRANCH, CADENCE,
             STATE_FILE, GITHUB_REPOSITORY；sync 模式另需 UPSTREAM_SHA。
"""
import datetime
import json
import os
import sys
from pathlib import Path

mode = sys.argv[1] if len(sys.argv) > 1 else "heartbeat"
path = Path(os.environ.get("STATE_FILE", ".github/sync-state.json"))
try:
    state = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    state = {}

now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
state.update({
    "schema": 1,
    "repository": os.environ.get("GITHUB_REPOSITORY", ""),
    "upstream": os.environ["UPSTREAM"],
    "upstream_branch": os.environ["UPSTREAM_BRANCH"],
    "target_branch": os.environ["TARGET_BRANCH"],
    "cadence": os.environ.get("CADENCE", ""),
    "policy": "additive-only; never delete; upstream-unavailable = no-op",
    "last_check_utc": now,
})
if mode == "sync":
    state["last_upstream_sha"] = os.environ["UPSTREAM_SHA"]
    state["last_sync_utc"] = now

path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(state, indent=2, ensure_ascii=False))
