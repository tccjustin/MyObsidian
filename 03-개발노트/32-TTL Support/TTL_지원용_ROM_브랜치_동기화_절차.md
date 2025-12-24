# TTL 지원용 ROM 브랜치 동기화 절차 (release/1.0.0-pre)

## 목적
- TTL 지원용 ROM 파일 생성/빌드를 위해, 작업 디렉토리(`linux_yp4.0_cgw_1.0.0_pre`)에서 **모든 repo를 동일한 release 브랜치로 맞춘다**.

## 작업 디렉토리
- `linux_yp4.0_cgw_1.0.0_pre`

## 절차

### 1) manifest 기준으로 최신화
```bash
repo sync
```

### 2) 모든 git repo를 release 브랜치로 일괄 체크아웃
```bash
repo forall -c 'git checkout -B release/1.0.0-pre origin/release/1.0.0-pre'
```

## 확인(권장)
- 각 repo가 동일 브랜치로 맞춰졌는지 확인:

```bash
repo forall -c 'echo -n "$REPO_PATH: "; git branch --show-current'
```

## 주의사항 / TODO
- `origin/release/1.0.0-pre`가 없는 repo가 있을 수 있음 → 그 repo는 별도 처리 필요
- 이후 ROM 생성/빌드 커맨드(예: build script/bitbake/fwdn 산출물 경로)는 이 문서에 추가 필요


