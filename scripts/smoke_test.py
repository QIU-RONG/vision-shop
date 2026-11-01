"""多模态助手冒烟测试：上传 1x1 PNG → mock 识别 → 搜 MallX。"""
import base64
import sys

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8020"
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
ok, fail = 0, []


def check(name, cond, extra=""):
    global ok
    if cond:
        ok += 1
        print("PASS", name, extra)
    else:
        fail.append(name)
        print("FAIL", name, extra)


with httpx.Client(timeout=30) as c:
    h = c.get(f"{BASE}/health").json()
    check("health", h["status"] == "UP", str(h))
    r = c.post(f"{BASE}/api/analyze", files={"file": ("iphone.png", PNG, "image/png")})
    check("analyze 200", r.status_code == 200, str(r.status_code))
    j = r.json() if r.status_code == 200 else {}
    check("mock vision", (j.get("analysis") or {}).get("mock") is True)
    check("keywords", bool((j.get("analysis") or {}).get("keywords")))
    check("products found", j.get("productCount", 0) >= 1, f"count={j.get('productCount')}")
    check("product has name", bool((j.get("products") or [{}])[0].get("name")))

    vi = c.post(f"{BASE}/api/visual/index", files={"file": ("smoke.png", PNG, "image/png")},
                params={"label": "smoke-a"})
    check("visual index", vi.status_code == 200 and vi.json().get("dim", 0) > 0, vi.text[:80])
    vs = c.post(f"{BASE}/api/visual/search", files={"file": ("smoke-q.png", PNG, "image/png")},
                params={"top_k": 3})
    matches = vs.json().get("matches") or []
    check("visual search", vs.status_code == 200 and matches and matches[0]["score"] > 0.9,
          f"score={matches[0]['score'] if matches else None}")

print(f"RESULT {ok}/{ok + len(fail)}", "fail:", fail)
sys.exit(0 if not fail else 1)
