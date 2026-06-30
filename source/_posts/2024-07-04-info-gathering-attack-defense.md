---

title: 信息收集攻防技巧详解
tags: \[Web 安全, 信息收集, 渗透测试, 子域名, 指纹识别, 防御]
date: 2024-07-04

---

# 信息收集攻防技巧详解

信息收集（Information Gathering / Reconnaissance）是渗透测试最重要的一步，也是决定攻击成败的关键。攻击者掌握的信息越多，攻击面就越大；防守方隐藏的信息越多，暴露面就越小。本文从攻击与防御双重视角出发，系统梳理信息收集的全链路技术。

## 1. 信息收集概述

### 1.1 信息收集在整个攻击链中的位置

    侦察 → 武器化 → 投递 → 利用 → 安装 → C2 → 行动
      ↑
    信息收集（本阶段）
      ├── 确定目标范围（IP段、域名、子域名）
      ├── 识别技术栈（OS、Web服务器、语言、框架、CMS）
      ├── 发现暴露服务（端口、API、管理后台）
      ├── 搜集敏感信息（源码泄露、配置泄露、员工信息）
      └── 绘制攻击路径（根据收集信息规划下一步）

### 1.2 信息收集分类

    信息收集
    ├── 按交互方式
    │   ├── 被动收集（不直接与目标交互）
    │   │   ├── 搜索引擎 (Google/Bing/Shodan/ZoomEye/Fofa)
    │   │   ├── DNS/Whois 查询
    │   │   ├── 证书透明度日志 (Certificate Transparency)
    │   │   ├── 公共代码仓库 (GitHub/GitLab)
    │   │   ├── 社工库/泄露数据库
    │   │   ├── 公司信息（年报、招聘、官网）
    │   │   └── 第三方服务（CDN、邮件、DNS托管商）
    │   └── 主动收集（直接与目标交互）
    │       ├── 端口扫描 (Nmap/Masscan/Zmap)
    │       ├── 服务识别 (Nmap脚本/banner抓取)
    │       ├── 目录扫描 (dirsearch/gobuster/ffuf)
    │       ├── 指纹识别 (Wappalyzer/WhatWeb)
    │       ├── 子域名爆破 (subfinder/amass)
    │       └── 漏洞扫描 (Nuclei/OpenVAS/AWVS)
    ├── 按目标类型
    │   ├── 网络层：IP段、子网、BGP AS号
    │   ├── 域名层：主域名、子域名、DNS记录
    │   ├── 应用层：端口、服务、框架、CMS、插件
    │   ├── 人员层：员工邮箱、社交账号、组织架构
    │   └── 数据层：泄露代码、配置文件、文档元数据
    └── 按阶段
        ├── 黑盒：从零开始，只知道目标名称
        ├── 灰盒：有一定信息（如内网IP段、员工账号）
        └── 白盒：有完整信息（源码、架构文档）

### 1.3 信息收集原则

- **由外到内**：先外网后内网，先广撒网后精确定位

- **由浅入深**：先被动后主动，先低风险后高风险

- **分类归档**：按 IP/域名/端口/服务/人员分类存储

- **持续迭代**：信息收集是持续过程，每次新发现都可能拓展攻击面

- **交叉验证**：多个信息源交叉验证，排除干扰和蜜罐

---

## 2. 搜索引擎信息收集

### 2.1 Google Hacking (Google Dork)

Google Dork 是最经典的信息收集技术。利用 Google 的高级搜索语法，可以发现大量敏感信息。

#### 核心语法速查

| 语法        | 功能                 | 示例                       |
| ----------- | -------------------- | -------------------------- |
| `site:`     | 限定搜索域名         | `site:example.com`         |
| `intitle:`  | 搜索网页标题         | `intitle:"index of"`       |
| `inurl:`    | 搜索 URL 包含关键词  | `inurl:admin`              |
| `intext:`   | 搜索页面正文         | `intext:"password"`        |
| `filetype:` | 搜索特定文件类型     | `filetype:sql password`    |
| `ext:`      | 同 filetype          | `ext:env DB_PASSWORD`      |
| `-`         | 排除关键词           | `site:example.com -www`    |
| `link:`     | 搜索链接到某域的页面 | `link:example.com`         |
| `cache:`    | 查看 Google 缓存     | `cache:example.com`        |
| `related:`  | 搜索相关网站         | `related:example.com`      |
| `*`         | 通配符               | `"*@example.com" password` |

#### 经典 Google Dork 案例

```bash
# 搜索子域名
site:example.com -www

# 搜索后台登录页面
site:example.com intitle:"login" OR intitle:"后台" OR intitle:"管理"
inurl:admin site:example.com

# 搜索敏感文件
site:example.com filetype:pdf "confidential"
site:example.com filetype:sql "password"
site:example.com filetype:env
site:example.com filetype:log
site:example.com ext:bak OR ext:old OR ext:backup

# 搜索配置文件泄露
site:example.com ext:xml OR ext:conf OR ext:cnf OR ext:reg
site:example.com ext:yml OR ext:yaml

# 搜索数据库文件
site:example.com ext:sql "INSERT INTO" OR "CREATE TABLE"
site:example.com ext:sql | ext:dbf | ext:mdb

# 搜索源码泄露
site:example.com intext:"<?php" intext:"mysql_connect"
site:example.com ext:php intext:"$password"

# 搜索.git/.svn泄露
site:example.com intitle:"Index of /.git"
site:example.com intitle:"Index of /.svn"

# 搜索目录遍历
site:example.com intitle:"Index of /" "parent directory"
site:example.com intitle:"Index of /admin"

# 搜索网络设备/摄像头
site:example.com intitle:"netgear" OR intitle:"cisco"
site:example.com inurl:"/view/viewer_index.shtml"

# 搜索API文档
site:example.com inurl:"/api" OR inurl:"/swagger"
site:example.com intitle:"Swagger UI"

# 搜索邮箱列表
site:example.com intext:"@example.com" filetype:pdf
site:example.com intext:"@example.com" filetype:xlsx

# 搜索错误信息（泄露路径/版本）
site:example.com intext:"Fatal error" OR "Stack trace"
site:example.com intext:"SQL syntax" OR "MySQL error"
site:example.com intext:"Warning: include(" OR "Warning: require("
```

#### Google Hacking 数据库

```bash
# 官方GHDB (Google Hacking Database)
# https://www.exploit-db.com/google-hacking-database

# 按分类浏览：
# - Footholds (入口点)
# - Files containing usernames (含用户名的文件)
# - Sensitive Directories (敏感目录)
# - Web Server Detection (Web服务器检测)
# - Vulnerable Files (漏洞文件)
# - Vulnerable Servers (漏洞服务器)
# - Error Messages (错误信息)
# - Files containing juicy info (含敏感信息文件)
# - Pages containing login portals (登录门户页面)
# - Various Online Devices (各类在线设备)
# - Advisories and Vulnerabilities (公告和漏洞)
```

### 2.2 Shodan——物联网与服务器搜索引擎

Shodan 扫描整个互联网，索引了全球的开放端口和服务 Banner 信息，是信息收集的核心工具。

#### 基础搜索语法

```bash
# 搜索特定域名/组织
hostname:example.com
org:"Example Corp"
ssl:"example.com"

# 搜索特定服务
product:"Apache httpd"
product:"nginx"
product:"MySQL"
product:"Redis"
product:"Elasticsearch"

# 搜索特定端口
port:22
port:3306
port:6379
port:9200
port:27017

# 搜索特定版本
product:"OpenSSH" version:"7.2"
"Apache/2.4.49"

# 搜索特定国家/城市
country:"CN"
country:"US"
city:"Beijing"

# 搜索操作系统
os:"Windows Server 2012"
os:"Linux"
os:"CentOS"

# 搜索HTTP响应
http.title:"Dashboard"
http.title:"管理后台"
http.status:200
http.component:"PHP"

# 搜索未授权访问
"authentication disabled" port:6379      # Redis未授权
"MongoDB Server Information" port:27017  # MongoDB未授权
"Unauthorized" port:9200                 # ES未授权
port:2181 "Zookeeper"                    # Zookeeper未授权

# 组合搜索
org:"Example Corp" port:443
country:"CN" product:"Elasticsearch"
city:"Shanghai" port:3389
```

#### Shodan CLI 用法

```bash
# 安装
pip install shodan
shodan init YOUR_API_KEY

# 基本搜索
shodan search 'hostname:example.com'
shodan search 'org:"Example Inc"' --fields ip_str,port,org,hostnames

# 统计信息
shodan stats --facets country 'org:"Example Inc"'

# 搜索指定IP
shodan host 1.2.3.4

# 扫描
shodan scan submit 192.168.1.0/24
shodan scan list

# 下载搜索结果
shodan download results.json.gz 'hostname:example.com'
shodan parse --fields ip_str,port,hostnames results.json.gz

# 实时监控（需高级API）
shodan stream --ports 22,80,443,3306,6379 --datadir /tmp/
```

#### Shodan Hacking 技巧

```bash
# 1. 查找暴露的Jenkins
http.title:"Dashboard [Jenkins]" http.component:"Jenkins"

# 2. 查找未设置密码的Redis
product:"Redis" "redis_version" -"requirepass"

# 3. 查找弱口令的MongoDB
product:"MongoDB" "access" -"authentication"

# 4. 查找泄露的Elasticsearch集群
http.title:"cluster_name" port:9200

# 5. 查找工业控制系统
port:502 (Modbus), port:44818 (EtherNet/IP), port:102 (S7)

# 6. 查找开放远程桌面
port:3389 country:"CN"

# 7. 查找Kubernetes Dashboard
http.title:"Kubernetes Dashboard" 200

# 8. 查找GitLab实例
http.title:"GitLab" port:80,443,8080

# 9. 查找Confluence/Wiki
http.component:"Atlassian Confluence"

# 10. 查找存在默认凭证的设备
"default password" port:80,443,8080
```

### 2.3 Fofa / ZoomEye

中国版的网络空间搜索引擎，对中国境内资产覆盖率更好。

#### Fofa 语法

```bash
# 基础语法
domain="example.com"
host="example.com"
ip="1.2.3.4"
port="80"
protocol="http"
title="管理后台"
header="nginx"
body="password"
server="Apache"
country="CN"
city="Beijing"
os="Windows"

# 逻辑运算符
&& (AND), || (OR), != (NOT), () (分组)

# 实战组合
domain="example.com" && port="80,443,8080"
title="后台" && country="CN"
server="Apache/2.4.6" && (port="80" || port="443")
```

#### Fofa API 使用

```bash
# Fofa API查询
curl "https://fofa.info/api/v1/search/all?email=xxx&key=xxx&qbase64=$(echo 'domain=example.com' | base64)&size=1000"

# Python批量查询
import requests, base64
query = base64.b64encode(b'domain="example.com"').decode()
url = f"https://fofa.info/api/v1/search/all?email=EMAIL&key=KEY&qbase64={query}&size=1000"
results = requests.get(url).json()
```

### 2.4 各类搜索引擎用法总结

| 搜索引擎       | 侧重点           | 适用场景                     |
| -------------- | ---------------- | ---------------------------- |
| **Google**     | 网页内容搜索     | 敏感文件/目录/后台/源码泄露  |
| **Shodan**     | 服务 Banner/端口 | 全球端口扫描/物联网/IoT 设备 |
| **Fofa**       | 中国资产覆盖     | 中国境内资产/Web 应用指纹    |
| **ZoomEye**    | Web 应用指纹     | Web 组件指纹/CMS 识别        |
| **Censys**     | SSL 证书/域名    | SSL 证书链分析/域名关联      |
| **BinaryEdge** | 实时扫描数据     | 流式数据/趋势分析            |
| **Hunter.how** | 中文资产         | 中文企业资产测绘             |
| **Onyphe**     | 多协议扫描       | 多维度资产收集               |

---

## 3. 域名与 DNS 信息收集

### 3.1 Whois 查询

```bash
# Linux
whois example.com
whois 1.2.3.4

# 字段关注点
# - 注册者姓名、邮箱、电话（可能关联其他资产）
# - 注册商、注册日期、到期日期
# - DNS服务器（可能泄露内部域名服务器）
# - 组织名称

# 批量查询
for domain in $(cat domains.txt); do
    whois $domain | grep -E "Registrar|Creation Date|Registrant Email" >> whois_results.txt
done
```

#### Whois 反查

通过注册者邮箱反查该邮箱注册的所有域名：

```bash
# 在线工具
# https://reverse-whois.com/
# https://domaintools.com/reverse-whois/

# ViewDNS.info
# https://viewdns.info/reversewhois/

# WhoisXML API
curl "https://reverse-whois.whoisxmlapi.com/api/v2..."
```

### 3.2 DNS 记录查询

```bash
# 常用dig命令
dig example.com ANY          # 查询所有记录
dig example.com A            # IPv4地址
dig example.com AAAA         # IPv6地址
dig example.com MX           # 邮件交换记录
dig example.com NS           # 域名服务器
dig example.com CNAME        # 别名记录
dig example.com TXT          # 文本记录（可能含SPF/DKIM/验证信息）
dig example.com SOA          # 授权起始记录
dig @8.8.8.8 example.com    # 指定DNS服务器查询
dig +short example.com       # 简洁输出
dig -x 1.2.3.4               # 反向查询
dig +trace example.com       # 递归查询路径

# 区域传送漏洞检测
dig AXFR @ns1.example.com example.com
nslookup -type=AXFR example.com ns1.example.com
# 如果成功获取全部DNS记录，是严重信息泄露

# SPF记录分析（可能泄露邮件服务器IP段）
dig TXT example.com | grep spf
# 如 "v=spf1 ip4:203.0.113.0/24 include:_spf.google.com ~all"

# DMARC记录
dig TXT _dmarc.example.com

# DKIM记录
dig TXT default._domainkey.example.com
```

### 3.3 子域名收集

子域名收集是信息收集中最核心的工作之一。每个子域名可能对应不同的服务和应用，即潜在的攻击入口。

#### 被动收集

```bash
# === 证书透明度 (Certificate Transparency) ===
# crt.sh 是最常用的CT日志查询
curl -s "https://crt.sh/?q=%.example.com&output=json" | \
    jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u

# 使用CertStream实时监控
# https://certstream.calidog.io/

# === 搜索引擎 ===
# 在Google Dork中搜索
site:*.example.com -www

# === DNS数据集 ===
# SecurityTrails
curl "https://api.securitytrails.com/v1/domain/example.com/subdomains?apikey=KEY"

# VirusTotal
curl -H "x-apikey: KEY" "https://www.virustotal.com/api/v3/domains/example.com/subdomains"

# AlienVault OTX
curl "https://otx.alienvault.com/api/v1/indicators/domain/example.com/passive_dns"

# === 公共DNS解析记录 ===
# Rapid7 Forward DNS (Project Sonar)
# DNSdumpster
# https://dnsdumpster.com/

# === GitHub ===
# 搜索配置文件中的子域名
# site:github.com example.com
```

#### 主动爆破

```bash
# === Subfinder (推荐首选) ===
subfinder -d example.com -all -o subs.txt
# -all: 使用所有配置的API源
# -passive: 仅被动收集

# === Amass (功能最强) ===
# 被动模式
amass enum -passive -d example.com -o subs.txt
# 主动模式（包含DNS爆破）
amass enum -active -d example.com -o subs.txt -brute -w wordlist.txt
# 仅暴力破解
amass enum -d example.com -brute -w subdomains-top1m.txt

# === PureDNS (最快的DNS爆破) ===
puredns bruteforce subdomains-top1m.txt example.com -r 8.8.8.8,1.1.1.1 -w subs.txt

# === massdns (高性能DNS解析器) ===
massdns -r resolvers.txt -t A -o S subdomains.txt -w massdns_results.txt

# === shuffledns ===
shuffledns -d example.com -w subdomains.txt -r resolvers.txt -o subs.txt

# === 字典选择 ===
# 小字典: https://github.com/rbsec/dnscan
# 大字典: https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt
# 通过排列组合生成:
# 如 {api,dev,test,stg,prod} × {,1,2,3} × {.example.com}
```

#### 工具自动化编排

```bash
#!/bin/bash
# 子域名收集全流程脚本
DOMAIN=$1
OUTDIR="recon_${DOMAIN}"
mkdir -p $OUTDIR

# 1. 被动收集
echo "[*] Passive enumeration..."
subfinder -d $DOMAIN -all -o $OUTDIR/passive.txt
curl -s "https://crt.sh/?q=%25.${DOMAIN}&output=json" | \
    jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u > $OUTDIR/crtsh.txt
amass enum -passive -d $DOMAIN -o $OUTDIR/amass_passive.txt

# 2. 合并去重
cat $OUTDIR/*.txt | sort -u > $OUTDIR/all_subs_unsolved.txt

# 3. DNS解析验证
echo "[*] Resolving..."
puredns resolve $OUTDIR/all_subs_unsolved.txt -r resolvers.txt -w $OUTDIR/resolved.txt

# 4. 主动爆破（基于已知子域名生成排列）
echo "[*] Permutation brute..."
gotator -sub $OUTDIR/resolved.txt -perm permutations.txt -depth 2 \
    -numbers 10 -mindup -md | puredns resolve -r resolvers.txt -w $OUTDIR/bruteforce.txt

# 5. 最终合并
cat $OUTDIR/resolved.txt $OUTDIR/bruteforce.txt | sort -u > $OUTDIR/all_resolved.txt
echo "[+] Total: $(wc -l < $OUTDIR/all_resolved.txt) subdomains"
```

### 3.4 DNS 历史记录

```bash
# SecurityTrails历史DNS
curl "https://api.securitytrails.com/v1/history/example.com/dns/a?apikey=KEY"

# CompleteDNS
# https://completedns.com/

# DNSDB
# https://www.dnsdb.info/

# 查看历史IP变化（可能发现真实IP隐藏历史）
# 尤其适用于使用了CDN的目标
```

---

## 4. IP 与网络层信息收集

### 4.1 绕过 CDN 获取真实 IP

很多网站在前面套了 Cloudflare/CDN，直接得到的 IP 是 CDN 节点而非源站。绕过 CDN 获取真实 IP 是信息收集的关键环节。

#### 方法汇总

```bash
# === 1. DNS历史记录 ===
# 使用SecurityTrails/DNSDB查询A记录历史
# 网站刚建立时可能没有CDN，历史记录暴露真实IP

# === 2. 子域名碰撞 ===
# 很多站点主域名使用CDN，但子域名不经过CDN
# 如: mail.example.com, ftp.example.com, direct.example.com
# 爆破多级子域名，找到没套CDN的子域名
# IP可能在同一C段或就是源站IP

# === 3. 邮件服务器 ===
# 查找网站发送的邮件头（注册邮件、密码找回邮件）
# 邮件头的Received:字段可能包含真实IP
# 主动：注册账号→触发密码找回→分析邮件头

# === 4. SSL证书 ===
# 使用Censys/Shodan搜索SSL证书
# 证书可能关联源站IP
# censys search 'services.tls.certificates.leaf_data.subject.common_name: "example.com"'

# === 5. 网站RSS/API端点 ===
# 一些功能可能绕过CDN直连源站
# ping example.com      → CDN IP
# ping api.example.com  → 可能直连
# ping rss.example.com  → 可能直连

# === 6. 全球多地Ping ===
# 使用全球多节点对比响应IP
# https://ping.pe/
# https://check-host.net/
# https://www.itdog.cn/ping/

# === 7. PHP/CGI信息泄露 ===
# 访问 phpinfo() 页面
# 查看_SERVER['SERVER_ADDR'] 等字段

# === 8. 网站漏洞直接回显 ===
# SSRF漏洞返回的IP
# 文件上传返回的绝对路径IP
# 数据库连接外带IP

# === 9. CloudFlare特殊子域名 ===
# direct.example.com (有时候直接解析到源站)
# 或使用 CloudFlare 的 `direct` 子域名获取源站
# cloudflare-dns.com 解析

# === 10. favicon.ico hash ===
# Shodan搜索相同的favicon hash
curl -s https://example.com/favicon.ico | python3 -c "
import mmh3, sys, codecs
print(mmh3.hash(codecs.encode(sys.stdin.buffer.read(),'base64')))
"
# 然后在Shodan搜索: http.favicon.hash:HASH_VALUE
```

### 4.2 端口扫描

#### Nmap 核心用法

```bash
# === 基础扫描 ===
nmap -sn 192.168.1.0/24              # Ping扫描（存活探测）
nmap -sS -p 1-65535 target.com       # SYN半连接扫描（需root）
nmap -sT -p 80,443,8080 target.com   # TCP全连接扫描
nmap -sU -p 53,161 target.com        # UDP扫描（较慢）
nmap -sV -p 22,80,443 target.com     # 版本探测

# === 加速扫描 ===
nmap -sS -p 1-65535 --min-rate 10000 target.com       # 高速扫描
nmap -sS -p- --min-rate 5000 --max-retries 1 target.com # 快速全端口
nmap -sS -p- -T4 --min-hostgroup 64 --max-rtt-timeout 100ms

# Masscan (更快的端口扫描)
masscan -p1-65535 --rate 10000 target.com

# === 服务与操作系统识别 ===
nmap -sV --version-intensity 9 target.com    # 深度版本探测
nmap -O --osscan-guess target.com             # 操作系统猜测
nmap -A -p 80,443 target.com                  # 全面扫描

# === NSE脚本(Nmap Scripting Engine) ===
ls /usr/share/nmap/scripts/ | head -30

# 漏洞扫描
nmap --script=vuln -p 80,443 target.com
nmap --script=http-vuln* -p 80,443 target.com

# 默认凭证检测
nmap --script=http-default-accounts -p 80,443 target.com

# HTTP信息收集
nmap --script=http-enum -p 80,443 target.com
nmap --script=http-methods -p 80,443 target.com
nmap --script=http-title -p 80,443,8080 target.com

# SSL检测
nmap --script=ssl-enum-ciphers -p 443 target.com
nmap --script=ssl-cert -p 443 target.com
nmap --script=ssl-heartbleed -p 443 target.com

# 数据库检测
nmap --script=mysql-info -p 3306 target.com
nmap --script=redis-info -p 6379 target.com
nmap --script=mongodb-info -p 27017 target.com

# 常用NSE分类
# auth     - 认证绕过
# broadcast - 局域网广播
# brute    - 暴力破解
# default  - 默认安全扫描
# discovery - 信息发现
# dos      - 拒绝服务测试
# exploit  - 漏洞利用
# fuzzer   - 模糊测试
# malware  - 恶意软件检测
# vuln     - 漏洞检测
```

#### 端口范围扫描策略

```bash
# 策略一：先Top端口，再全端口（适合时间有限）
nmap -sS --top-ports 1000 target.com             # 先扫Top 1000
nmap -sS -p- --min-rate 5000 target.com &         # 后台慢扫全端口

# 策略二：分段扫描（适合全端口扫描）
nmap -sS -p1-10000 target.com
nmap -sS -p10001-20000 target.com
# ... 分多段并行

# 策略三：Masscan快速全端口→Nmap精细扫描
masscan -p1-65535 --rate 5000 target.com -oG masscan.gnmap
# 提取开放端口后，用Nmap逐一版本探测
nmap -sV -p $(cat ports.txt | tr '\n' ',') target.com
```

#### 常见端口与服务速查

```bash
# Web服务
21    FTP           # vsftpd/ProFTPD (匿名登录检测)
22    SSH           # OpenSSH (版本漏洞检测)
23    Telnet        # (弱口令检测)
25    SMTP          # 邮件服务 (用户枚举)
53    DNS           # BIND (区域传送检测)
80    HTTP          # Apache/Nginx/IIS
110   POP3          # 邮件
111   RPCBind       # (NFS相关漏洞)
135   MSRPC         # Windows RPC
139   NetBIOS       # Windows文件共享
143   IMAP          # 邮件
161   SNMP          # (默认community: public/private)
389   LDAP          # (匿名绑定检测)
443   HTTPS         # SSL/TLS
445   SMB           # Windows文件共享 (永恒之蓝)
873   Rsync         # (未授权访问)
1433  MSSQL         # SQL Server
1521  Oracle        # Oracle DB
2049  NFS           # 网络文件系统
2181  Zookeeper     # (未授权访问)
2375  Docker        # Docker API (未授权访问)
3128  Squid         # 代理
3306  MySQL         # MySQL
3389  RDP           # Windows远程桌面
4440  Rundeck       # (未授权访问)
4848  GlassFish     # GlassFish
5432  PostgreSQL    # PostgreSQL
5555  Android ADB   # (未授权访问)
5900  VNC           # 远程桌面
5985  WinRM         # Windows远程管理
6379  Redis         # (未授权访问)
7001  WebLogic      # Oracle WebLogic
8009  AJP           # Tomcat AJP (幽灵猫漏洞)
8080  HTTP-Alt      # Tomcat/Jetty/JBoss
8443  HTTPS-Alt     # SSL
8888  Jupyter       # Jupyter Notebook
9000  PHP-FPM       # PHP-FPM
9092  Kafka         # Kafka
9200  Elasticsearch # (未授权访问)
11211 Memcached     # (UDP放大攻击/未授权)
27017 MongoDB       # (未授权访问)
50000 SAP           # SAP
```

### 4.3 IP 段扩展与 BGP 信息

```bash
# ASN查询
whois -h whois.cymru.com " -v 1.2.3.4"
# 返回: AS号 | IP | BGP Prefix | Country | Registry | Allocated Date

# BGP Toolkit
# https://bgp.he.net/

# IP反查同C段站点
# https://dnslytics.com/reverse-ip
# https://viewdns.info/reverseip/

# 获取整个ASN的IP段
curl -s "https://api.bgpview.io/asn/AS12345/prefixes" | jq '.data.ipv4_prefixes'

# 基于ASN批量扫描
# 找到目标ASN后，扫描其所有IP段的常见端口
```

---

## 5. Web 应用指纹识别

### 5.1 技术栈识别

```bash
# === WhatWeb ===
whatweb example.com
whatweb -a 3 example.com       # 侵略性3
whatweb --no-errors example.com # 安静模式

# === Wappalyzer ===
# 浏览器插件（手动浏览时使用）
# 或者CLI版本
wappalyzer https://example.com

# === BuiltWith ===
# https://builtwith.com/
# 查看网站使用的技术栈历史变化

# === WebAnalyze (Go) ===
webanalyze -host example.com -crawl 1

# === 手工识别 ===
# HTTP响应头
curl -I https://example.com
# Server: Apache/2.4.6 (CentOS)
# X-Powered-By: PHP/7.2.24
# Set-Cookie: PHPSESSID=xxx → PHP
# Set-Cookie: JSESSIONID=xxx → Java
# Set-Cookie: ASP.NET_SessionId=xxx → ASP.NET
# X-Generator: Drupal 7
```

### 5.2 CMS 识别

```bash
# === CMSeeK ===
cmsseek -u https://example.com --random-agent

# === WhatWeb CMS专用 ===
whatweb -p /usr/share/whatweb/plugins-disabled/ example.com

# === 手工CMS指纹 ===
# WordPress
curl -s https://example.com/wp-login.php
curl -s https://example.com/wp-content/
curl -s https://example.com/readme.html
curl -s https://example.com/wp-json/wp/v2/users   # API用户枚举

# Joomla
curl -s https://example.com/administrator/
curl -s https://example.com/language/en-GB/en-GB.xml

# Drupal
curl -s https://example.com/user/login
curl -s https://example.com/CHANGELOG.txt
curl -s https://example.com/robots.txt  # Drupal robots有特征

# 常见CMS路径特征
/admin                  → 各类CMS
/wp-admin               → WordPress
/user/login             → Drupal
/administrator          → Joomla
/admin/login.aspx       → Sitecore/ASP.NET CMS
/login.action           → Confluence/JIRA
/manager/html           → Tomcat
/console                → 各类控制台
/.env                   → Laravel (严重泄露)
/config/database.yml    → Rails
/WEB-INF/web.xml        → Java Web应用
/phpinfo.php            → PHP信息泄露
/test.php               → 测试文件
/info.php               → 同phpinfo
```

### 5.3 前端框架识别

```bash
# 查看页面源码中的特征
# React
view-source:https://example.com | grep "react"
# __REACT_DEVTOOLS_GLOBAL_HOOK__

# Vue.js
view-source:https://example.com | grep "vue"
# __vue_app__

# Angular
view-source:https://example.com | grep "ng-version"
# ng-version="15.0.0"

# jQuery
view-source:https://example.com | grep "jquery"

# Bootstrap
view-source:https://example.com | grep "bootstrap"
```

### 5.4 WAF 识别

```bash
# === wafw00f ===
wafw00f https://example.com
# 识别70+种WAF产品

# === Nmap WAF脚本 ===
nmap --script=http-waf-detect -p 80,443 example.com
nmap --script=http-waf-fingerprint -p 80,443 example.com

# === 手工检测 ===
# 发送恶意payload看响应
curl -s "https://example.com/?id=1' OR '1'='1"
# 如果返回WAF拦截页面（如403/406）、包含WAF特征串

# 常见WAF响应特征
# CloudFlare: cf-ray header, __cfduid cookie, 522/524状态码
# 阿里云WAF: X-Security header, YUNDUN cookie
# 腾讯云WAF: Tencent-LeakScan header
# ModSecurity: 响应中含ModSecurity字样
# 安全狗: Safedog字样
# D盾: D盾拦截页面特征
# 宝塔WAF: BTWAF字样

# WAF绕过探测
# 1. 测试大小写变换
curl -s "https://example.com/?id=1 AnD 1=1"

# 2. 测试参数污染
curl -s "https://example.com/?id=1&id=2"

# 3. 测试HTTP协议兼容性问题
# 使用HTTP/1.0
printf "GET /?id=1' HTTP/1.0\r\nHost: example.com\r\n\r\n" | nc example.com 80

# 4. 测试编码绕过
curl -s "https://example.com/?id=1%20%55%4e%49%4f%4e%20%53%45%4c%45%43%54"
```

---

## 6. 目录与文件扫描

### 6.1 目录爆破

```bash
# === dirsearch ===
dirsearch -u https://example.com -e php,asp,aspx,jsp,txt,bak,old,zip,tar.gz
dirsearch -u https://example.com -w /path/to/dict.txt -t 50 --random-agent

# === ffuf (Go,速度最快) ===
ffuf -u https://example.com/FUZZ -w wordlist.txt -mc 200,301,302,403
ffuf -u https://example.com/FUZZ -w wordlist.txt -fc 404       # 排除404
ffuf -u https://example.com/FUZZ -w wordlist.txt -fs 0          # 排除空响应
ffuf -u https://example.com/FUZZ -w wordlist.txt -t 100 -o results.json

# === gobuster ===
gobuster dir -u https://example.com -w wordlist.txt -x php,asp,jsp -t 50

# === feroxbuster (Rust,递归) ===
feroxbuster -u https://example.com -w wordlist.txt -x php,html -d 3 --random-agent

# === 字典推荐 ===
# https://github.com/danielmiessler/SecLists (Discovery/Web-Content)
# https://github.com/dirbuster/dirbuster (directory-list-2.3-medium.txt)
# https://github.com/daviddias/node-dirbuster (raft系列)
# https://github.com/six2dez/OneListForAll (多源合并)
```

### 6.2 敏感文件探测

```bash
# === 备份文件 ===
# 常见模式
index.php.bak
index.php~
index.php.old
index.php.save
index.php.swp
index.php.orig
index.php.zip
web.tar.gz
backup.zip
dump.sql
database.sql.bak

# === 配置文件 ===
/.env                    # Laravel/.env相关框架
/config.php.bak
/wp-config.php.bak
/web.config
/web.xml
/application.properties  # Spring Boot
/settings.py             # Django
/config/database.yml     # Rails
/package.json            # Node.js (依赖版本)

# === 版本控制泄露 ===
/.git/HEAD               # Git泄露
/.svn/entries            # SVN泄露
/.hg/requires            # Mercurial泄露
/.DS_Store               # macOS文件泄露

# === Git泄露利用 ===
# 使用GitHacker
git clone https://github.com/lijiejie/GitHack
python GitHack.py https://example.com/.git/

# 使用dvcs-ripper
rip-git.pl -v -u https://example.com/.git/

# 使用git-dumper
./git-dumper.sh https://example.com/.git/ /tmp/out/

# 恢复的.git目录可以完整查看源码历史
git log --oneline
git diff HEAD~1
```

### 6.3 递归目录扫描策略

```bash
# 第一轮：快速扫描常见路径
ffuf -u https://example.com/FUZZ -w commonspeak2-raft-small.txt -t 100 -of csv -o round1.csv

# 第二轮：基于第一轮发现的目录递归
ffuf -u https://example.com/FUZZ -w medium.txt -recursion -recursion-depth 2 -t 50

# 第三轮：对发现的目录做针对性扫描
# 如发现 /api/ 目录
ffuf -u https://example.com/api/FUZZ -w api-wordlist.txt -t 100

# 备份文件专项
for ext in bak old save swp orig zip tar.gz sql; do
    curl -s -o /dev/null -w "%{http_code} %{url}\n" \
        "https://example.com/index.php.${ext}"
done
```

---

## 7. 代码与信息泄露搜集

### 7.1 GitHub 信息泄露

```bash
# === GitHub Dork ===
# 搜索泄露的密钥/配置
site:github.com "example.com" password
site:github.com "example.com" "API_KEY"
site:github.com "example.com" "SECRET"
site:github.com "example.com" "BEGIN RSA PRIVATE KEY"
site:github.com "example.com" "access_key"
site:github.com "example.com" ".env" "DB_PASSWORD"
site:github.com "example.com" filename:.npmrc _auth

# 搜索内部文档
site:github.com "Example Corp" "password" OR "credentials"
site:github.com "example.com" "internal" OR "confidential"
site:github.com "example.com" "测试" OR "内网"

# 搜索上传的数据库
site:github.com "example.com" filename:dump.sql
site:github.com "example.com" filename:database.sql

# === GitRob ===
gitrob -repo example_org

# === truffleHog (检测高熵字符串/密钥) ===
trufflehog git https://github.com/example/repo --json

# === Gitleaks ===
gitleaks detect --source /path/to/repo --report-format json

# === GitGraber ===
gitGraber -k keywords.txt -q "example.com" -t github_token

# === 自动GitHub监控 ===
# 设置cron任务定期搜索
# 防止自身泄露后第一时间发现
```

### 7.2 配置与日志泄露

```bash
# === Web目录常见泄露 ===
# .env文件
curl https://example.com/.env
# 返回:
# APP_KEY=base64:xxx
# DB_CONNECTION=mysql
# DB_HOST=127.0.0.1
# DB_DATABASE=blog
# DB_USERNAME=root
# DB_PASSWORD=admin123
# AWS_ACCESS_KEY_ID=AKIA...
# AWS_SECRET_ACCESS_KEY=...

# 日志文件
curl https://example.com/storage/logs/laravel.log
curl https://example.com/logs/error.log
curl https://example.com/debug.log

# 调试页面
curl https://example.com/phpinfo.php
curl https://example.com/actuator   # Spring Boot Actuator
curl https://example.com/actuator/env  # 环境变量包括所有配置
curl https://example.com/actuator/mappings # 全部路由

# Django Debug模式
# Debug=True时访问不存在页面会泄露源码和配置
curl https://example.com/asdfghjk
# 查看异常页面中的settings信息

# 错误页面信息泄露
curl -H "Accept: application/json" https://example.com/api/xxx  # 触发JSON错误
# 可能返回: 数据库错误信息、路径、版本号
```

### 7.3 文档元数据

```bash
# === 下载公开的PDF/Word/Excel ===
# 网站公开下载的文件可能包含元数据
site:example.com filetype:pdf
site:example.com filetype:docx
site:example.com filetype:xlsx

# 下载后使用exiftool分析
exiftool document.pdf
# 可能泄露: 作者、软件版本、创建时间、修改历史

# FOCA (Fingerprinting Organizations with Collected Archives)
# 自动下载并分析元数据的工具
# https://github.com/ElevenPaths/FOCA
```

---

## 8. 社会工程信息收集

### 8.1 公司组织信息

```bash
# === LinkedIn ===
# 搜索公司员工列表
# "Example Corp" engineer
# 了解技术栈（从员工技能标签）
# 了解组织架构（部门、职位）

# === 招聘网站 ===
# 招聘JD中常包含技术栈信息
# "熟悉 React/Node.js/MongoDB"
# "负责维护Kubernetes集群"
# "有Hadoop/Flink大数据经验"

# 自动化收集
# theHarvester
theHarvester -d example.com -b linkedin,google -l 500 -f results.html

# === 公司官网 ===
# 关于我们 → 团队介绍
# 联系我们 → 电话、邮箱格式
# 新闻发布 → 合作伙伴、客户
# 投资者关系 → 财务报告、子公司

# === 企业信息平台 ===
# 天眼查 https://www.tianyancha.com/
# 企查查 https://www.qichacha.com/
# 查询：股东信息、子公司、法人、域名、软件著作权列表
# 软件著作权 → 内部系统名称
```

### 8.2 邮箱收集

```bash
# === theHarvester ===
theHarvester -d example.com -b google,bing,yahoo,baidu -l 500

# === Hunter.io ===
curl "https://api.hunter.io/v2/domain-search?domain=example.com&api_key=KEY"

# === EmailFinder ===
emailfinder -d example.com

# === 邮箱格式推测 ===
# 已知员工: 张三 → zhangsan@example.com
# 常见格式:
# firstname.lastname@
# firstname@
# firstname_lastname@
# f.lastname@
# firstnamelastname@
# lastname.firstname@

# === 邮箱验证 ===
# 通过SMTP VRFY命令（通常被禁用）
# 通过在登录页面测试邮箱是否存在
# 找回密码页面的响应差异（存在→已发送邮件，不存在→用户不存在）
```

### 8.3 社交账号与关联分析

```bash
# === Sherlock (跨平台用户名搜索) ===
sherlock username

# === maigret (更全的社交平台) ===
maigret username

# === Holehe (通过邮箱找注册的平台) ===
holehe email@example.com

# === 社工库查询 ===
# (仅用于合法授权的安全测试)
# 泄露密码查询 → 密码复用分析
```

---

## 9. API 与接口信息收集

### 9.1 API 端点发现

```bash
# === JavaScript源码分析 ===
# 使用浏览器DevTools → Sources → 搜索
# 关键词: api, endpoint, fetch, axios, url, baseURL

# 自动化JS提取
# LinkFinder
python linkfinder.py -i https://example.com/main.js -o cli

# getJS
getJS --url https://example.com --output js_files.txt

# JSSCanner (Burp插件)
# Burp → Spider → 提取所有JS → 分析URL和端点

# 在线工具
# https://urlscan.io/  → 搜索域名 → 查看页面请求
```

### 9.2 API 文档

```bash
# === Swagger/OpenAPI ===
curl https://example.com/swagger-ui.html
curl https://example.com/swagger.json
curl https://example.com/api-docs
curl https://example.com/v2/api-docs
curl https://example.com/v3/api-docs
curl https://example.com/openapi.json

# 发现后可直接浏览所有API接口和参数

# === GraphQL ===
curl https://example.com/graphql
# 使用Introspection查询获取全部schema
curl -X POST https://example.com/graphql \
    -H "Content-Type: application/json" \
    -d '{"query":"{ __schema { types { name fields { name } } } }"}'

# === SOAP/WSDL ===
curl https://example.com/service?wsdl
curl https://example.com/webservice?wsdl
```

### 9.3 手机 APP API 发现

```bash
# === 反编译APK/IPA ===
# 解包APK
apktool d app.apk -o app_source/

# 搜索硬编码的API地址
grep -rE "https?://[a-zA-Z0-9./?=_-]*" app_source/ | grep -v "android.com"
grep -rE "api|endpoint|baseUrl|BASE_URL" app_source/

# 搜索硬编码密钥
grep -rE "key|secret|token|password" app_source/ --include="*.java" --include="*.smali"

# 使用MobSF自动化分析
# https://github.com/MobSF/Mobile-Security-Framework-MobSF
docker run -p 8000:8000 opensecurity/mobile-security-framework-mobsf
```

---

## 10. 内网信息收集（进入内网后）

### 10.1 内网资产发现

```bash
# === ARP扫描 ===
arp -a
nmap -sn 192.168.1.0/24

# === 主机存活探测 ===
# ICMP
for i in {1..254}; do ping -c 1 -W 1 192.168.1.$i | grep "64 bytes"; done

# 批量Ping (fping)
fping -a -g 192.168.1.0/24 2>/dev/null

# === Windows环境 ===
net view                    # 查看域内计算机
net view /domain            # 查看所有域
net group /domain           # 查看域内所有组
net group "domain admins" /domain  # 域管理员
net group "domain computers" /domain
net user /domain            # 域用户
net time /domain            # 域控IP

# === Linux环境 ===
# 查看当前网络配置
ifconfig -a || ip addr show
route -n                    # 路由表
cat /etc/hosts              # hosts文件
cat /etc/resolv.conf        # DNS配置
arp -a                      # ARP缓存

# === 网段发现（多网卡） ===
# 查看本机所有IP，发现可能存在的其他网段
# 从配置文件中发现
find /etc /var /opt -name "*.conf" -o -name "*.cfg" -o -name "*.ini" 2>/dev/null | \
    xargs grep -lE "192\.168\.|10\.|172\.[12][6-9]|172\.[3][0-1]" 2>/dev/null
```

### 10.2 凭据收集

```bash
# === 配置文件中的密码 ===
find / -name "*.config" -o -name "*.conf" -o -name "*.ini" \
    -o -name "*.yaml" -o -name "*.yml" -o -name ".env" 2>/dev/null | \
    xargs grep -E "password|passwd|pass|secret|key|token|connectionString" 2>/dev/null

# === Bash历史 ===
cat ~/.bash_history | grep -E "mysql|ssh|pass|sudo|token"
cat ~/.zsh_history | grep -E "mysql|ssh|pass|sudo|token"

# === Windows ===
# 注册表中的密码
reg query HKLM /f password /t REG_SZ /s
reg query HKCU /f password /t REG_SZ /s

# 浏览器保存的密码
# Chrome: %APPDATA%\..\Local\Google\Chrome\User Data\Default\Login Data
# Firefox: logins.json + key4.db

# === 数据库连接信息 ===
# Java: context.xml, jdbc.properties, application.properties
# PHP: config.php, database.php, .env
# Python: settings.py, local_settings.py
# .NET: web.config, appsettings.json
```

---

## 11. 信息收集自动化平台

### 11.1 组合工具平台

```bash
# === ProjectDiscovery全家桶 ===
# Subfinder    → 子域名发现
# Httpx        → HTTP探测和指纹
# Nuclei       → 漏洞扫描
# Naabu        → 端口扫描
# Katana       → Web爬虫
# Uncover      → 搜索引擎聚合
# Chaos        → 子域名数据集

# 流水线示例
subfinder -d example.com -all -silent | \
    httpx -title -status-code -tech-detect -o http_results.json && \
    nuclei -l http_results.json -tags cve,exposure,misconfig

# === Amass ===
amass enum -d example.com -o amass_results.txt
amass intel -d example.com  # 关联域名发现

# === SpiderFoot (全自动OSINT) ===
# Web界面/Cli
python3 sf.py -s example.com -t all -o csv

# === Recon-ng (模块化侦察) ===
recon-ng
[recon-ng] marketplace install all
[recon-ng] create workspace example
[recon-ng] add domains example.com
[recon-ng] modules load recon/domains-hosts/bing_domain_web
[recon-ng] modules load recon/hosts-hosts/resolve
[recon-ng] run
```

### 11.2 云环境信息收集

```bash
# === AWS ===
# S3 Bucket发现
# naming pattern: example-com, example-backup, example-prod
aws s3 ls s3://example-com --no-sign-request
aws s3 ls s3://example-prod --no-sign-request

# 使用工具枚举
# s3scanner
python s3scanner.py scan --buckets-file buckets.txt

# CloudFront → 找源站
# Lambda → 找环境变量泄露
# IAM → 找过度权限

# === 阿里云/腾讯云 ===
# OSS Bucket发现
curl https://example-com.oss-cn-beijing.aliyuncs.com
# COS Bucket
curl https://example-com.cos.ap-guangzhou.myqcloud.com

# === Kubernetes ===
# API Server (端口6443/8443)
# etcd (端口2379)
# Dashboard (端口30000-32767)
# Kubelet (端口10250)
```

---

## 12. 防御方案——如何减少信息暴露

### 12.1 技术层面

```bash
# === 1. 服务器信息隐藏 ===
# Nginx隐藏版本号
# nginx.conf
server_tokens off;
more_clear_headers "Server";
more_clear_headers "X-Powered-By";

# Apache
# httpd.conf
ServerTokens Prod
ServerSignature Off

# PHP隐藏
# php.ini
expose_php = Off

# === 2. WAF配置 ===
# 拦截扫描器特征User-Agent
# 限制单IP请求频率
# 拦截明显的恶意payload

# === 3. 目录和文件保护 ===
# Nginx禁止访问敏感文件
location ~ /\.(?!well-known) {
    deny all;
}
location ~ \.(env|sql|log|bak|backup|old|save|swp|orig|git|svn|DS_Store)$ {
    deny all;
    return 403;
}

# === 4. DNS配置 ===
# 禁止区域传送
# 使用CAA记录限制证书颁发
# SPF记录中尽量减少IP信息泄露

# === 5. 错误页面 ===
# 自定义错误页面，不暴露技术信息
# 关闭debug模式
# 统一错误返回（不区分用户不存在/密码错误）

# === 6. 合理使用CDN ===
# 源站IP只允许CDN节点回源
# 使用iptables/安全组限制源站访问来源
# 为所有子域名启用CDN（不遗漏）
```

### 12.2 管理层面

```bash
# === 1. 代码仓库审计 ===
# 定期扫描内部代码仓库中的硬编码凭据
# 使用Gitleaks/truffleHog在CI/CD中自动扫描
# 强制使用环境变量或密钥管理服务

# === 2. 外部暴露面巡检 ===
# 定期在Fofa/Shodan搜索自身资产
# 监控新出现的子域名/端口/服务
# 使用Attack Surface Management (ASM)平台

# === 3. 安全意识培训 ===
# 员工不在社交平台泄露内部技术细节
# GitHub仓库权限审核（不公开Internal项目）
# 文档发布前清除元数据

# === 4. 暴露面收敛 ===
# 下线不用的服务
# 关闭非必要端口
# 定期清理过期DNS记录
# 及时删除测试/开发环境的外网入口

# === 5. 蜜罐部署 ===
# 部署伪装的敏感文件 (如.github/config.php~)
# 部署伪装的开放端口
# 访问即告警，提供早期预警
```

### 12.3 检测信息收集行为

```bash
# === 异常行为检测 ===
# 1. 同一IP短时间内请求大量不存在路径 → 目录扫描
# 2. 同一IP请求大量不同子域名 → 子域名爆破
# 3. User-Agent包含扫描器特征 → 工具识别
# 4. 请求URL包含常见敏感文件后缀 (.bak/.env/.git) → 敏感文件探测
# 5. DNS服务器收到大量不存在的子域名查询 → DNS爆破
# 6. 同一IP请求频率异常高 → 自动化扫描

# === 基础WAF规则 ===
# 拦截Git/Env/SVN探测
# 拦截目录扫描工具UA
# 拦截高频404请求的IP
# 对扫描行为加入延时/返回假数据/返回蜜罐
```

---

## 13. 信息收集工具速查表

| 类别         | 工具                                        | 用途           |
| ------------ | ------------------------------------------- | -------------- |
| **搜索引擎** | Google Dork, Shodan, Fofa, ZoomEye, Censys  | 被动信息收集   |
| **子域名**   | Subfinder, Amass, PureDNS, massdns          | 子域名枚举     |
| **端口扫描** | Nmap, Masscan, Naabu                        | 端口发现       |
| **Web 扫描** | Httpx, WhatWeb, Wappalyzer                  | HTTP 探测/指纹 |
| **目录扫描** | dirsearch, ffuf, gobuster, feroxbuster      | 目录/文件发现  |
| **漏洞扫描** | Nuclei, OpenVAS, AWVS                       | 漏洞检测       |
| **Git 泄露** | GitHack, dvcs-ripper, git-dumper, Gitleaks  | 源码恢复       |
| **DNS 分析** | dig, nslookup, dnsenum, dnsrecon            | DNS 信息收集   |
| **OSINT**    | theHarvester, SpiderFoot, Recon-ng, maigret | 自动化信息收集 |
| **WAF 识别** | wafw00f, Nmap http-waf-fingerprint          | WAF 检测       |
| **API 发现** | LinkFinder, getJS, Burp JS Link Finder      | API 端点提取   |
| **证书分析** | crt.sh, CertStream, SSLScan                 | SSL/CT 分析    |

---

> **核心法则**：信息收集没有"收集够了"这个概念。每一个新发现都可能是突破口，每一条被忽略的信息都可能是防守方的最后一道防线。

> **防守法则**：减少暴露面的最好方式，就是假设攻击者知道你能想到的一切信息收集手段，然后逐项检查你的防线。
