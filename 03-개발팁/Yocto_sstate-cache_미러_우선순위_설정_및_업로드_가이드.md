# Yocto sstate-cache 미러 우선순위 설정 및 업로드 가이드

## 1) 목적
- 빌드 시간을 줄이기 위해 **sstate-cache를 로컬 미러 우선**으로 사용하고,
- 필요 시 `rnd-file.telechips.com`(사내 파일서버)로 **sstate-cache 업로드**하는 절차를 정리합니다.

## 2) 관련 경로 메모 (linux-telechips 소스 위치 예시)
- workspace:
  - `/home/B030240/work1/ext-test/my-yocto1/build-axon/linux_yp4.0_cgw_1.x.x_dev/build/tcn1000/workspace/sources/linux-telechips`
- external-workspace:
  - `/home/B030240/work1/ext-test/my-yocto1/build-axon/linux_yp4.0_cgw_1.x.x_dev/external-workspace/tcn1000/sources/linux-telechips`

## 3) SSTATE_MIRRORS 설정 (로컬 미러 최우선)
`conf/local.conf` 등에 아래처럼 설정합니다.

```conf
# 기존 설정을 유지하면서 로컬 미러를 최우선으로 추가
SSTATE_MIRRORS = "file://.* file:///path/to/your/sstate-mirror/PATH \n"
SSTATE_MIRRORS += "file://.* http://rnd-file.telechips.com/4.0/PATH"
```

### 포인트
- 첫 번째 줄의 `file:///...`가 **로컬 미러(최우선)** 입니다.
- 두 번째 줄은 **원격 미러(차선)** 입니다.
- `/path/to/your/sstate-mirror/`는 실제 로컬 sstate 미러 경로로 치환합니다.

## 4) (예시) linux-telechips sstate 재생성 후 업로드
커널 패키지 이름이 확실치 않다면(메모 기준), 우선 `linux-telechips`를 대상으로 진행합니다.

### 4.1) sstate 정리(재생성 유도)

```bash
bitbake -c cleansstate linux-telechips
```

### 4.2) sstate-cache 업로드
아래 중 **실제 sstate-cache가 있는 경로**에 맞춰 사용합니다.

```bash
scp -r build/sstate-cache-*/* FS_ADMIN@rnd-file.telechips.com:/DATA1/files/4.0
```

또는:

```bash
scp -r sstate-cache/* FS_ADMIN@rnd-file.telechips.com:/DATA1/files/4.0
```

## 5) 주의사항
- 계정/경로/서버 정책은 프로젝트/조직에 따라 다를 수 있으니, 업로드 위치(`/DATA1/files/4.0`)는 운영 규정에 맞는지 확인합니다.
- 문서에 **토큰/패스워드 같은 시크릿을 원문으로 기록하지 않습니다.**


