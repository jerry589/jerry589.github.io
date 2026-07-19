---
title: 渗透测试面试系列二：Web基础漏洞——SSRF、XSS、SQL注入、CSRF、XXE
tags: [面试, 渗透测试, SSRF, XSS, SQL注入, CSRF, XXE, Web安全]
date: 2026-07-18
---

# 渗透测试面试系列二：Web基础漏洞——SSRF、XSS、SQL注入、CSRF、XXE

<!-- more -->

## SSRF

### SSRF 原理

服务器端请求伪造（Server-Side Request Forgery），服务端提供了从其他服务器应用获取数据的功能，且没有对目标地址做过滤与限制，服务器就以服务器自己的身份去访问其他服务器的资源。

### SSRF 利用

| 协议 | 用途 |
|------|------|
| **dict** | 泄露安装软件版本信息，查看端口，操作内网 Redis 服务等 |
| **file** | 在有回显的情况下，利用 file 协议可以读取任意内容 |
| **gopher** | 支持发出 GET、POST 请求，可以先截获请求包，再构造成符合 gopher 协议的请求。gopher 协议是 SSRF 利用中最强大的协议（俗称万能协议），可用于反弹 shell |
| **http/s** | 探测内网主机存活 |

### SSRF 防御

1. 设置 URL 白名单或者限制内网 IP
2. 统一错误信息，避免用户可以根据错误信息来判断远程服务器端口状态
3. 限制请求的端口为 HTTP 常用的端口，比如 80、443、8080、8088 等
4. 禁用不需要的协议，仅仅允许 HTTP 和 HTTPS

### SSRF 挖掘点

1. 分享：通过 URL 地址分享网页内容
2. 转码服务
3. 在线翻译
4. 图片加载与下载：通过 URL 地址加载或下载图片
5. 图片、文章收藏功能
6. 未公开的 API 实现以及其他调用 URL 的功能
7. 从 URL 关键字中寻找：Share、wap、url、link、src、source、target、u、3g、display、sourceURL、imageURL、domain

### SSRF 禁用 127.0.0.1 后如何绕过？

添加 @ 绕过：`www.baidu.com@127.0.0.1`

将 127.0.0.1 转换为其他进制绕过：

```
0177.0.0.1    // 八进制
0x7f.0.0.1    // 十六进制
2130706433    // 十进制
```

### SSRF 相关危险函数

`file_get_contents`、`fsockopen`、`curl_exec`、`fopen`、`readfile` 等函数使用不当会造成 SSRF 漏洞。

### SSRF 和 CSRF 的区别

| | SSRF | CSRF |
|------|------|------|
| 发起方 | 服务器端 | 客户端（浏览器） |
| 攻击目标 | 内网服务 | Web应用功能 |
| 本质 | 服务端请求伪造 | 客户端跨站请求伪造 |

---

## XSS

### XSS 原理

Web 页面用户输入可控，插入恶意 JS 代码或被存储进数据库中，浏览器解析执行获取用户 Cookie。

### XSS 分类

反射型 / DOM 型 / 存储型。

### XSS 防御

1. 正则过滤（标签/JS代码/事件）
2. 用户的输入进行 HTML 编码输出（无法进行闭合）
3. 服务端设置会话 Cookie 的 HTTP Only 属性（不能获取 Cookie）
4. 限制长度

### XSS 绕过

1. 大小写/双写/镶嵌
2. URL 编码/HTML 实体编码/编码单个字符
3. 禁用哪些标签，更换标签
4. `<input>` `<script>` 绕过实体编码
5. 禁用哪些 JS 代码，更换代码
6. 禁用什么事件，更换事件

### XSS 挖掘点

- **重灾区**：评论区、留言区、个人信息、订单信息等
- **针对型**：站内信、网页即时通讯、私信、意见反馈
- **存在风险**：搜索框、当前目录、图片属性等

### XSS 除了获取 Cookie 还能做什么？

页面跳转、获取管理员 IP、XSS 蠕虫、钓鱼攻击、前端 JS 挖矿、键盘记录、屏幕截图、获取后台 URL。

---

## SQL注入

### SQL注入原理

对用户输入的数据没有进行严格的过滤与判断，导致用户构造各种恶意 payload 拼接进后台数据库查询语句中执行。

### SQL注入分类

- **常见**：联合查询、布尔盲注、延时盲注、报错注入
- **其他**：宽字节注入、堆叠注入等

### SQL注入防御

**代码层面**：

1. 正则过滤
2. PHP 转义函数
3. 预编译（PDO）
4. 权限分明/权限限制

**网络层面**：WAF设备。

### SQL报错注入函数有哪些？

- `floor()` 报错注入
- `name_const()` 报错注入
- `exp()` 报错注入
- `convert()` 报错注入
- `extractvalue()` 报错注入（返回数据长度限制，最长32位）
- `updatexml()` 报错注入（返回数据长度限制，最长32位）

### SQL注入常用函数

- 逻辑运算符：`AND`、`OR`、`||`
- 联合查询：`UNION SELECT`
- 查询字段：`ORDER BY`
- 报错注入：`floor()`、`name_const()`、`exp()`、`convert()`、`extractvalue()`、`updatexml()`

### 宽字节注入原理/条件

目标站点对于特殊字符的转义（单双引号）前面会添加斜杠 `\`，斜杠的 URL 编码是 `%5c`。如果目标站点使用的是 GBK 编码，则可以构造 payload `%df` 加单引号，`%df` 与 `%5c` 结合成为一个汉字，而单引号则逃逸了出去。

### SQL注入如何判断数据库类型？

1. **端口**：MySQL 3306、MSSQL 1433、Oracle 1521
2. **页面报错信息**
3. **各数据库特有的数据表**：

```sql
-- MSSQL
AND (SELECT count(*) FROM sysobjects)>0 AND 1=1

-- Access
AND (SELECT count(*) FROM msysobjects)>0 AND 1=1

-- MySQL（5.0以上）
AND (SELECT count(*) FROM information_schema.TABLES)>0 AND 1=1

-- Oracle
AND (SELECT count(*) FROM sys.user_tables)>0 AND 1=1
```

4. **各数据库特有的连接符**：

```sql
-- MSSQL
AND '1' + '1' = '11'

-- MySQL
AND CONCAT('1','1')='11'

-- Oracle
AND CONCAT('1','1')='11'
```

5. **MSSQL 特征**：
   - 延时注入：`WAITFOR DELAY '00:00:10'`
   - 默认变量：`SELECT @@SERVERNAME`
   - 触发错误可能报出 DBMS 类型：`0/@@SERVERNAME`

6. **MySQL** 有内置的 `BENCHMARK()` 函数，可以测试某些特定操作的执行速度。

### SQL注入不存在回显怎么办？

1. 因为关闭了错误回显/没有回显位
2. 使用延时注入或布尔盲注
3. DNSLog 外带数据取回显

### MySQL 数据库站点无法链接的原因

1. MySQL 数据库链接不对外开放，只允许本地连接
2. 站库分离
3. 更改了端口

### MySQL 写 Shell 有几种方式？

1. 创建表导出
2. 一句话导出（INTO OUTFILE）
3. 日志备份获取 Shell（general_log / slow_query_log）

### MySQL 无法写 Shell 的原因

1. `my.ini` 配置 `secure-file-priv` 不为空或不包含目标路径
2. 绝对路径不正确
3. 权限不足/没有读写权限
4. 站库分离

---

## CSRF

### CSRF 原理

客户端跨站请求伪造（Cross-Site Request Forgery），攻击者诱导受害者进入第三方网站，向被攻击网站发送跨站请求，利用受害者在被攻击网站已获取的注册凭证，达到冒充用户执行操作的目的。

### CSRF 利用

构造好恶意请求包，配合钓鱼。

### CSRF 防御

1. 验证 HTTP Referer 字段
2. 添加 Token 字段并验证
3. 添加自定义字段并验证
4. 同源检测

### CSRF Token 的位置及绕过

Token 通常放在表单隐藏字段或请求头中。绕过思路：利用 XSS 读取同域下的 CSRF Token 后携带 Token 发起请求。

---

## XXE

### XXE 原理

XML 外部实体注入（XML External Entity），在应用程序解析 XML 输入时，当允许引用外部实体时，可构造恶意内容，产生漏洞。

服务端解析用户提交的 XML 文件时，未对 XML 文件引用的外部实体（含外部一般实体和外部参数实体）做合适的处理，并且实体的 URL 支持 `file://` 和 `ftp://` 等协议，导致可加载恶意外部文件和代码，造成任意文件读取、命令执行、内网端口扫描、攻击内网网站等危害。

### XXE 防御

XML 解析库在调用时严格禁止对外部实体的解析。

---

## 反序列化

### Java 反序列化原理

- **序列化**：把 Java 对象转换为字节序列的过程
- **反序列化**：把字节序列恢复为 Java 对象的过程

Java 应用对用户输入（即不可信数据）做了反序列化处理，那么攻击者可以通过构造恶意输入，让反序列化产生非预期的对象，非预期的对象在产生过程中就有可能带来任意代码执行。

### Java 序列化数据特征

- **序列化文件头**：数据 16 进制中以 `AC ED 00 05` 开头
- **TCP**：必有 `AC ED 00 05`，这个 16 进制流基本上意味着 Java 反序列化的开始
- **HTTP**：必有 `rO0AB`，这是 `AC ED 00 05` 的 Base64 编码结果
