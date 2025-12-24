### TCN1000_Linux_CGW SDK 동작 시나리오 요약

- 출처: [문서 원문](https://wiki.telechips.com/pages/viewpage.action?pageId=590078502)

| 대분류                          | 소분류              | 설명                                          |
| ---------------------------- | ---------------- | ------------------------------------------- |
| 부팅(Boot)                     | 자동 부팅 준비         | 차량 전원 인가 시 CAN/Ethernet 통신 및 스위칭/라우팅 준비     |
| 펌웨어 다운로드(Firmware download)  | FWDN 기록 및 부팅 검증  | SD_Data.fai→eMMC 기록, SNOR 이미지 기록 후 정상 부팅 확인 |
| 스위칭/라우팅(Switching & Routing) | 동종 네트워크 저지연 전달   | 동일 버스 간 데이터 최소 지연 전달                        |
| 스위칭/라우팅(Switching & Routing) | 이종 네트워크 변환 후 전달  | CAN↔Ethernet, CAN↔LIN 등 프레임 변환 후 전달         |
| 스위칭/라우팅(Switching & Routing) | 내부↔외부 데이터 전송     | 차량 내부 네트워크와 외부 네트워크 간 데이터 전송                |
| 스위칭/라우팅(Switching & Routing) | 라우팅 테이블 기반 전달    | 사전 설정된 라우팅 테이블에 따라 목적지로 전달                  |
| 스위칭/라우팅(Switching & Routing) | 라우팅 테이블 실시간 업데이트 | 런타임 라우팅 테이블 변경 지원                           |
| 보안(Security)                 | 전송 보안 적용         | MACSec/IPSec 등 보안 기술 적용                     |
| 보안(Security)                 | 신뢰 실행환경(TEE) 실행  | 보안이 필요한 애플리케이션을 TEE에서 실행                    |
| 침입탐지(IDS)                    | 침입 탐지            | 내/외부 네트워크 전송 데이터 검사로 침입 탐지                  |
| 시큐어 부트(Secure Boot)          | 펌웨어 무결성 검증       | 부팅 단계별 펌웨어 이미지 위·변조 검증 후 진행                 |
| 시스템 업데이트(A/B Update)         | A/B 업데이트         | 네트워크로 펌웨어 다운로드 후 시스템 앱으로 업데이트               |
| 세이프티(Safety)                 | 안전 상태 전이         | 오동작 검출 시 보고 및 Safe/Degraded 상태 진입           |




