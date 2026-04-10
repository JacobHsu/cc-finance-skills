"""
Banini Threads Scraper Report
------------------------------
Scrapes recent posts from @banini31 on Threads and writes
a raw post log to docs/banini.md.

Usage:
    python scripts/banini_report.py [username] [max_scroll]

No API key required. Uses Playwright + headless Chromium.
Prerequisites:
    pip install playwright parsel nested-lookup jmespath
    playwright install chromium
"""

import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

# Add skill scripts to path so we can import scrape_threads
_SKILL_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "skills", "banini", "scripts")
)
sys.path.insert(0, _SKILL_DIR)

from scrape_threads import scrape_profile  # noqa: E402

TW_TZ = timezone(timedelta(hours=8))
DEFAULT_USERNAME = "banini31"
DEFAULT_MAX_SCROLL = 5


def fmt_time(taken_at: int) -> str:
    dt = datetime.fromtimestamp(taken_at, tz=TW_TZ)
    now = datetime.now(TW_TZ)
    delta = (now.date() - dt.date()).days
    if delta == 0:
        label = "今天"
    elif delta == 1:
        label = "昨天"
    else:
        label = dt.strftime("%m/%d")
    return f"{label} {dt.strftime('%H:%M')}（{dt.strftime('%Y/%m/%d %H:%M')}）"


def build_report(posts: list, username: str) -> str:
    now_tw = datetime.now(TW_TZ)

    lines = [
        "# 巴逆逆 Threads 貼文紀錄",
        "",
        f"> 更新時間：{now_tw.strftime('%Y-%m-%d %H:%M')} 台灣時間",
        f"> 帳號：[@{username}](https://www.threads.com/@{username})",
        f"> 本次抓取：{len(posts)} 篇",
        "",
        "---",
        "",
    ]

    if not posts:
        lines += [
            "> ⚠️ 本次未抓取到任何貼文。",
            "> 可能原因：Threads 反爬封鎖、帳號名稱有誤，或網路問題。",
            "",
        ]
    else:
        for post in posts:
            time_str = fmt_time(post.get("taken_at", 0))
            text = (post.get("text") or "").strip()
            likes = post.get("likes", 0)
            replies = post.get("reply_count", 0)
            code = post.get("code", "")

            link = f"[原文](https://www.threads.com/@{username}/post/{code})" if code else ""

            lines += [
                f"### {time_str}",
                "",
                f"> {text}" if text else "> （無文字內容）",
                "",
                f"讚 {likes} ｜ 回覆 {replies}" + (f" ｜ {link}" if link else ""),
                "",
                "---",
                "",
            ]

    lines.append(
        f"*自動產生於 {now_tw.strftime('%Y-%m-%d %H:%M')} 台灣時間。僅供娛樂參考，不構成投資建議。*"
    )

    return "\n".join(lines)


def main() -> None:
    username = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USERNAME
    max_scroll = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAX_SCROLL

    print(f"Scraping @{username} (max_scroll={max_scroll})...")
    posts = asyncio.run(scrape_profile(username, max_scroll))
    own_posts = [p for p in posts if p["author"] == username]
    print(f"Got {len(own_posts)} posts by @{username}")

    report = build_report(own_posts, username)

    output_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "docs", "banini.md")
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report written to {output_path}")

    if not own_posts:
        sys.exit(1)


if __name__ == "__main__":
    main()
