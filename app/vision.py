"""视觉理解（Day 1）：可插拔 VLM。

没有 VISION_API_KEY 时用 mock（按文件名/固定规则返回），保证整个链路离线可跑；
有 key 时走 OpenAI 兼容的 /chat/completions（image_url base64）。
"""
import base64
import json
import os

import httpx

SYSTEM = """你是商品识别助手。看图片，只输出 JSON：
{"caption":"一句话描述","category":"品类","attributes":["颜色/材质/款式等"],"keywords":["用于搜索的中文关键词，最多5个"]}"""


def analyze(image_path: str, filename: str) -> dict:
    key = os.getenv("VISION_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        return _mock(filename)
    base = os.getenv("VISION_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("VISION_MODEL", "gpt-4o-mini")
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": [
                {"type": "text", "text": "识别这张商品图片"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            ]},
        ],
        "temperature": 0.2,
    }
    with httpx.Client(timeout=60) as c:
        r = c.post(f"{base}/chat/completions", headers={"Authorization": f"Bearer {key}"}, json=payload)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
    start, end = text.find("{"), text.rfind("}")
    data = json.loads(text[start:end + 1])
    return _normalize(data)


def _mock(filename: str) -> dict:
    """离线 mock：按文件名线索返回，默认一部 iPhone。"""
    name = (filename or "").lower()
    if "bag" in name:
        return {"caption": "一只皮包", "category": "箱包", "attributes": ["真皮", "黑色"],
                "keywords": ["包"], "mock": True}
    return {"caption": "一部黑色智能手机，钛金属边框", "category": "手机",
            "attributes": ["黑色", "钛金属", "大屏"], "keywords": ["iPhone", "手机"], "mock": True}


def _normalize(data: dict) -> dict:
    return {
        "caption": str(data.get("caption") or ""),
        "category": str(data.get("category") or ""),
        "attributes": [str(x) for x in (data.get("attributes") or [])][:8],
        "keywords": [str(x) for x in (data.get("keywords") or [])][:5],
        "mock": False,
    }
