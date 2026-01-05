# AXON TPA 설정: ACL / iport 매핑 / PHY Master-Slave

## 1) 목적
- scapy 등으로 송신한 패킷이 **의도한 포트(emac/HIF)** 로 흐르도록 TPA를 설정/검증하는 메모를 정리합니다.

---

## 2) 포워딩 규칙(메모 기반 개념)
원문 메모는 “src port `11:11`”로 표현되어 있으나, 아래 명령은 `--src_mac=00:...:11:11` 형태이므로
실제로는 **MAC suffix(예: `..:11:11`) 기반**으로 분기하는 규칙으로 보입니다.

- `..:11:11` → `emac1`
- `..:22:22` → `emac2`
- `..:33:33` → `emac3`
- `..:44:44` → `emac4`

각 `emacX`에서 들어온 패킷이 특정 dst MAC으로 들어오면 HIF로 전달.

---

## 3) ACL 설정 예시(`tc-tpa acl add`)

```bash
tc-tpa acl add --id=0 --iport=0x10 --src_mac=00:00:00:00:11:11 --mask_src_mac=ff:ff:ff:ff:ff:ff --fwd_port_list=0x1 --action=forward
tc-tpa acl add --id=1 --iport=0x10 --src_mac=00:00:00:00:22:22 --mask_src_mac=ff:ff:ff:ff:ff:ff --fwd_port_list=0x2 --action=forward
tc-tpa acl add --id=2 --iport=0x10 --src_mac=00:00:00:00:33:33 --mask_src_mac=ff:ff:ff:ff:ff:ff --fwd_port_list=0x4 --action=forward
tc-tpa acl add --id=3 --iport=0x10 --src_mac=00:00:00:00:44:44 --mask_src_mac=ff:ff:ff:ff:ff:ff --fwd_port_list=0x8 --action=forward

tc-tpa acl add --id=4 --iport=0x1 --dst_mac=00:00:00:00:11:11 --mask_dst_mac=ff:ff:ff:ff:ff:ff --fwd_port_list=0x10 --action=forward
tc-tpa acl add --id=5 --iport=0x2 --dst_mac=00:00:00:00:22:22 --mask_dst_mac=ff:ff:ff:ff:ff:ff --fwd_port_list=0x10 --action=forward
tc-tpa acl add --id=6 --iport=0x4 --dst_mac=00:00:00:00:33:33 --mask_dst_mac=ff:ff:ff:ff:ff:ff --fwd_port_list=0x10 --action=forward
tc-tpa acl add --id=7 --iport=0x8 --dst_mac=00:00:00:00:44:44 --mask_dst_mac=ff:ff:ff:ff:ff:ff --fwd_port_list=0x10 --action=forward

tc-tpa acl add --id=8 --iport=0xf --dst_mac=ff:ff:ff:ff:ff:ff --mask_dst_mac=ff:ff:ff:ff:ff:ff --fwd_port_list=0x10 --action=drop
```

---

## 4) iport 매핑(메모)

| iport | description |
| ----- | ----------- |
| 0x10  | HIF         |
| 0x01  | emac1       |
| 0x02  | emac2       |
| 0x04  | emac3       |
| 0x08  | emac4       |

---

## 5) ARP off(예시)

```bash
ip link set dev fp0 arp off
```

---

## 6) PHY Master/Slave 설정

### 6.1 드라이버 코드에서 Master/Slave 지정(메모)
파일: `drivers/tpa/platform/fpga/platform.c`

- 예시(메모): `TPA_EXTPHY_Set_MasterSlaveMode(emac_index, ms_mode)`
  - master: `1`
  - slave: `0`

### 6.2 `local.conf`에서 TPA master 선택(메모)

```conf
TPA_MASTER = "CA65"
#TPA_MASTER = "CM7-1"
#TPA_MASTER = "CM7-2"
```

### 6.3 현재 상태 확인(메모)

```bash
cat /proc/EPP/tpa_status
```

출력에서 `Mode[Slave]` 등으로 확인 가능.

---

## 7) ARL 테이블을 이용한 방법(메모)

```bash
tc-tpa arl add --mac=00:00:00:00:11:11 --fwd_port_list=0x10 --vlanid=1 --action=0 --tc=0 --hif_ch=0
tc-tpa arl add --mac=00:00:00:00:22:22 --fwd_port_list=0x10 --vlanid=1 --action=0 --tc=0 --hif_ch=0
```


