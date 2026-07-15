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
