# 外部工具實測紀錄

門檻(全過才上架):免費(免費層可完成核心用途)、免註冊免登入用到結果、開瀏覽器就能用。
實測方式:全新瀏覽器 context(無任何登入狀態),不登入,完成一次該工具的核心操作。
實測工具:Playwright + Chrome,截圖存查。

| 工具 | 實測日期 | 免費 | 免註冊 | 瀏覽器直開 | 結果 | 備註 |
|------|----------|------|--------|------------|------|------|
| Squoosh | 2026-07-15 | 過 | 過 | 過 | PASS | 上傳本站 og.png 實壓:52.9kB→24.9kB(-53%),可下載 |
| Photopea | 2026-07-15 | 過 | 過 | 過 | PASS | 免登入直接進編輯器,Account 為選配 |
| SVGOMG | 2026-07-15 | 過 | 過 | 過 | PASS | 首屏 demo 即展示優化結果 8.54k→5.03k(-58.9%),含下載/複製 |
| Excalidraw | 2026-07-15 | 過 | 過 | 過 | PASS | 免登入畫布直開(含 zh-TW 介面),實際畫出矩形 |
| AI 去背 BiRefNet demo | 2026-07-15 | 過 | 過 | 過 | PASS | 匿名上傳→ZeroGPU 推論→去背結果出現(約 60~120 秒) |
| 繁化姬 | 2026-07-15 | 過 | 過 | 過 | PASS | 「软件/视频/网络」→「軟體/影片/網路」,轉換正確;頁面有贊助廣告 |
| PageSpeed Insights | 2026-07-15 | 過 | 過 | 過 | PASS | 實測 yazelin.github.io 出完整報告(LCP 1.1s、CLS 0.27) |
| Metatags | 2026-07-15 | 過 | 過 | 過 | PASS | 貼網址→Google/X/FB 三平台預覽即出 |
| OpenGraph.xyz | 2026-07-15 | 過 | 過 | 過 | PASS | 掃描+Meta tag inspector 免登入可用;OG 圖產生器是付費上桿,不影響檢查功能 |
| Wheel of Names | 2026-07-15 | 過 | 過 | 過 | PASS | 點轉盤→「We have a winner!」開獎彈窗 |
| Campaign URL Builder | 2026-07-15 | 過 | 過 | 過 | PASS | 填欄位即產出 `?utm_source=facebook&utm_medium=social&utm_campaign=...` |
| Anthony 的 QR 工具箱 | 2026-07-15 | 過 | 過 | 過 | PASS | 輸入本站網址 QR 即時更新(740×740),可下載 |
| QRCode Monkey | 2026-07-15 | 過 | 過 | 過 | 不收 | 功能可用,但 cookie 同意牆+廣告/追蹤重;QR 類二擇一收更乾淨的 antfu 版 |

## 替換紀錄(外部工具 → 自製)

替換鐵律:同一份輸入在「原版 vs 自製版」各跑一次核心操作,自製版贏或平手才替換。

### 2026-07-16:Campaign URL Builder → 行銷連結工具(link-kit)

同輸入對比(url=`https://yazelin.github.io/`、source=facebook、medium=social、campaign 一組):

| 面向 | Google Campaign URL Builder | link-kit |
|------|------|------|
| 產出參數 | `?utm_source=facebook&utm_medium=social&utm_campaign=...` | 相同(平手) |
| 多通路 | 一次一組 | FB/IG/LINE/電子報/YT/Threads 勾選批次(贏) |
| QR | 無 | 每列附 QR,可調尺寸/容錯/顏色(贏) |
| 歷史/匯出 | 無 | localStorage 歷史+複製全部+CSV(贏) |
| 介面/追蹤 | 英文、掛分析 | 繁中、零追蹤(贏) |

結論:替換。驗證:`link-kit/verify/check.cjs` 對線上站 exit 0(rows=3、utm 正確覆蓋、QR 非空、無橫捲)。
antfu QR 工具箱保留不替換:其樣式/藝術 QR 功能自製版沒有,誠實並存。

## 自製工具門檻邊界檢查

| 工具 | 實測日期 | 結果 | 備註 |
|------|----------|------|------|
| LINE 貼圖工作室 | 2026-07-15 | PASS | 無痕免登入顯示「今日免費 AI 剩 1 / 1」「每天 1 次免費…免登入」;另有零成本替代路徑 B(自備 3×3 圖切格),免費層可完成核心用途 |
