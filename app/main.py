"""多模态商品助手（Day 1）：拍照/上传图片 → 视觉理解 → 搜 MallX 商品。"""
import os
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from . import mallx, vision

app = FastAPI(title="VisionShop", version="0.1.0")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_BYTES = 5 * 1024 * 1024
ALLOWED = {"image/jpeg", "image/png", "image/webp"}


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"), media_type="text/html")


@app.get("/health")
def health():
    return {"status": "UP", "vision": "mock" if not (os.getenv("VISION_API_KEY") or os.getenv("OPENAI_API_KEY")) else "vlm"}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=400, detail="只支持 jpeg/png/webp")
    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="图片不能超过 5MB")
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[file.content_type]
    path = os.path.join(UPLOAD_DIR, uuid.uuid4().hex + ext)
    with open(path, "wb") as f:
        f.write(raw)
    info = vision.analyze(path, file.filename or "")
    products = mallx.search(info.get("keywords") or [])
    return {"filename": file.filename, "image": f"/uploads/{os.path.basename(path)}",
            "analysis": info, "products": products, "productCount": len(products)}


@app.get("/uploads/{name}")
def uploaded(name: str):
    path = os.path.join(UPLOAD_DIR, os.path.basename(name))
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
    return FileResponse(path)
