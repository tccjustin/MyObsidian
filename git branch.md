vscode에서 branch 생성하고.. remote server에도 같이 생성시키기.. 

vscode : create new branch
vscode : checkout to that branch
vscode : publish branch

```
  

@startuml

autonumber

actor "Boot ROM/BL1" as ROM

participant "telechips_platform\n(SCP RAM FW)" as PLATFORM

participant "boot_time" as BOOTTIME

participant "PMU module" as PMU

participant "remote_proc" as RPROC

participant "PIC module" as PIC

participant "TCC Mailbox" as MBOX

participant "Transport\n(mod_transport)" as TRANSPORT

participant "SCMI service" as SCMI

participant "Clock HAL\n(mod_clock)" as CLOCK

participant "Clock debug driver" as CLKDBG

participant "OSPM/PSCI Agent" as AGENT

== 초기 진입 & 환경설정 ==

ROM -> PLATFORM: BL1에서 RAM FW로 제어 전달

PLATFORM -> BOOTTIME: add_boot_timestamp()

PLATFORM -> PMU: get_sfmc_topology(), get_boot_fail()

PLATFORM -> PLATFORM: start_procs()

== 이미지 테이블 검사 ==

PLATFORM -> PMU: SNOR topology/LUN 재확인

PLATFORM -> PLATFORM: memcpy image table & tcc_calc_crc32()

PLATFORM -> PLATFORM: rproc_infos 채움 (MCU/CA65 이미지 매핑)

== 원격 코어 부팅 ==

loop 각 이미지 항목

    PLATFORM -> RPROC: rproc_start(core, boot_addr)

    RPROC -> PMU: set_pmu_remap(core, boot_addr)

    RPROC -> BOOTTIME: add_rproc_boot_timestamp(core)

    RPROC -> PMU: set_pmu_sw_reset(sw_rst_id, deassert)

end

== PIC/Interrupt 구성 ==

PLATFORM -> PIC: pic_init(config_pic)

PIC -> PIC: IRQ 리스트 매핑 (Mailbox RX/TX, UART, Timer 등)

PIC -> PIC: 채널 enable

== SCMI 통신 ==

AGENT -> MBOX: Mailbox doorbell (SCMI 요청 기록)

MBOX -> PIC: IRQ raise (CA65 GP0)

PIC -> MBOX: NVIC 라우팅

MBOX -> TRANSPORT: signal_message() (RX ISR)

TRANSPORT -> SCMI: SCMI 메시지 전달

SCMI -> CLOCK: Clock protocol 요청

CLOCK -> CLKDBG: set/get/log rate

CLKDBG --> CLOCK: 결과 반환

CLOCK --> SCMI: 응답 페이로드

SCMI --> TRANSPORT: 응답 완료

TRANSPORT -> MBOX: trigger_event() (Tx→Rx 공유메모리 복사)

MBOX -> AGENT: doorbell + 응답 인터럽트

== 최종 타임스탬프 ==

PLATFORM -> BOOTTIME: add_rproc_boot_timestamp(MCU0)

@enduml
```