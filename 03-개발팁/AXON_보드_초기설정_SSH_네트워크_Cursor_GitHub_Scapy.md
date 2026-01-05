# AXON 보드 초기설정: SSH / 네트워크(ICS) / Cursor·VSCode 서버 / GitHub / Scapy

## 0) 범위
- AXON 보드에서 개발/테스트를 하기 위한 “기본 세팅” 모음
- 본 문서에 포함된 내용:
  - SSH(authorized_keys), known_hosts 트러블슈팅
  - Ethernet IP 설정(임시/영구), Windows 11 ICS(인터넷 공유)
  - 자동 로그인(시리얼 getty)
  - `.cursor-server` / `.vscode-server` 저장 위치 이동(심볼릭 링크)
  - 보드에서 git 사용(yocto 이미지에 git 포함, git config)
  - GitHub SSH 키 생성/권한 설정(※ 개인키 주의)
  - pip / scapy 설치(저장공간 제약 대응)
  - systemd로 부팅 시 스크립트 자동 실행
  - `vi` 터미널 에러(`E437`) 해결, 비밀번호 로그인 전용 ssh config

---

## 1) SSH 설정

### 1.1 `/home/root/.ssh/authorized_keys` 생성

```bash
mkdir -p /home/root/.ssh
chmod 700 /home/root/.ssh
```

`authorized_keys`는 **PC의 공개키(`id_rsa.pub` 또는 `id_ed25519.pub`) 내용**을 복사해서 넣습니다.
문서에는 공개키를 그대로 남기지 말고, 아래처럼 placeholder로 관리하세요.

```bash
cat > /home/root/.ssh/authorized_keys <<'EOF'
ssh-rsa <YOUR_PUBLIC_KEY> <COMMENT>
EOF
```

권한/소유자:

```bash
chmod 600 /home/root/.ssh/authorized_keys
chown -R root:root /home/root/.ssh
```

### 1.2 SSH 트러블슈팅: `REMOTE HOST IDENTIFICATION HAS CHANGED!`
PC에서 아래 경고가 뜨면:

```text
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
Host key verification failed.
```

PC의 `known_hosts`에서 해당 IP(예: `192.168.137.2`) 엔트리를 삭제합니다.

```text
C:\Users\jhlee17\.ssh\known_hosts
```

---

## 2) Ethernet 임시 설정(스크립트)

### 2.1 `/home/root/setip.sh` 생성

```bash
cat > /home/root/setip.sh <<'EOF'
#!/bin/sh
ifconfig eth0 down
ifconfig eth0 192.168.137.2
ifconfig eth0 up

ifconfig eth0 192.168.137.2 netmask 255.255.255.0 up
ip route del default
ip route add default via 192.168.137.1 dev eth0
EOF

chmod +x /home/root/setip.sh
```

---

## 3) Ethernet 영구 설정(systemd-networkd)

### 3.1 위치
- Image boot 후: `/lib/systemd/network/80-eth0.network`
- build 시: Yocto에서 `*.network`를 제공하는 레시피/파일을 수정(프로젝트 구조에 따라 상이)

### 3.2 예시(Static IP)

```conf
[Match]
Name=eth*

[Link]
MACAddress=F4:50:EB:01:02:03
MTUBytes=1500

[Network]
Address=192.168.137.2/24
Gateway=192.168.137.1
```

> Note: MACAddress/Address는 **충돌 고려해서 반드시 적절한 값으로 변경**하여 사용.

### 3.3 `fp0` 세팅 비활성화/원복

```bash
mv /lib/systemd/network/80-fp0.network /lib/systemd/network/80-fp0.network.disabled
```

원복:

```bash
mv /lib/systemd/network/80-fp0.network.disabled /lib/systemd/network/80-fp0.network
```

---

## 4) 자동 로그인(시리얼 getty)

### 4.1 빌드 단계에서 수정(예시)
`serial-getty@.service`의 `ExecStart`에 `-a root`를 추가:

```diff
-ExecStart=-/sbin/agetty -8 -L %I @BAUDRATE@ $TERM
+ExecStart=-/sbin/agetty -8 -a root -L %I @BAUDRATE@ $TERM
```

### 4.2 빌드 이후 수정(예시 경로)
- `/lib/systemd/system/serial-getty@.service`

---

## 5) `.cursor-server` / `.vscode-server` 저장 위치 이동(심볼릭 링크)

```bash
mkdir -p /opt/root/.cursor-server
ln -s /opt/root/.cursor-server /home/root/.cursor-server

mkdir -p /opt/root/.vscode-server
ln -s /opt/root/.vscode-server /home/root/.vscode-server

mkdir -p /opt/root/app
ln -s /opt/root/app /home/root/app
```

추가로 `net-app`도 이동 후 링크:

```bash
mv /home/root/net-app /opt/root/
ln -s /opt/root/net-app /home/root/net-app
```

---

## 6) 보드에서 git 사용을 위한 인터넷(Windows 11 ICS)

### 6.1 개념
- 보드는 보통 Ethernet에 물려있고, PC는 Wi-Fi로 인터넷이 됨
- Windows ICS(인터넷 연결 공유)로 Wi-Fi → Ethernet 공유를 켜야 보드에서 인터넷 사용 가능

### 6.2 Windows 11에서 ICS 켜기(요약)
- `Win + R` → `ncpa.cpl`
- 인터넷 되는 어댑터(보통 Wi-Fi) → 속성 → 공유 탭
- “다른 네트워크 사용자가 … 연결하도록 허용” 체크
- “홈 네트워킹 연결”에서 보드가 연결된 Ethernet 선택
- ICS를 켜면 PC Ethernet IP가 보통 **`192.168.137.1`** 로 설정됨

보드 네트워크 설정(예):

```bash
ifconfig eth0 192.168.137.2 netmask 255.255.255.0 up
ip route del default
ip route add default via 192.168.137.1 dev eth0
echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

### 6.3 NAT 트러블슈팅(메모)
- ICS 설정에서 체크를 껐다가 다시 켜는 방식으로 초기화가 도움이 될 수 있음
- Obsidian 이미지 `![[wifi-인터넷-공유.png]]`가 원문에 있었는데, 현재 Vault에 파일이 없어서 표시가 안 될 수 있습니다.

---

## 7) git 설치/설정

### 7.1 Yocto 이미지에 git 포함(예시)
`.bbappend` 등에서:

```bash
IMAGE_INSTALL:append = " git"
```

### 7.2 git 사용자 정보 설정

```bash
git config --global user.name "jhlee17"
git config --global user.email "jhlee17@telechips.com"
```

---

## 8) GitHub SSH 접속 설정(보드)

### 8.1 키 생성

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### 8.2 권한 설정(중요)

```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

> **주의**: 개인키(`id_ed25519`) 원문을 문서/레포에 남기지 않습니다.

---

## 9) pip / scapy 설치(공간 제약 대응)

### 9.1 pip 부트스트랩 및 `/opt/pylib`에 설치

```bash
python3 -m ensurepip
mkdir -p /opt/pylib
python3 -m pip install --no-cache-dir --target /opt/pylib pip setuptools wheel
python3 -m pip --version
```

현재 세션에서만 적용:

```bash
export PYTHONPATH=/opt/pylib:$PYTHONPATH
```

영구 적용은 `.bashrc` 등에 기록.

### 9.2 scapy 설치

```bash
export TMPDIR=/tmp
python3 -m pip install --no-cache-dir --target /opt/pylib scapy
```

---

## 10) 부팅 시 스크립트 자동 실행(systemd)

### 10.1 스크립트 작성(예: `/usr/local/bin/test.sh`)

```bash
mkdir -p /usr/local/bin
nano /usr/local/bin/test.sh
```

```bash
#!/bin/sh
echo "테스트 스크립트 실행됨 $(date)" >> /var/log/test.log
# 실제 실행할 커맨드들...
```

```bash
chmod +x /usr/local/bin/test.sh
```

### 10.2 systemd 유닛 작성

```bash
nano /etc/systemd/system/test.service
```

```ini
[Unit]
Description=My Test Script at Boot
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/test.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

등록/실행:

```bash
systemctl daemon-reload
systemctl enable test.service
systemctl start test.service
```

확인:

```bash
journalctl -u test.service -b
cat /var/log/test.log
```

---

## 11) 기타 팁

### 11.1 `vi` 에러: `E437: Terminal capability "cm" required`
TERM 설정이 맞지 않을 때 발생할 수 있음:

```bash
export TERM=xterm
```

### 11.2 SSH를 비밀번호로만 접속하고 싶을 때
`~/.ssh/config` 예시:

```sshconfig
Host axon-board
    HostName 192.168.137.3
    User root
    PubkeyAuthentication no
    PreferredAuthentications password
```

권한:

```bash
chmod 600 ~/.ssh/config
```

---

## 관련 문서
- TPA/PHY/ACL 관련은 아래로 분리:
  - `03-개발팁/AXON_TPA_ACL_PHY_MasterSlave_설정.md`


