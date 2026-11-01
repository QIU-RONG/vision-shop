"""调用 MallX 商品搜索（只读）。"""
import os

import httpx

BASE = os.getenv("MALLX_BASE", "http://127.0.0.1:8081")


def search(keywords: list[str], size: int = 6) -> list[dict]:
    seen, out = set(), []
    for kw in keywords or []:
        try:
            with httpx.Client(timeout=10) as c:
                r = c.get(f"{BASE}/api/products", params={"keyword": kw, "current": 1, "size": size})
                r.raise_for_status()
                rows = (r.json().get("data") or {}).get("records") or []
        except Exception:  # noqa: BLE001
            continue
        for p in rows:
            pid = p.get("id")
            if pid in seen:
                continue
            seen.add(pid)
            out.append({
                "id": pid,
                "name": p.get("name"),
                "price": p.get("minPrice") or p.get("price"),
                "image": p.get("mainImage"),
                "shopName": p.get("shopName"),
            })
            if len(out) >= size:
                return out
    return out


def product(pid: int) -> dict | None:
    """按 id 取 MallX 商品（用于把视觉相似结果变成商品卡片）。"""
    try:
        with httpx.Client(timeout=10) as c:
            r = c.get(f"{BASE}/api/products/{pid}")
            if r.status_code != 200:
                return None
            d = r.json().get("data") or {}
            price = d.get("minPrice") or d.get("price")
            if price is None and d.get("skus"):
                price = d["skus"][0].get("price")
            return {"id": d.get("id", pid), "name": d.get("name"),
                    "price": price, "image": d.get("mainImage"),
                    "shopName": d.get("shopName")}
    except Exception:  # noqa: BLE001
        return None
