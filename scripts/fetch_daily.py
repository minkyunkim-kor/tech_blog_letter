#!/usr/bin/env python3
"""
techblogposts.com 에서 특정 날짜(KST)에 발행된 글 목록을 수집하는 스크립트.

techblogposts.com/ko 페이지가 내부적으로 호출하는 /api/v1/posts 엔드포인트는
"{publishDate epoch ms}:{원문 URL}" 형태의 커서로 페이지네이션을 지원한다.
RSS(rss.xml)는 최신 10건만 제공하므로, 이 스크립트는 그 API를 커서로 순회하며
지정한 날짜(KST, 기본값: 어제) 범위에 해당하는 글만 걸러 JSON으로 출력한다.

사용 예:
    python fetch_daily.py                # 어제(KST) 발행 글 수집
    python fetch_daily.py 2026-07-01     # 특정 날짜(KST) 발행 글 수집

출력: 표준출력에 JSON 배열 (title, company, link, publishDate ISO8601)
      해당 날짜에 글이 없으면 빈 배열 []을 출력한다.
"""

import sys
import json
import urllib.request
from datetime import datetime, timedelta, timezone

BASE_URL = "https://www.techblogposts.com/api/v1/posts"
KST = timezone(timedelta(hours=9))


def fetch_page(cursor=None):
    url = BASE_URL
    if cursor:
        url += "?cursor=" + urllib.parse.quote(cursor, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def kst_date_str(epoch_ms):
    dt = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).astimezone(KST)
    return dt.strftime("%Y-%m-%d")


def collect_for_date(target_date_str, max_pages=30):
    """target_date_str: 'YYYY-MM-DD' (KST 기준 날짜)"""
    target_start = datetime.strptime(target_date_str, "%Y-%m-%d").replace(tzinfo=KST)
    target_end = target_start + timedelta(days=1)

    cutoff_ms = target_start.timestamp() * 1000
    upper_ms = target_end.timestamp() * 1000

    collected = []
    cursor = None
    for _ in range(max_pages):
        data = fetch_page(cursor)
        posts = data.get("posts", [])
        if not posts:
            break
        for p in posts:
            if cutoff_ms <= p["publishDate"] < upper_ms:
                collected.append(p)
        last_post = posts[-1]
        if last_post["publishDate"] < cutoff_ms:
            break
        cursor = data.get("cursor")
        if not cursor:
            break

    result = []
    for p in collected:
        result.append(
            {
                "title": p["title"],
                "company": p.get("company"),
                "link": p["id"],
                "publishDate": datetime.fromtimestamp(
                    p["publishDate"] / 1000, tz=timezone.utc
                ).isoformat(),
            }
        )
    # 최신순으로 온 데이터를 오래된 순으로 정렬
    result.sort(key=lambda x: x["publishDate"])
    return result


def main():
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = (datetime.now(KST) - timedelta(days=1)).strftime("%Y-%m-%d")

    posts = collect_for_date(target_date)
    print(json.dumps({"date": target_date, "posts": posts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
