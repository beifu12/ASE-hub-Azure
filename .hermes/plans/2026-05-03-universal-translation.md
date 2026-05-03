# Universal Translation Implementation Plan

> **For Hermes:** Sprint 6 — add general English↔Chinese translation.

**Goal:** 给 ASE Hub 加上通用翻译能力，不只是 Azure 术语，而是**任意英文→中文**翻译（邮件、文章、段落随便贴）

**Architecture:** 
- 翻译后端用 **MyMemory API**（免费，无需 API Key，1000字符/天匿名额度，注册免费 Key 提升到 10000字符/天）
- 新增 `/api/translate/zh` 端点
- 保留现有 `/api/translate`（Azure 术语表），两者互补
- 前端新增 "通用翻译" Blade 面板：粘贴英文 → 点翻译 → 出中文结果

**Tech Stack:** Python `requests`（已有），MyMemory REST API

---

## Task 1: 创建通用翻译服务

**Objective:** 新建 `universal_translator.py`，封装 MyMemory API

**Files:**
- Create: `app/services/universal_translator.py`

**代码：**

```python
"""Universal English↔Chinese translator via MyMemory (free, no API key)."""

import requests
from typing import Optional

_MYMEMORY_URL = "https://api.mymemory.translated.net/get"


def translate_en2zh(text: str, email: Optional[str] = None) -> dict:
    """
    Translate English text to Chinese via MyMemory.
    
    Anonymous: ~1000 chars/day. With email: ~10000 chars/day.
    Email is optional — pass user email for higher quota.
    """
    if not text.strip():
        return {"error": "No text provided"}

    params = {"q": text[:500], "langpair": "en|zh-CN"}
    if email:
        params["de"] = email

    try:
        resp = requests.get(_MYMEMORY_URL, params=params, timeout=10)
        data = resp.json()

        if resp.status_code == 200 and data.get("responseStatus") == 200:
            translated = data["responseData"]["translatedText"]
            match = data["responseData"].get("match", 0)
            return {
                "original": text[:500],
                "translated": translated,
                "quality": match * 100,  # 0-100 match score
                "source": "MyMemory"
            }
        else:
            return {
                "error": data.get("responseDetails", "Translation failed"),
                "original": text[:500]
            }
    except Exception as e:
        return {"error": str(e), "original": text[:500]}


def translate_zh2en(text: str, email: Optional[str] = None) -> dict:
    """Translate Chinese text to English."""
    if not text.strip():
        return {"error": "No text provided"}

    params = {"q": text[:500], "langpair": "zh-CN|en"}
    if email:
        params["de"] = email

    try:
        resp = requests.get(_MYMEMORY_URL, params=params, timeout=10)
        data = resp.json()

        if resp.status_code == 200 and data.get("responseStatus") == 200:
            return {
                "original": text[:500],
                "translated": data["responseData"]["translatedText"],
                "quality": data["responseData"].get("match", 0) * 100,
                "source": "MyMemory"
            }
        return {"error": data.get("responseDetails", "Translation failed")}
    except Exception as e:
        return {"error": str(e)}
```

**Step 2: 验证**

```bash
cd /root/projects/ase-hub && \
python3 -c "
from app.services.universal_translator import translate_en2zh
r = translate_en2zh('Hello world, how are you today?')
print(r)
"
```

预期输出：`{'original': 'Hello world...', 'translated': '你好世界...', ...}`

---

## Task 2: 添加 API 端点

**Objective:** 在 `api.py` 加 `/api/translate/zh` 和 `/api/translate/en`

**Files:**
- Modify: `app/routes/api.py`（在 glossary 区域之后追加）

```python
# ═══════════ UNIVERSAL TRANSLATION ═══════════

from app.services import universal_translator


@router.get("/translate/zh")
async def api_translate_zh(q: str = "", email: str = ""):
    """Translate English to Chinese via MyMemory."""
    if not q.strip():
        return {"error": "Query parameter 'q' required"}
    email_addr = email if email else None
    return universal_translator.translate_en2zh(q.strip(), email_addr)


@router.get("/translate/en")
async def api_translate_en(q: str = "", email: str = ""):
    """Translate Chinese to English via MyMemory."""
    if not q.strip():
        return {"error": "Query parameter 'q' required"}
    email_addr = email if email else None
    return universal_translator.translate_zh2en(q.strip(), email_addr)
```

---

## Task 3: 新建通用翻译页面 HTML

**Objective:** 简约翻译工具页面

**Files:**
- Create: `app/templates/translator.html`

页面设计：居中布局，上方 textarea 贴英文，点按钮翻译，下方显示中文结果。

---

## Task 4: 添加页面路由

**Objective:** 访问 `/translator` 显示翻译工具

**Files:**
- Modify: `app/routes/pages.py`

```python
@router.get("/translator", response_class=HTMLResponse)
async def translator_page():
    path = TEMPLATE_DIR / "translator.html"
    return path.read_text(encoding="utf-8")
```

---

## Task 5: 侧边栏添加翻译入口

**Files:**
- Modify: `app/templates/index.html`（sidebar 导航区）

在 Favorites 区域添加：
```html
<a class="nav-item" href="/translator">🌐 Translate</a>
```

---

## Task 6: 添加测试

**Files:**
- Modify: `app/tests/test_api.py`

```python
def test_translate_zh(client):
    token = _login_admin(client)
    response = client.get(
        "/api/translate/zh?q=hello",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "translated" in data or "error" in data
```

---

## Task 7: 构建部署

标准流程：Docker build → push ACR → SSH deploy

---

## 预算

| API | 免费额度 | 是否够用 |
|-----|---------|---------|
| MyMemory (匿名) | ~1000 字符/天 | 几条短邮件 |
| MyMemory (注册) | ~10000 字符/天 | 足够日常使用 |
| Microsoft Translator (Azure) | 2M 字符/月 | 绰绰有余 |

**建议先用 MyMemory**（零配置），如果不够用再切到 Azure Translator。
