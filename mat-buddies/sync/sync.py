"""Fold new Mat Buddies taps from the ntfy relay into state.json (run by GitHub Actions)."""
import json, re, time, urllib.request, datetime
TOPIC = "https://ntfy.sh/mat-buddies-ch7q4xk2m9"
PATH = "mat-buddies/state.json"
DAYS = {"mon", "tue", "wed", "thu", "fri", "sat"}
st = json.load(open(PATH))
st.setdefault("weeks", {}); st.setdefault("seen", []); st.setdefault("lastTime", 0)
since = str(max(0, st["lastTime"] - 1)) if st["lastTime"] else "12h"
req = urllib.request.Request(TOPIC + "/json?poll=1&since=" + since, headers={"User-Agent": "mat-buddies-sync"})
lines = urllib.request.urlopen(req, timeout=30).read().decode().splitlines()
seen = set(st["seen"]); changed = False
for line in lines:
    try: m = json.loads(line)
    except Exception: continue
    if m.get("event") != "message" or m["id"] in seen or m["time"] < st["lastTime"]: continue
    try: e = json.loads(m["message"])
    except Exception: e = None
    if isinstance(e, dict):
        if e.get("t") == "set" and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(e.get("week"))) and e.get("day") in DAYS and e.get("f") in ("k", "a"):
            st["weeks"].setdefault(e["week"], {}).setdefault(str(e["kid"])[:40], {}).setdefault(e["day"], {})[e["f"]] = bool(e.get("v"))
        elif e.get("t") == "addkid" and isinstance(e.get("id"), str) and isinstance(e.get("name"), str):
            if not any(k["id"] == e["id"] for k in st["roster"]):
                st["roster"].append({"id": e["id"][:40], "name": e["name"][:24]})
    seen.add(m["id"]); st["seen"].append(m["id"]); st["lastTime"] = max(st["lastTime"], m["time"]); changed = True
if changed:
    st["seen"] = st["seen"][-300:]
    cutoff = (datetime.date.today() - datetime.timedelta(days=180)).isoformat()
    st["weeks"] = {w: v for w, v in st["weeks"].items() if w >= cutoff}
    json.dump(st, open(PATH, "w"), indent=1)
print("new messages folded in" if changed else "no new messages")
