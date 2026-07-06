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

참고: Claude(Cowork)의 샌드박스 환경에서는 outbound 네트워크가 allowlist로 제한되어
있어, 이 스크립트를 bash로 직접 실행하면 techblogposts.com 요청이 프록시에서 차단될
수 있습니다. Cowork의 매일 09:00 자동화 작업은 이 스크립트 대신 브라우저(Claude in
Chrome)의 fetch()로 동일한 /api/v1/posts 엔드포인트를 호출하는 방식을 사용합니다.
이 스크립트는 사용자의 로컬 머신 등 네트워크 제약이 없는 환경에서 그대로 사용할 수
있도록 남겨둔 참고/백업용 구현입니다.

velopers.kr 병합: velopers.kr(https://www.velopers.kr/)은 techblogposts.com과 별도의
두 번째 소스로, 커서 API 대신 목록 페이지(`/?page=N`, 발행일 내림차순)를 순회해 대상
날짜의 글을 찾고, 각 글의 상세 페이지(`/post/{id}`)에서 원문 링크와 요약을 가져옵니다.
두 소스 결과는 원문 링크 기준으로 중복 제거한 뒤 합쳐 하루치 파일을 만듭니다. 이 스크립트
자체는 techblogposts.com 전용이며, velopers.kr 수집 로직은 자동화 작업(스케줄 프롬프트)
안에 동일한 브라우저 fetch 방식으로 구현되어 있습니다.
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
