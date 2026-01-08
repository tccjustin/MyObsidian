# Git 브랜치 생성/네이밍 규칙 조사 (이 Vault 기준)

## 결론
- 현재 워크스페이스(Obsidian Vault) 안에서 **“브랜치 생성/네이밍 규칙”을 명시적으로 정의한 단일 문서/규칙 파일은 확인되지 않았습니다.**
- 대신, 일부 개발 노트/대화 로그에 **관례적으로 사용된 브랜치명 패턴 사례**(예: `release/...`, `feature/...`, `SD710XL-...`)가 흩어져 있습니다.

---

## 확인한 범위
- `.cursorrules`: AI 동작/문서화 스타일만 있고, Git 브랜치 규칙은 없음
- `ai/`: `index.md`, `jira-jql.md`, `00-index-workflow.md`에 브랜치 규칙 항목 없음

---

## “규칙에 가까운” 참고 사례(문서/노트)

### 1) 릴리즈 브랜치를 모든 repo에 맞추는 절차(특정 작업 절차)
- `02-개발노트/22-TTL Support/TTL_지원용_ROM_브랜치_동기화_절차.md`
  - 예: `release/1.0.0-pre`
  - 내용은 “네이밍 규칙”이라기보다, TTL ROM 지원을 위한 **동기화/체크아웃 절차**에 가깝습니다.

### 2) 원격 브랜치 목록에 등장하는 네이밍 사례(대화/메모)
- `chatgpt/2025-11-14-리눅스_파일_복사.md`
  - 예시로 등장: `origin/SD710XL-1670-standalone-demo`, `origin/SD710XL-1725-yocto-build-source-mirror-down`,
    `origin/feature/SD710XL-1662-cmr-250910`, `origin/qa/SD710XL-1751-linux_yp4.0_cgw_1.0.0`, `origin/release/1.0.0-pre` 등
  - 역시 “워크스페이스 규칙”이라기보다는 특정 상황의 설명/예시입니다.

---

## 정리(현재 상태)
- **공식 규칙 파일**: 없음(최소한 `ai/*`, `.cursorrules` 기준)
- **관례적 패턴(추정)**: `release/<version>`, `feature/<JIRA-KEY>-<desc>` 또는 `SDxxxx-<desc>` 형태가 실제 리포/환경에서 사용된 흔적은 있음
  - 단, 이는 “이 Vault에서 정한 규칙”이 아니라, “어딘가(원격/업무 환경)에서 사용된 브랜치명 사례”로 보는 게 안전합니다.

---

## 확인 질문(규칙을 새로 만들지 여부)
원하시면 이 Vault의 `ai/`에 **Git 브랜치 규칙(네이밍/생성/PR 흐름)** 문서를 새로 만들 수 있는데,
아래 중 어느 쪽이 맞나요?

1) “규칙은 이미 사내/팀에 있는데, 이 Vault 안에 문서만 없는 상태” → 기존 규칙(예: Confluence 페이지/팀 컨벤션)을 알려주시면 Vault에 반영  
2) “이 Vault 자체의 규칙을 새로 정하고 싶다” → 기본안(예: `feature/<JIRA>-<short-desc>`, `fix/<JIRA>-...`, `release/<ver>`, `wip/<name>-...`)을 제안하고 확정해 문서화



