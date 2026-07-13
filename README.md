# tech_blog_letter

[TechBlogPosts](https://www.techblogposts.com/ko)와 [Velopers](https://www.velopers.kr/)에 매일 올라오는 국내 기술 블로그 글을 모아, 하루 단위 파일로 자동 정리하는 저장소입니다. 두 소스에 모두 있는 글은 원문 링크 기준으로 중복 제거한 합집합(union)으로 관리합니다.

## 저장소 구조

```
tech_blog_letter/
├── README.md
├── posts/
│   └── YYYY-MM-DD.md   # 해당 날짜(KST)에 발행된 글 모음(두 소스 합집합). 글이 없는 날은 파일을 만들지 않음
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

- **techblogposts.com**: 참조 https://www.techblogposts.com/ko , RSS https://www.techblogposts.com/rss.xml (최신 10건만 제공). RSS로 커버되지 않는 과거 구간은 내부적으로 사용하는 `/api/v1/posts` 엔드포인트를 커서 기반(`cursor={timestamp}:{url}`)으로 순회하여 수집합니다.
- **velopers.kr**: 참조 https://www.velopers.kr/ , RSS https://www.velopers.kr/rss.xml . 목록 페이지(`/?page=N`)가 발행일 내림차순으로 정렬되어 있어, 대상 날짜 범위에 들어올 때까지 페이지를 순회하며 수집합니다. 각 게시글 상세 페이지(`/post/{id}`)의 원문 링크·두줄요약·핵심내용·태그를 기반으로 정리합니다.
- 두 소스에서 수집한 글은 원문(원저작자) 링크를 기준으로 중복을 제거해 합집합으로 병합합니다.
- 가능하면 각 글의 원문에 직접 접속해 본문을 확인한 뒤 요약 / 주목 포인트 / keyword를 작성하며, 원문 접근이 제한된 경우 그 사실을 명시합니다.

## 자동화

매일 09:00 KST에 스케줄 작업이 실행되어, 전일(KST) 발행된 글을 techblogposts.com과 velopers.kr에서 각각 수집·중복 제거한 뒤 `posts/`에 파일을 추가하고 GitHub에 커밋·푸시합니다. 해당 날짜에 새 글이 없으면 파일을 생성하지 않습니다. 푸시가 끝나면 그날의 글 모음과 요약을 Telegram으로 전송합니다.

무인 실행 특성상 사람이 권한 프롬프트에 응답할 수 없으므로, FUSE 마운트 환경에서 죽은 프로세스가 남긴 stale `.git/*.lock` 파일을 `rm -f`로 정리하는 것만 `.claude/settings.json`의 `permissions.allow`에 좁게 허용해두었습니다(2026-07-08).

Claude in Chrome 도구(navigate, get_page_text, javascript_tool 등)로 브라우저를 직접 조작해 수집하는 경우, 작업이 끝나면 사용한 탭을 모두 닫아 탭 그룹을 정리합니다(`tabs_close_mcp`로 그룹의 마지막 탭을 닫으면 그룹이 자동 제거됨). 다음 실행을 위해 브라우저 탭을 열어둔 채로 세션을 끝내지 않습니다(2026-07-13).
