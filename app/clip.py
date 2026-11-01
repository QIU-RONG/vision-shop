"""本地 CLIP 图像向量（Day 2）。"""
import math
import os

_MODEL = None


def embed_image(path: str):
    global _MODEL
    if _MODEL is None:
        from fastembed import ImageEmbedding
        _MODEL = ImageEmbedding(model_name=os.getenv("CLIP_MODEL", "Qdrant/clip-ViT-B-32-vision"), threads=1)
    vec = next(iter(_MODEL.embed([path])))
    return [float(x) for x in vec]


def cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)
