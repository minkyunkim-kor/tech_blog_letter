# tech_blog_letter

[TechBlogPosts](https://www.techblogposts.com/ko)에 매일 올라오는 국내 기술 블로그 글을 모아, 하루 단위 파일로 자동 정리하는 저장소입니다.

## 저장소 구조

```
tech_blog_letter/
├── README.md
├── posts/
│   └── YYYY-MM-DD.md   # 해당 날짜(KST)에 발행된 글 모음. 글이 없는 날은 파일을 만들지 않음
└── scripts/
    └── fetch_daily.py  # techblogposts.com API에서 특정 날짜의 글 목록을 수집하는 스크립트
```

## 일별 파일 포맷

`posts/YYYY-MM-DD.md`에는 해당 날짜(KST 기준)에 발행된 모든 글에 대해 아래 항목을 정리합니다.

- 제목 (원문 링크 포함)
- 회사
- 본문 요약
- 주목할 point
- keyword

## 데이터 수집 방식

- 참조: https://www.techblogposts.com/ko , RSS: https://www.techblogposts.com/rss.xml (최신 10건만 제공)
- RSS로 커버되지 않는 과거 구간은 techblogposts.com이 내부적으로 사용하는 `/api/v1/posts` 엔드포인트를 커서 기반(`cursor={timestamp}:{url}`)으로 순회하여 수집합니다.
- 각 글의 원문에 접속해 본문을 확인한 뒤 요약 / 주목 포인트 / keyword를 작성합니다.

## 자동화

매일 09:00 KST에 스케줄 작업이 실행되어, 전일 발행된 글을 수집하고 `posts/`에 파일을 추가한 뒤 GitHub에 커밋·푸시합니다. 해당 날짜에 새 글이 없으면 파일을 생성하지 않습니다.
