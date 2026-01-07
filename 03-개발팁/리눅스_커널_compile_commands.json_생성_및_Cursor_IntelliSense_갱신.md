# 리눅스 커널 `compile_commands.json` 생성 및 Cursor IntelliSense 갱신

## 1) 증상
- `compile_commands.json`을 생성했는데 **빈 파일**이 만들어짐
- Cursor에서 매크로(예: `POLLING_MODE`) 변경 시 IntelliSense가 제대로 따라오지 않음

## 2) 원인
- **소스 디렉토리에서 실행**하여, 빌드 산출물인 `*.cmd` 파일을 찾지 못함  
  (실제 `*.cmd`는 별도의 **빌드 디렉토리**에 존재)

## 3) 해결 절차 (정상 동작 커맨드)
아래처럼 **커널 빌드 디렉토리**에서 실행:

```bash
cd /home/B030240/work1/svfinal2/build/tcn1000-sv/tmp/work/tcn1000_sv-telechips-linux/linux-telechips/5.10.177-r0/build
python3 /home/B030240/work1/svfinal2/build/tcn1000-sv/tmp/work-shared/tcn1000-sv/kernel-source/scripts/clang-tools/gen_compile_commands.py \
  -d . \
  -o /home/B030240/work1/svfinal2/build/tcn1000-sv/tmp/work-shared/tcn1000-sv/kernel-source/scripts/clang-tools/compile_commands.json
```

## 4) 결과 확인
- `compile_commands.json` **10,381줄** 생성
- **TPA 드라이버 152개 항목** 포함
- `drivers/tpa/platform/fpga/platform.c` 포함

## 5) Cursor에서 후속 조치
- **Window Reload**
  - `Ctrl + Shift + P` → `Reload Window`
- 또는 **Cursor 재시작**

## 6) 기대 효과
- 이후 `POLLING_MODE=1` 같은 설정 변경 시, Cursor IntelliSense가 올바르게 인식되어 관련 코드가 활성화된 상태로 표시됨



