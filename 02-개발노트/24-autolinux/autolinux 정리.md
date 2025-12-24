# autolinux 정리 (build-autolinux)

> Telechips용 **Yocto 기반 SDK**를 다운로드/설정/빌드하는 과정을 자동화하는 런처(오케스트레이션) 스크립트.

## 목차
- [1. 이 프로젝트가 하는 일(최상위 개념)](#1-이-프로젝트가-하는-일최상위-개념)
- [2. 디렉터리 구조와 역할](#2-디렉터리-구조와-역할)
- [3. 사용 흐름(Configure → Build → 부가 기능)](#3-사용-흐름configure--build--부가-기능)
- [4. 한 문장 요약](#4-한-문장-요약)

---

## 1. 이 프로젝트가 하는 일(최상위 개념)

### 목적
- `build-autolinux`는 Telechips용 Yocto 기반 SDK를 **쉽게 다운로드·설정·빌드**하기 위한 자동화 툴 세트입니다.
- `repo` + Yocto 환경(`poky`) + `buildtools` + `source-mirror`를 한 번에 세팅합니다.
- SDK(플랫폼) / Manifest / Machine / Feature / Image를 **인터랙티브하게 선택**하고,
  선택 결과를 `autolinux.config`에 저장한 뒤, `bitbake` 빌드까지 자동 실행합니다.

### 핵심 진입점 / 자주 쓰는 커맨드
- 최상위 실행 파일: `./autolinux` (Python, 메인 로직)

```bash
./autolinux -c configure   # SDK/머신/피처 선택 및 환경 준비
./autolinux -c build       # 이미지 빌드
```

### 기타 커맨드(요약)
- `clean`, `update`, `devtool`, `layers`, `make_fai`, `make_updatedir`, `chk_security`, `upload_sstate`, `info`, `modify` 등

---

## 2. 디렉터리 구조와 역할

### 큰 그림
- `./autolinux`가 **전체 플로우(설정 → 소스 준비 → 환경 구성 → 빌드 호출)**를 오케스트레이션합니다.
- 템플릿(`template/*.py`)에서 “지원 가능한 선택지”를 로딩하고,
  Feature 시스템(`classes/feature.py`)으로 `local.conf`/`bblayers.conf`를 수정하며,
  실제 Yocto 명령은 `script/*.sh`로 래핑해서 호출합니다.

### 구성 요소 요약(트리)
```text
autolinux                  # Python 메인 스크립트(오케스트레이션)
script/                    # Yocto 명령 wrapper shell
template/                  # SDK/보드별 설정 템플릿
classes/feature.py         # Feature on/off 및 conf 수정 핵심
classes/features/*.py      # 플랫폼별 Feature 정의 집합
```

### `autolinux` (Python 메인 스크립트)
- CLI 파서, 전체 플로우 제어, `repo sync`, buildtools 설치, Yocto 빌드 호출까지 담당
- 내부 동작(요약):
  - `template/sdk.py` + `template/tccxxxx_*.py` 로딩
  - SDK/Manifest/Machine/Feature/Build Script/Image 목록을 메모리에 구성
  - `classes/feature.py`로 Feature on/off + 의존성/배타성 처리 + `local.conf`/`bblayers.conf` 수정
  - `script/*.sh` 호출로 `bitbake`, `devtool`, `bitbake-layers` 실행

### `script/` (Yocto wrapper shell)
- Yocto 명령을 “환경 준비 + 실행” 형태로 감싼 얇은 wrapper들
- 주요 파일:
  - `build_configure.sh`
    - `source <buildtools env>`
    - `source <poky>/oe-init-build-env build/<machine> ...`
    - `conf/` 생성 및 초기 설정
  - `build_image.sh`
    - 위와 유사하게 env를 잡고 `bitbake <image | cmd>` 실행
  - `devtool.sh`
    - env 설정 후 `devtool` 실행
  - `bitbake-layers.sh`
    - env 설정 후 `bitbake-layers` 실행
  - `upload_sstate_cache.sh`
    - 가장 최근 빌드(`build/$MACHINE/tmp/buildstats/.../build_stats`)의 **Elapsed**를 읽어서
    - **20분(1200초) 이상**이면 `build/sstate-cache-*`를 Telechips 파일 서버로 `scp` 업로드
  - `auto_completion.sh`
    - bash completion 제공 (`./autolinux -c ...` 및 각 서브커맨드 탭 자동완성)

### `template/` (SDK/플랫폼/보드별 템플릿)
- `sdk.py`
  - SDK 딕셔너리: `"adas" / "ivi" / "cluster" / "develop" ...` 등 플랫폼별 지원 SDK 목록
  - `SOURCE_MIRROR`, `BUILDTOOL`: 미리 다운로드된 경로를 지정해 **symlink로 재사용** 가능
- `tccxxxx_linux_*.py`, `tca200x_linux_adas.py` 등
  - `Machines`: 지원 Yocto `MACHINE` 리스트/패밀리 구조
  - `Manifests`, `ManifestsURL`: 사용할 `manifest.xml` 목록과 `repo url`
  - `MainImages`, `SubImages`: main/sub core에서 선택 가능한 Yocto 이미지 목록
  - `MainBuildScript`, `SubBuildScript`: main/sub core용 빌드 스크립트 경로
  - `MainFeatures`, `SubFeatures`: 디폴트 Feature 세트

### Feature 시스템: `classes/feature.py` + `classes/features/*.py`
- Feature 정의는 다음 파일들에 분산됨:
  - `classes/features/common.py`, `dev.py`, `old.py`
  - 플랫폼별 `adas.py`, `ivi.py`, `cluster.py`, `sv.py`, `dvrs.py`, `hvp.py`, `vpu.py` 등
- 이들 파일에서 `MainFeatures`, `SubFeatures` 리스트를 정의
- 각 Feature 항목은 대략 아래 형태의 dict:

```text
{name, desc, conf, ID, dep, edep, date, commercial, status ...}
```

- Feature 클래스 주요 역할:
  - 여러 Feature 목록을 합쳐 “현재 SDK에 맞는 Feature 목록” 구성
  - `date` 필드와 SDK 발행일을 비교해 지원 기간 밖 Feature 제외
  - `enableFeature` / `disableFeature`로 Feature on/off + `dep`/`edep`(의존/배타) 처리
  - `write_feature()`로 선택된 Feature에 따라 conf 수정
    - `local.conf`: `#` 주석/해제 방식으로 option 토글
    - `bblayers.conf`: 레이어 경로 추가/제거 (`meta-dev`, `meta-dev-module` 등)

---

## 3. 사용 흐름(Configure → Build → 부가 기능)

## 3.1 초기 설정: `configure`

```bash
./autolinux -c configure
```

### 1) 기본 설정 로딩
- `read_config(srcdir)`
  - `template/sdk.py`의 `SDK`, `BUILDTOOL`, `SOURCE_MIRROR`로 기본 설정 로딩

### 2) 구성 선택(인터랙티브/옵션)
- `setup_configuration()`
  - SDK 선택: `-s` 또는 메뉴
  - 해당 SDK의 `template/tccxxxx_*.py` import 후 다음 정보 세팅:
    - `ManifestURL`, `SupportedMachineList`, `SupportedManifestList`, `MainFeatures`, `SubFeatures`, ...
  - Manifest 선택: `-x` 또는 메뉴
  - Machine 선택: `-m` 또는 메뉴 (`multi`/`hvp`는 다중 선택 가능)
  - Feature 선택:
    - 옵션 `-f`, `-sf`가 있으면 사용
    - 없으면 `sel_feature()`로 터미널 UI에서 main/sub feature on/off 선택
  - 선택 결과를 `autolinux.config`에 저장:
    - `SDK`, `MANIFEST`, `MACHINE`, `VERSION`, `FEATURES`, `SUBFEATURES`

### 3) 소스/툴 준비
- `setup_environment()`
  - `repo init -u ManifestURL -m <manifest>` + `repo sync`로 `poky` 등 소스 준비
  - Yocto `DISTRO_VERSION`을 읽어 Distro 값으로 사용 (예: `5.0 → scarthgap`)
  - `source-mirror`, `buildtools` 디렉터리 준비
    - 로컬 `SOURCE_MIRROR`/`BUILDTOOL` 경로가 있으면 symlink
    - 없으면 Telechips FTP에서 `sftp`로 mirror/buildtools를 내려받아 설치

### 4) 빌드 환경 구성(conf 생성/수정)
- `setup_build_environment()`
  - `script/build_configure.sh`를 SDK/MACHINE 조합별로 실행 → `build/<machine>/conf` 생성
  - `modify_confs()` → `Feature.write_feature()` + `write_local()`
    - `local.conf`에 `DL_DIR`, `SSTATE_DIR`, `SOURCE_MIRROR_URL`, `SDK_VERSION`, QA branch, 보드 버전에 따른 `dtb`명 등을 반영
    - `bblayers.conf`에 Feature에 따른 레이어 추가/삭제
  - `sub-core`, `guest2` 등 보드 구조일 경우 sub-core용 conf까지 자동 구성

## 3.2 빌드: `build`

```bash
./autolinux -c build
```

### 1) 이미지 선택 및 기록
- `command_build()`
  - main/sub image 리스트 기반으로 이미지 선택 메뉴 표시
  - 선택된 이미지를 `autolinux.config`의 `IMAGE` 또는 `SUBIMAGE`에 기록

### 2) 실제 빌드 실행
- `exec_build()`
  - `script/build_image.sh <buildtools_env> <poky_dir> <machine | mc:...> <bitbake cmd>` 호출
  - `multi/hvp`, `guest2`, `sub-core`가 활성화된 경우:
    - 메인 이미지는 foreground 빌드
    - sub-core/guest2 이미지는 `multiprocessing.Process`로 백그라운드 병렬 빌드
  - 성공 시 `build/<mach>/tmp/deploy/images/<mach>` 경로들을 요약 출력

## 3.3 부가 기능들(요약)
- `clean`
  - `./autolinux -c clean`: 현재 build history(`tmp`, `cache`, `buildhistory`)를 `build/delete/<N>/...`로 이동(recycle)
  - `./autolinux -c clean old`: `build/delete` 자체를 백그라운드에서 삭제
  - `./autolinux -c clean all`: `build` 전체 삭제(확인 프롬프트 + timeout)
- `update`
  - `./autolinux -c update`: 설정된 manifest 기준으로 `repo sync` 재수행(로컬 변경 사라짐)
- `devtool`
  - `./autolinux -c devtool <args>` 또는 `./autolinux -c devtool sub <args>`
  - `script/devtool.sh` 통해 실행(sub-core 지원)
- `layers`
  - `./autolinux -c layers add-layer 'poky/meta-telechips/...'`
  - 상대 경로 `poky`/`layers`가 있으면 앞에 `path/`를 붙여 사용
  - `script/bitbake-layers.sh` 통해 실행
- `make_fai`
  - FWDN용 `SDdata.fai` 생성(`tmp/deploy/fwdn` 경로 안내)
- `make_updatedir`
  - `meta-update` feature가 켜져 있을 때 update용 파일 디렉터리(`update`, `update_main`, `update_sub`) 생성
  - `with-subcore`면 sub-core update 디렉터리도 병렬 생성
- `chk_security`
  - main/sub 각각에 대해 security flag 결과 csv 생성용 빌드 수행 후 결과 경로 안내
- `upload_sstate`
  - `./autolinux -c upload_sstate`
  - 내부적으로 `script/upload_sstate_cache.sh <mach> <Distro>` 호출
  - 빌드 시간이 기준 이상이면 sstate-cache를 Telechips mirror 서버에 업로드
- `info`
  - 현재 `autolinux.config` 내용을 보기 좋게 출력(sub-feature 포함 여부에 따라)
- `modify`
  - 기존 `autolinux.config` 기반으로 변경
    - `modify feature`: feature on/off 재선택 후 conf 재생성
    - `modify sub-feature`: sub-core feature만 조정
    - `modify image`: 이미지만 재선택
    - `modify machine`: (단일 SDK일 때) machine 변경
    - `modify version`: `VERSION(master/qa/release)` 변경

---

## 4. 한 문장 요약
“Telechips 보드를 위한 Yocto SDK를, manifest/머신/feature/이미지 선택부터 `repo sync`, source-mirror/buildtools 셋업, conf 수정, `bitbake` 빌드, sstate 업로드까지 한 번에 자동화해 주는 빌드 프레임워크”

> 원하시면, “신규 SDK 환경 셋업 → 이미지 빌드”까지의 **자주 쓰는 명령 세트 튜토리얼**이나, 특정 SDK 템플릿 파일 구조/Feature 의존성 규칙(`dep`/`edep`)만 따로 더 자세히 정리해드릴 수 있습니다.