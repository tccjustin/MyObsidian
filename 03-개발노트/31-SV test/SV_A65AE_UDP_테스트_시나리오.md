# SV A65AE UDP 테스트 시나리오 (초안)

## 목적
- SV board(A65AE)에서 **master ↔ slave 간 UDP 패킷 기반 테스트(SV TEST)** 동작을 정의/검증한다.

## 구성
- **Master 보드**: slave 보드로 UDP 패킷 송신
- **Slave 보드**: UDP 패킷 수신 후 즉시 동작/응답 수행

## 동작 시퀀스 (현재까지 정리된 내용)
1. **Master → Slave**
   - UDP로 `SV TEST` 패킷을 전송
2. **Slave**
   - UDP 패킷을 수신하면 **즉시** (TODO: 무엇을?) 수행

## 패킷/프로토콜 (TODO)
- **목적지 IP/Port**: TODO
- **송신 주기/타임아웃**: TODO
- **Payload 포맷**: TODO
  - 예: 문자열 `"SV TEST"` 인지 / magic 값+버전+CRC 같은 구조인지

## 기대 동작 (검증 포인트)
- **Master**
  - 패킷 송신 성공 여부(소켓 에러, 라우팅/ARP, NIC up)
- **Slave**
  - 수신 트리거가 정상적으로 동작하는지
  - 수신 직후 수행 동작의 완료 기준/로그/리턴 코드

## 체크리스트
- [ ] Master/Slave IP, Port 확정
- [ ] 패킷 포맷 확정(헤더/필드/엔디안)
- [ ] Slave 수신 후 “바로” 수행하는 액션 정의
- [ ] 성공/실패 판정 기준 정의(응답 패킷 유무, 로그 키워드 등)

## 남은 질문 (작성자 확인 필요)
- Slave가 수신 후 즉시 수행하는 동작은 무엇인가요?
  - 예: ACK 응답 송신? GPIO 토글? 특정 서비스 실행? FW download trigger?
- Master는 응답(ACK)을 기다리나요, 단방향 트리거인가요?


