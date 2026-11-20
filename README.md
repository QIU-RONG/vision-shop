# VisionShop · 多模态商品助手

上传/拍摄一张商品图片 → 视觉模型识别属性与关键词 → 搜索 MallX 商品 → 返回可点击的商品卡片；
另支持 **CLIP 以图搜同款**（本地向量，无需外部服务）。

## 功能

- 图片上传（jpeg/png/webp，≤5MB），落盘与静态回显；
- 视觉理解可插拔：配置 `VISION_API_KEY` 走 OpenAI 兼容 VLM；未配置自动 mock（离线可跑）；
- 属性/关键词 → MallX `/api/products` 搜索 → 去重卡片（名称/价格/店铺/跳详情）；
- CLIP 图像相似：`fastembed` 本地 `clip-ViT-B-32-vision`（512 维），向量存 SQLite；
- CLIP 命中按 `product_id` 回查 MallX 商品，渲染相似度与商品卡片；
- Web 演示页：拖拽上传、识别标签、商品网格、以图搜同款。

## 架构

```
浏览器 ──上传图片──▶ FastAPI
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   VLM 识别属性/关键词        CLIP 图像向量（本地）
          │                       │
          ▼                       ▼
   MallX /api/products      相似图检索 → product_id → MallX 商品卡片
```

## 快速开始

前置：Python 3.10+；**先启动 MallX 后端（默认 `http://127.0.0.1:8081`）**，否则搜不到商品。

```powershell
git clone https://github.com/QIU-RONG/vision-shop.git
cd vision-shop

python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 首次下载 CLIP 模型（约 100MB），国内可加镜像
$env:HF_ENDPOINT="https://hf-mirror.com"
.venv\Scripts\python -m uvicorn app.main:app --port 8020
```

打开 <http://127.0.0.1:8020>，拖一张图片即可。

冒烟测试（需 MallX 8081 在跑）：

```powershell
.venv\Scripts\python scripts\smoke_test.py
# RESULT 9/9
```

## Docker

```bash
docker build -t vision-shop:local .

docker run -d --name vision-shop -p 8020:8020 \
  --add-host host.docker.internal:host-gateway \
  -e MALLX_BASE=http://host.docker.internal:8081 \
  -v vision_uploads:/app/uploads -v visiondata:/data \
  vision-shop:local
```

或 `docker compose up -d --build`。注意：容器里的 `MALLX_BASE` 要指向**宿主机可达的 MallX 地址**；
Docker Desktop 用 `host.docker.internal` 即可；WSL 原生 Docker 访问 Windows 宿主的 8081
可能被防火墙拦截，此时把 MallX 也放进同一 Compose 网络最稳。

## 配置

| 变量 | 说明 |
|---|---|
| `VISION_API_KEY` | 视觉模型 key（OpenAI 兼容）；不配则 mock |
| `VISION_BASE_URL` | 默认 `https://api.openai.com/v1` |
| `VISION_MODEL` | 默认 `gpt-4o-mini`，可换 Qwen-VL/GLM-4V |
| `MALLX_BASE` | MallX 后端地址，默认 `http://127.0.0.1:8081` |
| `CLIP_MODEL` | 默认 `Qdrant/clip-ViT-B-32-vision` |

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 演示页 |
| POST | `/api/analyze` | 上传图片 → 识别 → 搜商品 |
| POST | `/api/visual/index` | 图片加入 CLIP 索引（可带 label/product_id） |
| POST | `/api/visual/search` | 以图搜相似（返回相似度与商品） |
| GET | `/health` | 健康检查（含 vision 模式） |

```bash
curl -X POST http://127.0.0.1:8020/api/analyze -F "file=@phone.jpg"
curl -X POST "http://127.0.0.1:8020/api/visual/index?label=iphone&product_id=1" -F "file=@phone.jpg"
curl -X POST "http://127.0.0.1:8020/api/visual/search?top_k=3" -F "file=@query.jpg"
```

## 已知限制

- 未配视觉 key 时是 mock，识别结果是固定规则，不代表真实模型效果；
- 商品图用 `picsum.photos` 占位（外网），离线会显示占位块；
- CLIP 索引目前手动添加：MallX 种子商品图片是假域名，无法直接抓取；
- 单机 SQLite，索引规模大时应换 pgvector/Milvus。

同作者项目：[MallX 商城](https://github.com/QIU-RONG/Mallx) · [ai-gateway](https://github.com/QIU-RONG/ai-gateway)
