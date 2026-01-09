---
tags:
  - git
  - commit
  - commit-message
  - convention
  - prefix
  - telechips
---

# Git 커밋 메시지 prefix 분류 규칙: `[bug]` / `[ref]` / `[fea]` / `[upg]`

## 목적
커밋 메시지 앞에 prefix를 붙여 **변경 목적을 빠르게 분류/검색**하기 위한 규칙.

## 규칙(원문)
`commit_classifier = ( "bug" | "ref" | "fea" | "upg" )`  
→ `bug`, `ref`, `fea`, `upg` 중 하나를 선택

## prefix 의미

| prefix | 의미 | 언제 쓰나(요약) |
|---|---|---|
| `[bug]` | 버그 수정 | 오동작/결함/에러 수정, 크래시/누수/오류 수정 |
| `[ref]` | 리팩토링 | 기능 변화 없이 구조 개선, 가독성/유지보수성 개선 |
| `[fea]` | 기능 추가 | 신규 기능/옵션/모듈 추가, 동작 확장 |
| `[upg]` | 개선(기능/성능) | 기존 기능 개선, 성능/안정성/품질 개선(최적화 등) |

## 커밋 메시지 형식(권장)

```text
[<bug|ref|fea|upg>] <한 줄 요약>
```

필요하면 상세 본문을 추가:

```text
[fea] Add SSH key provisioning script

- Add /home/root/.ssh provisioning helper
- Document permissions and ownership
```

## 예시 모음(검색용)
- `[bug] Fix null dereference in tpa driver`
- `[ref] Refactor network setup script for readability`
- `[fea] Add scapy install steps to docs`
- `[upg] Improve boot script reliability and logging`

## 관련 문서
- 커밋 메시지 작성(전체) 정리: `03-개발팁/커밋_메시지_작성_규칙_telechips_wiki_354585711.md`


