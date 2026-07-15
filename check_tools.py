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
            except urllib.error.HTTPError as e:
                # 403/429 = 反爬蟲/限流,伺服器活著;404/410/5xx 才算死
                if e.code not in (403, 429):
                    errors.append(f"{where}: HTTP {e.code}")
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
