# marketing-toolbox 行銷工具箱 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 上線 https://yazelin.github.io/marketing-toolbox/ ——台灣行銷人的免費線上小工具書籤站(自製 7 個 + 外部實測過的工具,約 20 個)。

**Architecture:** 純靜態 GitHub Pages:單檔 `index.html`(HTML+CSS+JS 全 inline)fetch 同目錄 `tools.json` 渲染卡片牆;分類 tab 與搜尋用原生 JS。加工具 = 改一筆 JSON。`check_tools.py`(stdlib)驗 JSON schema 與連結活著;`verify/mobile-check.cjs`(playwright)驗手機 RWD。

**Tech Stack:** 原生 HTML/CSS/JS(零框架、零 build、零 runtime 依賴)、Python 3 stdlib(驗證器)、Playwright(已全域安裝 1.54.1,僅驗收用)、inkscape 1.4.4(OG 圖輸出)、gh CLI(建 repo 與 Pages)。

## Global Constraints

- Spec:`docs/superpowers/specs/2026-07-15-marketing-toolbox-design.md`,以下每條抄自 spec,所有 task 一體適用。
- 全站正體中文;站內文案與 commit 訊息**不用 emoji**(工具內容本身的 emoji 不在此限)。
- 收錄門檻(硬規則,含自製工具):1) 免費(免費層足以完成核心用途) 2) 免註冊免登入即可用到結果 3) 開瀏覽器就能用。外部工具**上架前逐一人工實測**。
- 分類固定五類,字串精確為:`素材製作`、`文案與提示詞`、`發文前檢測`、`互動與名單`、`連結與追蹤`。
- tag 固定三值:`自製`、`開源`(有公開 repo)、`官方`(原廠免費提供、無公開 repo)。
- 授權 MIT,著作權人 `2026 林亞澤 (Yaze Lin)`。
- footer 推廣三連結固定為:`https://github.com/yazelin/marketing-toolbox`、`https://www.facebook.com/yaze.lin.gm`、`https://buymeacoffee.com/yazelin`。
- 資產連結不加 cache-busting 參數(不加 `?v=`)。
- 不引用任何外部 CDN/webfont/analytics;頁面資產只有 repo 內檔案。
- v1 不做:後端、Worker、訪客分析、英文版、工具截圖、自動掃描、評分留言。
- 工作目錄:`/home/ct/marketing-toolbox`(已 git init,main 分支,spec 已 commit)。
- 每個 commit 訊息結尾加:`Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`。

---

### Task 1: 專案基礎 + tools.json 資料層 + 驗證器

**Files:**
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `check_tools.py`
- Create: `tools.json`

**Interfaces:**
- Produces: `tools.json` — 陣列,每筆欄位 `name`(str)、`url`(https)、`category`(五類之一)、`tag`(自製/開源/官方)、`desc`(str)、`usage`(str)、`repo`(選填,GitHub URL)。Task 2 的 index.html 與 Task 4 都吃這個 schema。
- Produces: `python3 check_tools.py [--live]` — schema 驗證,`--live` 加驗每個 url HTTP <400;全過 exit 0 印 `OK: N tools`,否則每行一錯 exit 1。

- [ ] **Step 1: 寫 LICENSE 與 .gitignore**

`LICENSE`(MIT 全文):

```text
MIT License

Copyright (c) 2026 林亞澤 (Yaze Lin)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

`.gitignore`:

```text
__pycache__/
*.pyc
```

- [ ] **Step 2: 寫 check_tools.py(先寫驗證器 = 這層的測試)**

```python
#!/usr/bin/env python3
"""tools.json 驗證器:schema 檢查;--live 加驗每個 url 活著(HTTP <400)。"""
import json
import sys
import urllib.request

CATS = {"素材製作", "文案與提示詞", "發文前檢測", "互動與名單", "連結與追蹤"}
TAGS = {"自製", "開源", "官方"}
REQUIRED = ("name", "url", "category", "tag", "desc", "usage")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) marketing-toolbox link check"}


def check(path="tools.json", live=False):
    errors = []
    try:
        with open(path, encoding="utf-8") as f:
            tools = json.load(f)
    except Exception as e:  # 檔案不存在或 JSON 壞掉都算同一種失敗
        return [f"tools.json 讀取失敗: {e}"], 0
    if not isinstance(tools, list) or not tools:
        return ["tools.json 必須是非空陣列"], 0
    seen_names, seen_urls = set(), set()
    for i, t in enumerate(tools):
        where = f"#{i} {t.get('name', '?')}"
        for field in REQUIRED:
            if not isinstance(t.get(field), str) or not t[field].strip():
                errors.append(f"{where}: 缺欄位 {field}")
        if t.get("category") not in CATS:
            errors.append(f"{where}: category 不在五類內")
        if t.get("tag") not in TAGS:
            errors.append(f"{where}: tag 須為 自製/開源/官方")
        if not str(t.get("url", "")).startswith("https://"):
            errors.append(f"{where}: url 須為 https")
        if "repo" in t and not str(t["repo"]).startswith("https://github.com/"):
            errors.append(f"{where}: repo 須為 GitHub 連結")
        if t.get("name") in seen_names:
            errors.append(f"{where}: name 重複")
        if t.get("url") in seen_urls:
            errors.append(f"{where}: url 重複")
        seen_names.add(t.get("name"))
        seen_urls.add(t.get("url"))
        if live and str(t.get("url", "")).startswith("https://"):
            try:
                req = urllib.request.Request(t["url"], headers=UA)
                with urllib.request.urlopen(req, timeout=20) as resp:
                    if resp.status >= 400:
                        errors.append(f"{where}: HTTP {resp.status}")
            except Exception as e:
                errors.append(f"{where}: 連線失敗 {e}")
    return errors, len(tools)


if __name__ == "__main__":
    errs, n = check(live="--live" in sys.argv)
    for e in errs:
        print(e)
    if errs:
        sys.exit(1)
    print(f"OK: {n} tools")
```

- [ ] **Step 3: 跑驗證器,確認它會抓錯(此時 tools.json 還不存在)**

Run: `cd /home/ct/marketing-toolbox && python3 check_tools.py`
Expected: 印出 `tools.json 讀取失敗: ...`,exit code 1(`echo $?` 為 1)。

- [ ] **Step 4: 寫 tools.json(首發 7 個自製工具,內容如下,一字不差)**

```json
[
  {
    "name": "emoji 拉霸機",
    "url": "https://yazelin.github.io/emoji-slot-machine/",
    "category": "素材製作",
    "tag": "自製",
    "desc": "3×3 emoji 格子轉成循環拉霸動畫影片",
    "usage": "FB 抽獎貼文放一支會動的開獎影片,比純文字停留更久、互動更多",
    "repo": "https://github.com/yazelin/emoji-slot-machine"
  },
  {
    "name": "LINE 貼圖工作室",
    "url": "https://yazelin.github.io/line-sticker-studio/",
    "category": "素材製作",
    "tag": "自製",
    "desc": "上傳一張圖,AI 生成八張 LINE 貼圖,打包 ZIP 可直接上架",
    "usage": "品牌吉祥物做成貼圖上架 LINE,粉絲日常聊天就在幫你曝光",
    "repo": "https://github.com/yazelin/line-sticker-studio"
  },
  {
    "name": "AI 字體風格庫",
    "url": "https://yazelin.github.io/ai-font-styles/",
    "category": "文案與提示詞",
    "tag": "自製",
    "desc": "上百種 AI 生圖字體風格實渲圖卡,一鍵複製提示詞",
    "usage": "做活動主視覺前先挑字體風格,提示詞直接複製進生圖工具",
    "repo": "https://github.com/yazelin/ai-font-styles"
  },
  {
    "name": "PromptFill",
    "url": "https://yazelin.github.io/PromptFill/",
    "category": "文案與提示詞",
    "tag": "自製",
    "desc": "結構化 AI 繪圖提示詞產生器",
    "usage": "行銷素材要固定風格量產時,把提示詞欄位鎖住只換主題",
    "repo": "https://github.com/yazelin/PromptFill"
  },
  {
    "name": "行銷頁健檢器",
    "url": "https://yazelin.github.io/marketing-page-checker/",
    "category": "發文前檢測",
    "tag": "自製",
    "desc": "貼上網址,檢查 OG、SEO、CTA、速度與追蹤設定",
    "usage": "活動頁上線前跑一輪,別等發文後才發現分享卡片破圖",
    "repo": "https://github.com/yazelin/marketing-page-checker"
  },
  {
    "name": "今天吃什麼",
    "url": "https://yazelin.github.io/what-to-eat/",
    "category": "互動與名單",
    "tag": "自製",
    "desc": "便當遊戲風餐點轉盤,點一下交給命運決定",
    "usage": "社群互動貼文素材:叫粉絲轉一次,截圖留言今天的命運",
    "repo": "https://github.com/yazelin/what-to-eat"
  },
  {
    "name": "網頁粉碎機",
    "url": "https://yazelin.github.io/div-smash/",
    "category": "互動與名單",
    "tag": "自製",
    "desc": "貼一個網址,把網頁打成碎片,真實物理掉落堆疊",
    "usage": "官網改版文的哏:把舊站打爛的影片配新站連結,自帶話題",
    "repo": "https://github.com/yazelin/div-smash"
  }
]
```

- [ ] **Step 5: 跑驗證器確認過**

Run: `python3 check_tools.py && python3 check_tools.py --live`
Expected: 兩次都印 `OK: 7 tools`,exit 0。(--live 那次約 10 秒,7 個 URL 在 plan 撰寫當日已全數 curl 過 200。)

- [ ] **Step 6: Commit**

```bash
cd /home/ct/marketing-toolbox
git add LICENSE .gitignore check_tools.py tools.json
git commit -m "feat(data): tools.json 首發 7 個自製工具 + schema/連結驗證器

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: index.html 單頁卡片牆 + 手機驗證腳本

**Files:**
- Create: `index.html`
- Create: `verify/mobile-check.cjs`

**Interfaces:**
- Consumes: 同目錄 `tools.json`(Task 1 schema)。
- Produces: 頁面 DOM 約定——每張卡片是 `article.card`;分類 tab 是 `button`(accessible name 即分類字串,如「發文前檢測」);搜尋框 `input#q`。Task 7 的驗收腳本依賴這些 selector。
- Produces: `NODE_PATH=$(npm root -g) node verify/mobile-check.cjs <url>` — iPhone 13 模擬,印 `{"cards":N,"hscroll":bool,"afterTab":N}`,cards>0 且無橫向捲動且 tab 過濾後 >0 才 exit 0。

- [ ] **Step 1: 寫 verify/mobile-check.cjs(先寫驗收腳本)**

```js
// 用法: NODE_PATH=$(npm root -g) node verify/mobile-check.cjs <url>
// 預設用系統 Google Chrome(channel:'chrome');沒裝時 PW_CHANNEL=none 用內建 chromium
const { chromium, devices } = require('playwright');

(async () => {
  const url = process.argv[2] || 'http://localhost:8000/';
  const opts = process.env.PW_CHANNEL === 'none' ? {} : { channel: 'chrome' };
  const browser = await chromium.launch(opts);
  const page = await (await browser.newContext({ ...devices['iPhone 13'] })).newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForSelector('.card', { timeout: 10000 });
  const cards = await page.locator('.card').count();
  const hscroll = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1
  );
  await page.getByRole('button', { name: '發文前檢測' }).tap();
  const afterTab = await page.locator('.card').count();
  console.log(JSON.stringify({ cards, hscroll, afterTab }));
  await browser.close();
  if (!cards || hscroll || !afterTab) process.exit(1);
})().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
```

- [ ] **Step 2: 跑腳本確認它會失敗(index.html 還不存在)**

Run: `cd /home/ct/marketing-toolbox && python3 -m http.server 8000 &` 然後 `NODE_PATH=$(npm root -g) node verify/mobile-check.cjs http://localhost:8000/`
Expected: 非零 exit(waitForSelector `.card` 逾時或 404)。若報 Chrome channel 找不到,改跑 `PW_CHANNEL=none NODE_PATH=$(npm root -g) node verify/mobile-check.cjs http://localhost:8000/`,並在後續所有驗證沿用 `PW_CHANNEL=none`。

- [ ] **Step 3: 寫 index.html(完整內容如下)**

```html
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>行銷工具箱|免費、免註冊的行銷線上小工具</title>
<meta name="description" content="台灣行銷人的免費線上小工具書籤站:素材製作、文案與提示詞、發文前檢測、互動與名單、連結與追蹤。每個工具免費、免註冊、開瀏覽器就能用。">
<link rel="canonical" href="https://yazelin.github.io/marketing-toolbox/">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<meta property="og:type" content="website">
<meta property="og:site_name" content="行銷工具箱">
<meta property="og:title" content="行銷工具箱|免費、免註冊的行銷線上小工具">
<meta property="og:description" content="每個工具點進去就能用:免費、免註冊、開瀏覽器就好。素材、文案、檢測、互動、追蹤五類實測收錄。">
<meta property="og:url" content="https://yazelin.github.io/marketing-toolbox/">
<meta property="og:image" content="https://yazelin.github.io/marketing-toolbox/assets/og.png">
<meta property="og:image:secure_url" content="https://yazelin.github.io/marketing-toolbox/assets/og.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="zh_TW">
<meta name="twitter:card" content="summary_large_image">
<style>
:root {
  --bg: #f6f7f9; --panel: #ffffff; --text: #1c2028; --muted: #5c6470;
  --line: #dde1e7; --accent: #c77800; --accent-ink: #ffffff;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14161c; --panel: #1c1f27; --text: #eceef2; --muted: #9aa1ad;
    --line: #2b2f3a; --accent: #f5a524; --accent-ink: #14161c;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", system-ui, sans-serif;
  line-height: 1.6;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 0 20px; }
header.site { padding: 48px 0 8px; text-align: center; }
header.site h1 { margin: 0; font-size: 2rem; letter-spacing: .05em; }
header.site .tagline { color: var(--muted); margin: 8px 0 0; }
.controls { position: sticky; top: 0; background: var(--bg); padding: 16px 0 12px; z-index: 5; }
#q {
  width: 100%; padding: 10px 14px; font-size: 1rem; color: var(--text);
  background: var(--panel); border: 1px solid var(--line); border-radius: 10px;
}
#q:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
.tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.tabs button {
  padding: 6px 14px; font-size: .95rem; cursor: pointer; color: var(--text);
  background: var(--panel); border: 1px solid var(--line); border-radius: 999px;
}
.tabs button[aria-pressed="true"] { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
#count { color: var(--muted); font-size: .85rem; margin: 10px 0 0; }
.grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px; padding: 16px 0 40px;
}
.card {
  background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
  border-top: 4px solid var(--cat, var(--line));
  padding: 16px; display: flex; flex-direction: column; gap: 8px;
}
.card .meta { display: flex; align-items: center; gap: 8px; font-size: .8rem; color: var(--muted); }
.badge {
  padding: 1px 8px; border-radius: 999px; border: 1px solid var(--line); font-size: .75rem;
}
.badge.tag-自製 { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
.card h3 { margin: 0; font-size: 1.1rem; }
.card .desc { margin: 0; font-size: .95rem; }
.card .usage {
  margin: 0; font-size: .88rem; color: var(--muted);
  border-left: 3px solid var(--cat, var(--line)); padding-left: 10px;
}
.card .actions { margin-top: auto; display: flex; align-items: center; gap: 12px; padding-top: 6px; }
.btn {
  display: inline-block; padding: 7px 16px; border-radius: 10px; text-decoration: none;
  background: var(--accent); color: var(--accent-ink); font-size: .95rem;
}
.card .actions .src { font-size: .85rem; color: var(--muted); }
a { color: var(--accent); }
#empty { display: none; text-align: center; color: var(--muted); padding: 40px 0 60px; }
footer.site {
  border-top: 1px solid var(--line); padding: 28px 0 40px; text-align: center;
  color: var(--muted); font-size: .9rem;
}
footer.site nav { display: flex; justify-content: center; gap: 20px; margin: 10px 0; }
</style>
</head>
<body>
<header class="site wrap">
  <h1>行銷工具箱</h1>
  <p class="tagline">每個工具點進去就能用:免費、免註冊、開瀏覽器就好。</p>
</header>

<div class="controls wrap">
  <input id="q" type="search" placeholder="搜尋工具、用途…" aria-label="搜尋工具">
  <div class="tabs" id="tabs"></div>
  <p id="count"></p>
</div>

<main class="wrap">
  <div class="grid" id="grid"></div>
  <div id="empty">沒有符合的工具。換個關鍵字,或
    <a href="https://github.com/yazelin/marketing-toolbox/issues/new?template=submit-tool.yml">投稿一個</a>?
  </div>
</main>

<footer class="site wrap">
  <p>收錄門檻:免費、免註冊、開瀏覽器就能用——每個外部工具都人工實測過。
    <a href="https://github.com/yazelin/marketing-toolbox/issues/new?template=submit-tool.yml">投稿工具</a></p>
  <nav>
    <a href="https://github.com/yazelin/marketing-toolbox">GitHub</a>
    <a href="https://www.facebook.com/yaze.lin.gm">Facebook</a>
    <a href="https://buymeacoffee.com/yazelin">Buy Me a Coffee</a>
  </nav>
  <p>MIT License © 2026 林亞澤</p>
</footer>

<noscript><p class="wrap" style="text-align:center">本頁需要啟用 JavaScript 才能顯示工具清單。</p></noscript>

<script>
const CATS = ['素材製作', '文案與提示詞', '發文前檢測', '互動與名單', '連結與追蹤'];
const CAT_COLORS = {
  '素材製作': '#e8763a',
  '文案與提示詞': '#8a63d2',
  '發文前檢測': '#2f9e6e',
  '互動與名單': '#d6336c',
  '連結與追蹤': '#3b82c4',
};
const state = { q: '', cat: '全部' };
let tools = [];

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text != null) n.textContent = text;
  return n;
}

function card(t) {
  const c = el('article', 'card');
  c.style.setProperty('--cat', CAT_COLORS[t.category] || 'var(--line)');
  const meta = el('div', 'meta');
  meta.append(el('span', 'badge tag-' + t.tag, t.tag), el('span', null, t.category));
  const actions = el('div', 'actions');
  const go = el('a', 'btn', t.tag === '自製' ? '開啟工具' : '前往工具');
  go.href = t.url;
  go.target = '_blank';
  go.rel = 'noopener';
  actions.append(go);
  if (t.repo) {
    const src = el('a', 'src', '開源 repo');
    src.href = t.repo;
    src.target = '_blank';
    src.rel = 'noopener';
    actions.append(src);
  }
  c.append(meta, el('h3', null, t.name), el('p', 'desc', t.desc), el('p', 'usage', '實戰:' + t.usage), actions);
  return c;
}

function render() {
  const q = state.q.trim().toLowerCase();
  const hits = tools.filter((t) =>
    (state.cat === '全部' || t.category === state.cat) &&
    (!q || [t.name, t.desc, t.usage, t.category, t.tag].join(' ').toLowerCase().includes(q))
  );
  const grid = document.getElementById('grid');
  grid.replaceChildren(...hits.map(card));
  document.getElementById('empty').style.display = hits.length ? 'none' : 'block';
  document.getElementById('count').textContent = '顯示 ' + hits.length + ' / 共 ' + tools.length + ' 個工具';
}

function buildTabs() {
  const tabs = document.getElementById('tabs');
  ['全部', ...CATS].forEach((cat) => {
    const b = el('button', null, cat);
    b.setAttribute('aria-pressed', String(cat === state.cat));
    b.addEventListener('click', () => {
      state.cat = cat;
      tabs.querySelectorAll('button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      render();
    });
    tabs.append(b);
  });
}

document.getElementById('q').addEventListener('input', (e) => {
  state.q = e.target.value;
  render();
});

buildTabs();
fetch('tools.json')
  .then((r) => r.json())
  .then((data) => { tools = data; render(); })
  .catch(() => {
    document.getElementById('empty').textContent =
      '工具清單載入失敗。本地預覽請用 python3 -m http.server,不能直接開檔案。';
    document.getElementById('empty').style.display = 'block';
  });
</script>
</body>
</html>
```

- [ ] **Step 4: 本地驗證通過**

Run(http.server 若已在跑就不用重啟):
```bash
cd /home/ct/marketing-toolbox
curl -s http://localhost:8000/ | grep -c '<h1>行銷工具箱</h1>'
NODE_PATH=$(npm root -g) node verify/mobile-check.cjs http://localhost:8000/
```
Expected: grep 印 `1`;腳本印 `{"cards":7,"hscroll":false,"afterTab":1}` 且 exit 0(此時「發文前檢測」類只有行銷頁健檢器一個)。

- [ ] **Step 5: 桌機目視檢查**

用瀏覽器(或 chrome-devtools MCP)開 `http://localhost:8000/`:深淺色各看一次(系統主題切換或 DevTools 模擬 prefers-color-scheme),確認 tab 點擊過濾、搜尋「拉霸」剩 1 張卡、footer 三連結在。
Expected: 以上皆成立,無 console error。

- [ ] **Step 6: Commit**

```bash
git add index.html verify/mobile-check.cjs
git commit -m "feat(ui): 單檔卡片牆——分類 tab、搜尋、深淺色、footer 三連結 + 手機驗證腳本

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: 視覺資產 favicon.svg + assets/og.png

**Files:**
- Create: `favicon.svg`
- Create: `assets/og.svg`(來源檔,一併 commit)
- Create: `assets/og.png`(inkscape 輸出)

**Interfaces:**
- Consumes: index.html 已引用 `favicon.svg` 與 `assets/og.png`(Task 2 寫死的路徑,不可改名)。

- [ ] **Step 1: 寫 favicon.svg(工具箱圖形,不用 emoji)**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#1a1d24"/>
  <path d="M24 28v-6a8 8 0 0 1 16 0v6" fill="none" stroke="#f5a524" stroke-width="5" stroke-linecap="round"/>
  <rect x="14" y="28" width="36" height="22" rx="5" fill="#f5a524"/>
  <rect x="29" y="34" width="6" height="8" rx="2" fill="#1a1d24"/>
</svg>
```

- [ ] **Step 2: 寫 assets/og.svg**

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#14161c"/>
  <rect width="1200" height="6" fill="#f5a524"/>
  <g transform="translate(92,110)">
    <path d="M28 40v-12a20 20 0 0 1 40 0v12" fill="none" stroke="#f5a524" stroke-width="10" stroke-linecap="round"/>
    <rect y="40" width="96" height="58" rx="12" fill="#f5a524"/>
    <rect x="40" y="56" width="16" height="20" rx="5" fill="#14161c"/>
  </g>
  <text x="92" y="340" font-family="Noto Sans CJK TC" font-weight="700" font-size="104" fill="#f3f4f6">行銷工具箱</text>
  <text x="92" y="425" font-family="Noto Sans CJK TC" font-size="42" fill="#9aa1ad">免費、免註冊、開瀏覽器就能用的行銷小工具</text>
  <text x="92" y="560" font-family="Noto Sans CJK TC" font-size="30" fill="#6b7280">yazelin.github.io/marketing-toolbox</text>
</svg>
```

- [ ] **Step 3: 輸出 PNG 並驗證**

```bash
cd /home/ct/marketing-toolbox
inkscape assets/og.svg --export-type=png --export-filename=assets/og.png --export-width=1200 --export-height=630
python3 -c "import struct,sys; d=open('assets/og.png','rb').read(); w,h=struct.unpack('>II', d[16:24]); print(w,h,len(d)); sys.exit(0 if (w,h)==(1200,630) else 1)"
```
Expected: 印 `1200 630 <bytes>`;bytes 應 < 100000(扁平色 PNG)。若 ≥ 100KB,跑 `optipng assets/og.png`(沒裝就 `convert assets/og.png -colors 64 assets/og.png`)壓到 100KB 內——GitHub Pages 路由對 >100KB 資產很慢。
再目視:`xdg-open assets/og.png`(或 Read 該圖檔)確認中文字有渲染出來、沒有變豆腐框。

- [ ] **Step 4: 本地頁面引用驗證**

Run: `curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/assets/og.png http://localhost:8000/favicon.svg`
Expected: 兩行 `200`。

- [ ] **Step 5: Commit**

```bash
git add favicon.svg assets/og.svg assets/og.png
git commit -m "feat(assets): favicon 與 OG 分享圖(inkscape 由 SVG 輸出)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: 外部工具實測與上架

**Files:**
- Create: `docs/tool-vetting.md`(實測紀錄)
- Modify: `tools.json`(附加通過的外部工具)

**Interfaces:**
- Consumes: Task 1 的 schema 與 `check_tools.py`。
- Produces: `tools.json` 擴充後總數約 17~20;`docs/tool-vetting.md` 每工具一列的實測結果表。

- [ ] **Step 1: 建 docs/tool-vetting.md 表頭**

```markdown
# 外部工具實測紀錄

門檻(全過才上架):免費(免費層可完成核心用途)、免註冊免登入用到結果、開瀏覽器就能用。
實測方式:無痕視窗開網址,不登入,完成一次該工具的核心操作。

| 工具 | 實測日期 | 免費 | 免註冊 | 瀏覽器直開 | 結果 | 備註 |
|------|----------|------|--------|------------|------|------|
```

- [ ] **Step 2: 逐一實測下列候選,記錄到表中**

實測操作(用瀏覽器或 chrome-devtools MCP,一律不登入):

| 候選 | 網址 | 核心操作(要完成才算 PASS) |
|------|------|------|
| Squoosh | https://squoosh.app/ | 丟一張 PNG,壓縮後下載成功 |
| Photopea | https://www.photopea.com/ | 開新畫布,打字,匯出 PNG |
| SVGOMG | https://svgomg.net/ | 貼一段 SVG,優化後複製結果 |
| Excalidraw | https://excalidraw.com/ | 畫兩個方塊連線,匯出 PNG |
| 去背(BiRefNet demo) | https://huggingface.co/spaces/ZhengPeng7/BiRefNet_demo | 上傳一張圖,拿到去背結果 |
| 繁化姬 | https://zhconvert.org/ | 貼一段簡體字,轉出台灣化正體 |
| PageSpeed Insights | https://pagespeed.web.dev/ | 測 yazelin.github.io,拿到手機分數 |
| metatags.io | https://metatags.io/ | 貼網址,看到 OG 預覽 |
| opengraph.xyz | https://www.opengraph.xyz/ | 貼網址,看到 FB/Twitter 卡片預覽 |
| Wheel of Names | https://wheelofnames.com/ | 貼三個名字,轉出一個中獎者 |
| Campaign URL Builder | https://ga-dev-tools.google/campaign-url-builder/ | 填 utm 欄位,產出完整網址 |
| QR 產生器(二擇一) | https://qrcode.antfu.me/ 與 https://www.qrcode-monkey.com/ | 輸入網址,下載 QR 圖;兩個都測,收體驗乾淨的那個 |

判定規則:任一門檻不過 → 表上記 FAIL + 原因,**不上架**;可另找同用途替代(同門檻實測)或該類先缺著。
同場加測自製工具的門檻邊界:LINE 貼圖工作室——無痕開站,不登入,確認免費額度可完成一次產出;不行就從 tools.json 移除並在表上記錄。

- [ ] **Step 3: 通過者寫進 tools.json**

以下是每個候選的預擬條目(desc/usage 已寫好;實測後 FAIL 的整筆刪掉,PASS 的照抄附加到 tools.json 陣列尾端;tag 依實況:有公開 repo 標「開源」並填 repo,否則標「官方」):

```json
[
  {
    "name": "Squoosh",
    "url": "https://squoosh.app/",
    "category": "素材製作",
    "tag": "開源",
    "desc": "Google 出品的圖片壓縮器,拖進來即壓,左右滑動比對畫質",
    "usage": "貼文圖先壓小再上傳,別讓 FB 幫你壓到糊掉",
    "repo": "https://github.com/GoogleChromeLabs/squoosh"
  },
  {
    "name": "Photopea",
    "url": "https://www.photopea.com/",
    "category": "素材製作",
    "tag": "官方",
    "desc": "瀏覽器裡的 Photoshop,開 PSD 改字改圖免安裝",
    "usage": "外包給的 PSD 素材要改一行字,不用等設計師也不用買軟體"
  },
  {
    "name": "SVGOMG",
    "url": "https://svgomg.net/",
    "category": "素材製作",
    "tag": "開源",
    "desc": "SVG 最佳化工具,肉眼無差畫質下把檔案砍到最小",
    "usage": "官網 logo 與圖示上線前過一輪,頁面速度分數有感",
    "repo": "https://github.com/jakearchibald/svgomg"
  },
  {
    "name": "Excalidraw",
    "url": "https://excalidraw.com/",
    "category": "素材製作",
    "tag": "開源",
    "desc": "手繪風白板,畫流程圖與示意圖,匯出 PNG/SVG",
    "usage": "行銷漏斗、活動流程畫成手繪圖,貼進簡報和貼文都親切",
    "repo": "https://github.com/excalidraw/excalidraw"
  },
  {
    "name": "AI 去背(BiRefNet)",
    "url": "https://huggingface.co/spaces/ZhengPeng7/BiRefNet_demo",
    "category": "素材製作",
    "tag": "開源",
    "desc": "開源去背模型線上 demo,上傳圖片直接拿去背結果",
    "usage": "商品照去背做主圖,不用付費去背服務的浮水印贖金",
    "repo": "https://github.com/ZhengPeng7/BiRefNet"
  },
  {
    "name": "繁化姬",
    "url": "https://zhconvert.org/",
    "category": "文案與提示詞",
    "tag": "官方",
    "desc": "簡轉繁加台灣用語在地化,不只換字還換詞",
    "usage": "對岸來的稿發文前過一輪,別讓「視頻」「軟件」漏上你的粉專"
  },
  {
    "name": "PageSpeed Insights",
    "url": "https://pagespeed.web.dev/",
    "category": "發文前檢測",
    "tag": "官方",
    "desc": "Google 官方網頁速度與體驗評分,手機桌機分開看",
    "usage": "活動頁太慢廣告費就白燒,上線前先看手機分數"
  },
  {
    "name": "Metatags",
    "url": "https://metatags.io/",
    "category": "發文前檢測",
    "tag": "官方",
    "desc": "貼網址即時預覽 Google、FB、Twitter 上的分享長相",
    "usage": "發文前先看分享卡片會長怎樣,標題被截斷當場就知道"
  },
  {
    "name": "OpenGraph.xyz",
    "url": "https://www.opengraph.xyz/",
    "category": "發文前檢測",
    "tag": "官方",
    "desc": "OG 標籤檢查器,列出缺哪些標籤與各平台預覽",
    "usage": "分享卡片破圖時來這查是缺 og:image 還是尺寸不對"
  },
  {
    "name": "Wheel of Names",
    "url": "https://wheelofnames.com/",
    "category": "互動與名單",
    "tag": "官方",
    "desc": "名單轉盤抽獎,貼上名字全螢幕轉給大家看",
    "usage": "直播抽獎用它轉,過程全螢幕透明,觀眾才服氣"
  },
  {
    "name": "Campaign URL Builder",
    "url": "https://ga-dev-tools.google/campaign-url-builder/",
    "category": "連結與追蹤",
    "tag": "官方",
    "desc": "Google 官方 UTM 產生器,填欄位組出追蹤網址",
    "usage": "每檔活動連結都加 UTM,GA 才分得出哪篇貼文真的帶單"
  },
  {
    "name": "Anthony 的 QR 工具箱",
    "url": "https://qrcode.antfu.me/",
    "category": "連結與追蹤",
    "tag": "開源",
    "desc": "開源 QR code 產生器,可調樣式與容錯率",
    "usage": "印刷品放的 QR 先在這裡調高容錯率,實體海報掃得動",
    "repo": "https://github.com/antfu/qrcode-toolkit"
  },
  {
    "name": "QRCode Monkey",
    "url": "https://www.qrcode-monkey.com/",
    "category": "連結與追蹤",
    "tag": "官方",
    "desc": "免費 QR code 產生器,可加 logo 換色高解析下載",
    "usage": "要放品牌 logo 的 QR 用這個,免費下載高解析不浮水印"
  }
]
```

(QR 兩個擇一收;若兩個都 PASS,收 qrcode.antfu.me 優先——開源且無廣告。)

- [ ] **Step 4: 驗證**

Run: `python3 check_tools.py && python3 check_tools.py --live && NODE_PATH=$(npm root -g) node verify/mobile-check.cjs http://localhost:8000/`
Expected: `OK: N tools`(N=7+通過數,預期 17~19);--live 全過;mobile-check cards=N、hscroll=false、afterTab=3(發文前檢測應有健檢器+PSI+metatags/opengraph 至少 3 張)。
另外目視:每類在頁面上至少 2 個工具;若「連結與追蹤」只剩 1 個,回 Step 2 找替代候選補測。

- [ ] **Step 5: Commit**

```bash
git add tools.json docs/tool-vetting.md
git commit -m "feat(data): 外部工具實測上架——每筆附實測紀錄,不合門檻者不收

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: 投稿模板 + README 完稿

**Files:**
- Create: `.github/ISSUE_TEMPLATE/submit-tool.yml`
- Create: `README.md`

**Interfaces:**
- Consumes: index.html footer 與空狀態已連到 `issues/new?template=submit-tool.yml`(Task 2 寫死,檔名不可改)。

- [ ] **Step 1: 寫 .github/ISSUE_TEMPLATE/submit-tool.yml**

```yaml
name: 投稿工具
description: 推薦一個行銷人用得上的免費線上小工具
title: "[投稿] 工具名稱"
labels: ["投稿"]
body:
  - type: input
    id: url
    attributes:
      label: 工具連結
      placeholder: https://...
    validations:
      required: true
  - type: dropdown
    id: category
    attributes:
      label: 分類
      options:
        - 素材製作
        - 文案與提示詞
        - 發文前檢測
        - 互動與名單
        - 連結與追蹤
    validations:
      required: true
  - type: textarea
    id: why
    attributes:
      label: 為什麼行銷人需要它
      description: 一兩句實戰場景,例如「抽獎貼文要公開透明的開獎方式」
    validations:
      required: true
  - type: checkboxes
    id: gate
    attributes:
      label: 收錄門檻確認(三項都要成立)
      options:
        - label: 免費(免費額度足以完成核心用途)
        - label: 免註冊、免登入就能用到結果
        - label: 開瀏覽器就能用,不用安裝
```

- [ ] **Step 2: 寫 README.md**

```markdown
# 行銷工具箱 marketing-toolbox

台灣行銷人的免費線上小工具書籤站。

**線上使用:https://yazelin.github.io/marketing-toolbox/**

每個工具的承諾:點進去就能用——**免費、免註冊、開瀏覽器就好**。
每個工具附一句「實戰註解」:行銷上什麼場景用它,不是翻譯官方簡介。

## 分類

| 分類 | 內容 |
|------|------|
| 素材製作 | 圖片、影片、貼圖、壓縮、去背 |
| 文案與提示詞 | AI 提示詞、字體風格、文字轉換 |
| 發文前檢測 | OG 預覽、SEO、速度、行銷頁健檢 |
| 互動與名單 | 抽獎、轉盤、趣味互動素材 |
| 連結與追蹤 | UTM、QR code、短網址 |

## 收錄門檻

三項全部成立才上架,外部工具逐一人工實測(紀錄在 `docs/tool-vetting.md`):

1. 免費——免費額度足以完成核心用途
2. 免註冊、免登入就能用到結果
3. 開瀏覽器就能用,不用安裝

卡片標籤:`自製`(我做的)、`開源`(有公開 repo)、`官方`(原廠免費提供)。

## 投稿工具

知道好工具?[開一張投稿 issue](https://github.com/yazelin/marketing-toolbox/issues/new?template=submit-tool.yml),
或直接 PR 改 `tools.json`(一筆一工具,欄位見下)。

## 開發

零框架、零 build。加工具 = 在 `tools.json` 加一筆:

```json
{
  "name": "工具名(繁中)",
  "url": "https://...",
  "category": "五類之一",
  "tag": "自製|開源|官方",
  "desc": "一句用途",
  "usage": "一句行銷實戰場景",
  "repo": "(選填)https://github.com/..."
}
```

本地預覽與驗證:

```bash
python3 -m http.server 8000   # 開 http://localhost:8000/
python3 check_tools.py        # schema 驗證
python3 check_tools.py --live # 加驗連結活著
```

## 關於作者

林亞澤(Yaze Lin)——工業自動化 SI 轉 AI 應用。

- Blog:https://yazelin.github.io/
- Facebook:https://www.facebook.com/yaze.lin.gm
- Buy Me a Coffee:https://buymeacoffee.com/yazelin

## License

MIT © 2026 林亞澤 (Yaze Lin)
```

- [ ] **Step 3: 驗證 YAML 可解析**

Run: `python3 -c "import yaml,sys; yaml.safe_load(open('.github/ISSUE_TEMPLATE/submit-tool.yml')); print('yaml ok')"`
Expected: `yaml ok`。(機器沒 pyyaml 就 `python3 -c "import json"` 略過,靠上線後開一次投稿頁驗證——Task 7 有這步。)

- [ ] **Step 4: Commit**

```bash
git add .github README.md
git commit -m "docs: README 完稿(收錄門檻/投稿/開發)+ 投稿 issue 模板

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: 建 GitHub repo、推送、開 Pages

**Files:**
- Modify: 無(純 GitHub 操作)

**Interfaces:**
- Produces: 線上站 `https://yazelin.github.io/marketing-toolbox/`,Task 7 驗收對象。

- [ ] **Step 1: 建 repo 並推送**

```bash
cd /home/ct/marketing-toolbox
gh repo create yazelin/marketing-toolbox --public --source . --push \
  --description "行銷工具箱 — 免費、免註冊即用的行銷線上小工具書籤站"
```
Expected: 建立成功並推 main。

- [ ] **Step 2: 設 homepage、topics、建投稿 label**

```bash
gh repo edit yazelin/marketing-toolbox \
  --homepage "https://yazelin.github.io/marketing-toolbox/" \
  --add-topic marketing --add-topic tools --add-topic taiwan --add-topic github-pages
gh label create 投稿 --repo yazelin/marketing-toolbox --color F5A524 --description "工具投稿" --force
```
Expected: 皆成功(label 不建的話 issue 模板的 labels 會被 GitHub 靜默忽略)。

- [ ] **Step 3: 開 GitHub Pages(main 分支根目錄)**

```bash
gh api -X POST repos/yazelin/marketing-toolbox/pages \
  -f "source[branch]=main" -f "source[path]=/"
```
Expected: HTTP 201 回 JSON。若回 409 表示已開啟,視同成功。

- [ ] **Step 4: 等 Pages 上線**

```bash
for i in $(seq 1 20); do
  code=$(curl -s -o /dev/null -w '%{http_code}' https://yazelin.github.io/marketing-toolbox/)
  echo "try $i: $code"; [ "$code" = 200 ] && break; sleep 15
done
```
Expected: 幾分鐘內出現 `200`。20 次(5 分鐘)還不到 200 就 `gh api repos/yazelin/marketing-toolbox/pages` 看 status 排查。

---

### Task 7: 上線驗收 + 驗證清單

**Files:**
- Create: `docs/launch-verification.md`(驗收結果紀錄)

**Interfaces:**
- Consumes: Task 2 的 mobile-check.cjs、Task 1 的 check_tools.py、線上站。

- [ ] **Step 1: 自動化驗收三連發**

```bash
cd /home/ct/marketing-toolbox
python3 check_tools.py --live
NODE_PATH=$(npm root -g) node verify/mobile-check.cjs https://yazelin.github.io/marketing-toolbox/
curl -s -o /dev/null -w '%{http_code}\n' https://yazelin.github.io/marketing-toolbox/assets/og.png
```
Expected: `OK: N tools`;mobile-check hscroll=false、cards=N、afterTab>=3、exit 0;og.png `200`。

- [ ] **Step 2: 行銷頁健檢器自檢(吃自家狗糧)**

用瀏覽器(或 chrome-devtools MCP)開 `https://yazelin.github.io/marketing-page-checker/`,貼入 `https://yazelin.github.io/marketing-toolbox/` 執行檢查。
Expected: OG 與 SEO 區無紅字(og:image/寬高/site_name/description/canonical Task 2 都齊了)。有紅字就修 index.html 的 meta → commit → push → 等 Pages 更新(快取約 10 分鐘)→ 重驗。

- [ ] **Step 3: 人工點驗**

線上站逐項確認:footer 三連結各點一次可達;「投稿工具」連結開得出 issue 表單(欄位齊全);tab 與搜尋在線上版正常;深淺色各看一次。
Expected: 全過。

- [ ] **Step 4: 寫 docs/launch-verification.md**

記錄格式(填實際結果):

```markdown
# 上線驗收 2026-07-15

| 驗收項 | 方式 | 結果 |
|--------|------|------|
| tools.json schema + 連結活著 | check_tools.py --live | OK: N tools |
| 手機 RWD(iPhone 13) | verify/mobile-check.cjs 線上跑 | cards=N, hscroll=false |
| OG/SEO | marketing-page-checker 自檢 | 無紅字 |
| OG 圖 | curl assets/og.png | 200 |
| footer 三連結 | 人工點擊 | 皆可達 |
| 投稿表單 | 開 issue 模板頁 | 欄位齊全 |
| FB 分享卡片 | FB Sharing Debugger | 待 yazelin 人工(需 FB 登入) |
```

- [ ] **Step 5: Commit + push**

```bash
git add docs/launch-verification.md
git commit -m "docs: 上線驗收紀錄

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
git push
```

- [ ] **Step 6: 交辦事項回報**

回報 yazelin:站已上線 + 驗收表 + 唯一待人工項:用 FB Sharing Debugger(需 FB 登入)貼 `https://yazelin.github.io/marketing-toolbox/` 確認分享卡片,首次抓取若無圖按一次「再次抓取」。
