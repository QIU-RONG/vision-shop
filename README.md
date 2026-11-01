# VisionShop · 多模态商品助手

上传/拍摄一张商品图 → 视觉模型识别属性与关键词 → 调用 MallX 商品搜索 → 返回可点击的商品卡片。

## 架构

```
浏览器（上传图片）
      │  multipart
      ▼
FastAPI ──▶ 视觉理解（VLM，可插拔；无 key 用 mock）
      │            │ keywords
      │            ▼
      └────▶ MallX /api/products 搜索 ──▶ 商品卡片
```

## 快速开始

```powershell
cd D:\VisionShop
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 先确保 MallX 后端在 8081
.venv\Scripts\python -m uvicorn app.main:app --port 8020
# 打开 http://127.0.0.1:8020
```

冒烟：`.venv\Scripts\python scripts\smoke_test.py` → `RESULT 6/6`。

## 配置

| 变量 | 说明 |
|---|---|
| `VISION_API_KEY` | 视觉模型 key（OpenAI 兼容）；不配则用 mock |
| `VISION_BASE_URL` | 默认 `https://api.openai.com/v1` |
| `VISION_MODEL` | 默认 `gpt-4o-mini` |
| `MALLX_BASE` | MallX 后端地址，默认 `http://127.0.0.1:8081` |

## 已实现

- 图片上传校验（类型/5MB）、落盘、静态回显；
- VLM 可插拔：OpenAI 兼容 `image_url` base64；无 key 自动 mock（离线可跑）；
- 属性/关键词抽取 → MallX 搜索 → 去重卡片（名称/价格/店铺/跳详情）；
- Web 演示页（拖拽上传、识别标签、商品网格）。

## 路线图

- [ ] CLIP 图像相似检索（本地 fastembed，按图搜同款）
- [ ] 多图/视频输入；拍照上传（移动端）
- [ ] 属性编辑（用户改“黑色”为“白色”再搜）
- [ ] 与 MallX 前端集成（详情页“以图搜同款”入口）
- [ ] 真实视觉模型端到端验证（需要 key）
