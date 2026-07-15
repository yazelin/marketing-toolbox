# marketing-toolbox 行銷工具箱 — 設計 spec

日期:2026-07-15
狀態:已與 yazelin 逐項拍板

## 1. 定位與目標

台灣行銷人的**免費線上小工具書籤站**,GitHub Pages 純靜態站。

雙重目標(同等重要):

- **對外導流資產**:經營成行銷人常回訪的書籤站,自製工具卡片即自家作品展示;footer 走既定推廣三連結(GitHub / FB / BMC)。
- **自用工具箱**:yazelin 自己做行銷素材時的快速取用入口。

**信任承諾(對訪客的一句話)**:站上每個工具都是「點進去、開瀏覽器就能用——免費、免註冊」。

**差異化**:每個工具附一句繁中**實戰註解**(行銷上什麼場景用它),不是翻譯官方簡介。這是跟隨便一個 awesome list 的根本差別。

## 2. 收錄門檻(硬規則)

外部工具必須同時滿足,**上架前逐一人工實測**:

1. 免費(免費層足以完成該工具的核心用途)
2. 免註冊、免登入即可用到結果
3. 開瀏覽器就能用(不用裝東西)

開源優先但不強制;官方免費工具(如 Google 的 Campaign URL Builder)合門檻就收。
反例:Meta 分享除錯器要登 FB 帳號 → 不收。

每張卡片標 tag:`自製` / `開源` / `官方`。

## 3. 分類(依行銷工作流,五類)

| 分類 | 涵蓋 | 自家主力 |
|------|------|----------|
| 素材製作 | 圖、影片、貼圖、壓縮、去背 | emoji-slot-machine、line-sticker-studio |
| 文案與提示詞 | 提示詞產生、字體風格、文字轉換 | PromptFill、ai-font-styles |
| 發文前檢測 | OG 預覽、SEO、速度、健檢 | marketing-page-checker |
| 互動與名單 | 抽獎、轉盤、quiz、趣味分享 | what-to-eat、div-smash |
| 連結與追蹤 | 短網址、QR code、UTM | (首發以外部工具為主) |

## 4. 技術選型

**單檔 `index.html` + `tools.json`,零框架、零 build**(與 web-effects-collector 同哲學)。

- 分類 tab、關鍵字搜尋、卡片牆,全用原生 JS 讀 JSON 渲染。
- 加一個工具 = 改一筆 JSON,不動 HTML。
- 已否決:Jekyll(build 層多餘,filter 仍要 JS)、Astro(卡片牆用不上)。

## 5. 資料架構

`tools.json`,一筆一工具,自製與外部同一 schema(混合式靠 tag 區分,不做兩套邏輯):

```json
{
  "name": "emoji 拉霸機",
  "url": "https://yazelin.github.io/emoji-slot-machine/",
  "category": "素材製作",
  "tag": "自製",
  "desc": "3×3 emoji 拉霸動畫影片產生器",
  "usage": "FB 抽獎貼文用它做會動的開獎影片,比純文字貼文停留久",
  "repo": "https://github.com/yazelin/emoji-slot-machine"
}
```

欄位:`name`(繁中)、`url`、`category`(五類之一)、`tag`(自製/開源/官方)、`desc`(一句用途)、`usage`(一句實戰註解)、`repo`(有開源 repo 才填,選填)。

## 6. 頁面設計

單頁卡片牆:

- 頂部:站名「行銷工具箱」+ 一句信任承諾 + 搜尋框
- 分類 tab(全部 + 五類),點擊過濾
- 卡片:工具名、tag 徽章、desc、usage、CTA(自製=「站內開啟」語感,外部=「前往」);有 repo 的附 GitHub 小連結
- RWD(手機單欄)、深淺色主題(prefers-color-scheme)
- OG/SEO meta 齊全;上線後用自家 marketing-page-checker 驗自己
- 無重資產:v1 不放工具截圖,純文字卡片 + 分類色

## 7. 首發內容

自製工具 7 個(上架前逐一驗 Pages 還活著):

1. emoji-slot-machine — 素材製作
2. line-sticker-studio — 素材製作
3. ai-font-styles — 文案與提示詞
4. PromptFill — 文案與提示詞
5. marketing-page-checker — 發文前檢測
6. what-to-eat — 互動與名單
7. div-smash — 互動與名單

外部工具:每類補 3~5 個。候選(**僅為方向,上架前逐一實測「免費+免註冊」,不合就換**):

- 素材製作:Squoosh、Photopea、SVGOMG、Excalidraw
- 文案與提示詞:繁化姬(zhconvert)
- 發文前檢測:PageSpeed Insights、metatags.io、opengraph.xyz
- 互動與名單:wheelofnames
- 連結與追蹤:Google Campaign URL Builder、開源 QR code 產生器(實測後擇一)

首發總量目標:20~30 個,寧缺勿濫。

自製工具同樣以第 2 節門檻檢視:免註冊可用到結果才上架(line-sticker-studio 以免費額度內可完成一次產出為準;若實測不符,首發先不收)。

## 8. 收集機制

- 手動維護:遇到好工具加一筆 `tools.json`,PR 或直接 commit。
- 投稿管道:GitHub issue 模板,欄位=工具連結、屬哪類、為什麼行銷人需要它。
- README 寫明收錄三條件與投稿方式。
- 自動掃描 pipeline:不做,等有回訪流量再評估。

## 9. 慣例(既定規矩,照辦)

- MIT 授權,著作權人林亞澤
- footer 推廣三連結:GitHub / FB / BMC
- 站內文案不用 emoji(工具本身內容如 emoji-slot-machine 的 emoji 不在此限)
- 全站正體中文
- 資產連結不加 cache-busting 參數

## 10. 首版不做

- 後端、任何 Worker
- 訪客分析
- 英文版 i18n
- 工具截圖/縮圖
- 自動掃描收集 pipeline
- 評分、留言、排序演算法

## 11. 驗收標準

- GitHub Pages 上線,首頁可開、五類 tab 與搜尋可用
- `tools.json` 每筆外部工具都經人工實測:免費、免註冊、瀏覽器直開
- 自製工具 7 個連結逐一點開確認活著
- 手機 RWD 用 Playwright iPhone 13 profile 驗過
- marketing-page-checker 跑本站,OG/SEO 項目過關
- FB 分享除錯器貼站網址,分享卡片正常(此步驟人工)
- footer 三連結齊全
