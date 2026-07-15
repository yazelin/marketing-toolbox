# 上線驗收 2026-07-15

站:https://yazelin.github.io/marketing-toolbox/

| 驗收項 | 方式 | 結果 |
|--------|------|------|
| tools.json schema + 連結活著 | `check_tools.py --live` | OK: 19 tools |
| 手機 RWD(iPhone 13 模擬) | `verify/mobile-check.cjs` 對線上站 | cards=19, hscroll=false, 檢測 tab=4, exit 0 |
| OG/SEO | 行銷頁健檢器自檢 | 71/100 及格;分享卡 20/20、SEO 18/20(僅 JSON-LD 黃字);CTA/追蹤扣分屬書籤站刻意取捨 |
| OG 圖 | curl assets/og.png | 200(52.9KB,1200×630) |
| favicon | curl favicon.svg | 200 |
| footer 三連結 | curl(瀏覽器 UA) | GitHub / Facebook / BMC 皆 200 |
| 分類 tab + 搜尋(線上) | Playwright 深淺色各跑一次 | 搜「拉霸」=1 卡;「連結與追蹤」tab=2 卡;兩主題皆正常 |
| 深淺色主題 | Playwright colorScheme 截圖 | 皆正常(本地開發時已目視) |
| 投稿表單 | YAML 解析驗證 + 檔案上線 + 「投稿」label 已建 | 通過;表單實際渲染需 GitHub 登入,留人工點一次 |
| FB 分享卡片 | FB Sharing Debugger | 待 yazelin 人工(需 FB 登入) |

## 待人工兩項

1. FB Sharing Debugger 貼 `https://yazelin.github.io/marketing-toolbox/`,首次抓取沒圖就按一次「再次抓取」。
2. 登入 GitHub 開一次「投稿工具」issue 模板頁,確認欄位渲染正常。
