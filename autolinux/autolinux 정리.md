1. 이 프로젝트가 하는 일 (최상위 개념)
목적:
build-autolinux는 Telechips용 Yocto 기반 SDK를 쉽게 다운로드·설정·빌드하기 위한 자동화 툴 세트입니다.
repo + Yocto 환경(poky) + buildtools + source-mirror를 한 번에 세팅
SDK(플랫폼) / Manifest / Machine / Feature / Image 를 인터랙티브하게 선택하고
선택 결과를 autolinux.config로 저장한 뒤, bitbake 빌드까지 자동으로 실행해 주는 런처/오케스트레이션 스크립트입니다.
핵심 진입점:
최상위 실행 파일: ./autolinux (파이썬, 메인 로직)
사용자는 보통 다음 식으로 사용:
./autolinux -c configure : SDK/머신/피처 선택 및 환경 준비
./autolinux -c build : 이미지 빌드
기타: clean, update, devtool, layers, make_fai, make_updatedir, chk_security, upload_sstate, info, modify 등
2. 디렉터리 구조와 각 역할
autolinux (파이썬 메인 스크립트)
CLI 파서, 전체 플로우 제어, repo sync, buildtools 설치, Yocto 빌드 호출까지 모든 오케스트레이션을 담당합니다.
내부적으로:
template/sdk.py와 각종 template/tccxxxx_*.py를 읽어서
지원 SDK 목록, Manifest 목록, Machine 목록, Feature 목록, Build Script 경로, Image 목록을 메모리에 올림
classes/feature.py를 사용해서 Feature on/off, dependency 처리, local.conf/bblayers.conf 수정을 수행
script/*.sh를 호출해서 실제로 bitbake, devtool, bitbake-layers 를 실행
script/ 디렉터리
Yocto 명령을 싸서 호출하는 얇은 shell wrapper 들입니다.
주요 파일:
build_configure.sh
source <buildtools env>
source <poky>/oe-init-build-env build/<machine> ...를 실행해서 conf 디렉터리 생성 및 초기 설정을 수행.
build_image.sh
위와 비슷하게 env를 잡고 bitbake <image or cmd> 를 실행.
devtool.sh
env 설정 후 devtool 명령 실행.
bitbake-layers.sh
env 설정 후 bitbake-layers 명령 실행.
upload_sstate_cache.sh
가장 최근 빌드(build/$MACHINE/tmp/buildstats/.../build_stats)의 Elapsed 시간을 읽어서
20분(1200초) 이상 걸렸으면 build/sstate-cache-* 를 Telechips 파일 서버에 scp 업로드.
auto_completion.sh
bash completion 스크립트로, ./autolinux 의 -c 옵션과 각 커맨드(configure, update, build, clean, modify 등)에 대해 탭 자동완성 제공.
template/ 디렉터리
SDK/플랫폼과 보드별 설정 템플릿입니다.
sdk.py:
SDK 딕셔너리: “adas / ivi / cluster / develop …” 등의 플랫폼별 지원 SDK 리스트
SOURCE_MIRROR, BUILDTOOL: 미리 다운로드 받은 source-mirror, buildtools 경로를 지정해서 링크로 재사용할 수 있게 함.
여러 개의 tccxxxx_linux_*.py, tca200x_linux_adas.py 등:
Machines : 지원하는 Yocto MACHINE 리스트 혹은 패밀리 구조
Manifests, ManifestsURL : 사용할 manifest.xml 목록과 repo url
MainImages, SubImages : main/sub core 에서 선택 가능한 Yocto 이미지들
MainBuildScript, SubBuildScript : main/sub core용 빌드 스크립트 경로
MainFeatures, SubFeatures : 해당 SDK에서 디폴트로 켜거나/끄는 Feature 세트
classes/feature.py + classes/features/*.py
Feature 시스템의 핵심입니다.
classes/features/common.py, dev.py, old.py 및 각 플랫폼별 adas.py, ivi.py, cluster.py, sv.py, dvrs.py, hvp.py, vpu.py 등에서:
MainFeatures, SubFeatures 라는 리스트를 정의
각 항목은 {name, desc, conf, ID, dep, edep, date, commercial, status ...} 형태의 딕셔너리
Feature 클래스는:
여러 Feature 목록을 합쳐서 현재 SDK에 맞는 Feature 목록을 구성
날짜(date 필드)와 SDK 발행일을 비교해 지원 기간 밖인 Feature는 제외
enableFeature, disableFeature 로 Feature on/off 및 의존성/배타성(edep/dep) 처리
write_feature() 로:
선택된 Feature에 따라 local.conf, bblayers.conf 를 파싱/수정
local.conf: # 주석/해제 방식으로 option 토글
bblayers.conf: 레이어 경로를 추가하거나 제거 (meta-dev, meta-dev-module 등 지원)
3. 사용 흐름(Configure → Build → 부가 기능)
1) 초기 설정 (configure)
./autolinux -c configure 실행
read_config(srcdir):
template/sdk.py 의 SDK, BUILDTOOL, SOURCE_MIRROR 로 기본 설정 로딩
setup_configuration():
SDK 선택 (-s 옵션이나 인터랙티브 메뉴)
해당 SDK에 대응되는 template/tccxxxx_*.py 를 import
ManifestURL, SupportedMachineList, SupportedManifestList, MainFeatures, SubFeatures, … 로 세팅
Manifest 선택 (-x 옵션 또는 메뉴)
Machine 선택 (-m 옵션 또는 메뉴, multi/hvp 인 경우는 여러 개 선택 가능)
Feature 선택:
옵션에 -f, -sf 가 있으면 그걸 쓰고
없으면 sel_feature() 로 터미널 UI에서 main/sub feature on/off 선택
선택 결과(SDK, MANIFEST, MACHINE, VERSION, FEATURES, SUBFEATURES)를 autolinux.config에 저장
setup_environment():
repo init -u ManifestURL -m <manifest> + repo sync 로 poky 등 소스 준비
Yocto DISTRO_VERSION 읽어서 Distro 값으로 사용 (예: 5.0 → scarthgap)
source-mirror, buildtools 디렉터리 생성 및
로컬 SOURCE_MIRROR, BUILDTOOL 경로가 있으면 symlink
없으면 Telechips FTP에서 sftp로 mirror 및 buildtools 받아서 설치
setup_build_environment():
script/build_configure.sh를 SDK/MACHINE 조합별로 실행하여 build/<machine>/conf 생성
modify_confs() → Feature.write_feature() + write_local():
local.conf에 DL_DIR, SSTATE_DIR, SOURCE_MIRROR_URL, SDK_VERSION, QA branch, 보드 버전에 따른 dtb 명 등 반영
bblayers.conf에 Feature에 따른 레이어 추가/삭제
sub-core, guest2 등의 보드 구조일 경우 자동으로 sub-core용 conf까지 구성
2) 빌드 (build)
./autolinux -c build
command_build():
먼저 이미지 선택 메뉴를 띄워(main/sub image 리스트 기반)
선택된 이미지 이름을 autolinux.config의 IMAGE 또는 SUBIMAGE에 기록
exec_build():
script/build_image.sh <buildtools_env> <poky_dir> <machine or mc:...> <bitbake command> 호출
multi/hvp, guest2, sub-core가 활성화된 경우:
메인 이미지를 foreground에서 빌드
sub-core/guest2 이미지는 multiprocessing.Process 로 백그라운드 병렬 빌드
빌드 성공 시, build/<mach>/tmp/deploy/images/<mach> 경로들을 요약 출력
3) 부가 기능들
clean:
./autolinux -c clean : 현재 build history(tmp, cache, buildhistory)를 build/delete/<N>/... 로 이동 (recycle)
./autolinux -c clean old : build/delete 자체를 백그라운드에서 삭제
./autolinux -c clean all : build 전체를 삭제 (확인 프롬프트 + timeout)
update:
./autolinux -c update : 설정된 manifest 기준으로 repo sync 다시 수행 (로컬 변경 사라짐)
devtool:
./autolinux -c devtool <args> 혹은 ./autolinux -c devtool sub <args>
script/devtool.sh를 통해 devtool 명령 실행 (sub-core도 지원)
layers:
./autolinux -c layers add-layer 'poky/meta-telechips/...'
상대 경로 poky 또는 layers가 있으면 path/를 앞에 붙여서 사용
script/bitbake-layers.sh로 실제 bitbake-layers 호출
make_fai:
FWDN용 SDdata.fai 생성 (tmp/deploy/fwdn 경로 안내)
make_updatedir:
meta-update feature가 켜져 있을 때, update용 파일 디렉터리(update, update_main, update_sub) 생성
with-subcore일 경우 sub-core update 디렉터리도 병렬로 생성
chk_security:
main/sub 각각에 대해 security flag 결과 csv를 만들기 위한 빌드 수행 후, 결과 경로 안내
upload_sstate:
./autolinux -c upload_sstate:
내부적으로 script/upload_sstate_cache.sh <mach> <Distro> 호출
빌드 시간이 기준 이상이면 sstate-cache를 Telechips mirror 서버에 업로드
info:
현재 autolinux.config 내용을 보기 좋게 출력 (sub-feature 포함 여부에 따라)
modify:
이미 설정된 autolinux.config를 기반으로
modify feature : feature on/off 재선택 후 conf 재생성
modify sub-feature : sub-core feature만 조정
modify image : 이미지만 재선택
modify machine : (단일 SDK일 때) machine 변경
modify version : VERSION(master/qa/release) 변경
4. 정리: 이 프로젝트를 한 문장으로 요약하면
“Telechips 보드를 위한 Yocto SDK를, manifest/머신/feature/이미지 선택부터 repo sync, source-mirror/buildtools 셋업, conf 수정, bitbake 빌드, sstate 업로드까지 한 번에 자동화해 주는 빌드 프레임워크”입니다.
원하시면,
실제로 자주 쓰이는 명령 세트(예: 신규 SDK 환경 셋업부터 이미지 빌드까지 step-by-step 튜토리얼)나
특정 SDK 파일(tcc805x_linux_ivi.py 같은 것)의 구조, 혹은 Feature 시스템(의존성 표현법, edep 규칙)만 따로 더 자세히 풀어서 설명해드릴 수 있습니다.