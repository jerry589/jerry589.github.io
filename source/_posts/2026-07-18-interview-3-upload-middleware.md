---
title: 渗透测试面试系列三：文件上传、文件包含、未授权访问与中间件漏洞
tags: [面试, 渗透测试, 文件上传, 文件包含, 未授权访问, 中间件漏洞, 解析漏洞]
date: 2026-07-18
---

# 渗透测试面试系列三：文件上传、文件包含、未授权访问与中间件漏洞

<!-- more -->

## 文件上传绕过全分类

### 基于前端 JS

1. Burp 抓包修改绕过
2. 禁用指定 JS 文件

### 基于后端 MIME

1. 修改 Content-Type（文件 MIME）
2. 基于 Body 标识头

### 基于简单过滤

1. 双写后缀
2. 大小写

### 基于后端黑名单

拦截指定的后缀名。

**FUZZ 可利用扩展**：

1. FUZZ 可上传扩展名（不在黑名单，可被解析利用）
2. `.htaccess` 文件（Apache 服务器中的分布式配置文件，启用和关闭在 `httpd.conf` 文件中配置，`mod_rewrite` 模块开启，`AllowOverride All`）
3. `.user.ini` 文件（自 PHP 5.3.0 起，是一个能被动态加载的 ini 文件，此类文件仅被 CGI／FastCGI SAPI 处理。不需要重启服务器中间件，只需要等待 `user_ini.cache_ttl` 所设置的时间（默认为 300 秒），即可被重新加载）
4. HTML 文件（存储型 XSS）
5. SOAP、ASMX 文件（XML RCE）

### 系统特性绕过

1. 后缀添加空格、添加点、添加冒号，基于 Windows 特性被删除
2. 后缀添加斜杠，基于特性被删除（Windows/Linux）
3. 后缀添加 NTFS 数据流 `::$DATA`，基于特性（Windows）

### 容器解析特性绕过

1. **Apache 容器解析特性**（1.X/2.X 版本）：解析文件名的方式是从后向前识别扩展名，遇见可识别的扩展名为止，都不可识别则报错。例如 `/1.php.abcd` → 解析为 PHP
2. **Apache HTTPD 换行解析漏洞**（2.4.0-2.4.29 版本）：Burp 抓包，Hex 选项卡 `.php` 后面右键 Insert byte，添加一个 `0a`，访问 `1.php\x0a` 将被按照 PHP 后缀进行解析
3. **Nginx 空字节代码解析漏洞**（0.8.41~1.5.6）：`%20%00` 空字节代码解析

### 基于后端白名单

只允许指定的后缀名，需配合以下绕过：

1. **配置文件**：`.htaccess` 文件
2. **文件包含**：包含解析存在 WebShell 的文件
3. **Tomcat AJP 协议任务文件包含**
4. **ThinkPHP 任意文件包含日志 Getshell**

### IIS 解析漏洞

1. **IIS 目录解析**（5.X/6.0）：目录名包含 `.asp`、`.asa`、`.cer`、`.cdx`，目录下所有文件都按照 ASP 解析执行（如 `/test.asp/1.jpg`）
2. **IIS 文件名解析**（5.X/6.0）：文件名包含 `.asp;`、`.asa;`、`.cer;`、`.cdx;`，优先按照 ASP 解析执行（如 `/1.asp;1.jpg`）

### PHP CGI 解析漏洞

`php.ini` 配置文件 `cgi.fix_pathinfo=1`，访问 `/1.jpg/1.php` 或 `/1.jpg/.php`，`1.jpg` 以 PHP 来解析。

### 编辑器漏洞

- UEditor 任意文件上传
- FCKeditor 编辑器
- eWebEditor 编辑器
- DotNetTextBox 编辑器
- Kedit 编辑器
- Cute Editor 在线编辑器

---

## 文件包含

### 原理

文件包含函数（include/require 等）将指定文件的内容读入并作为 PHP 代码解析执行。

### 利用方式

1. 包含日志文件（如 ThinkPHP 日志文件包含）
2. 包含被污染的 SSH 日志来 Getshell
3. 包含图片马
4. 包含 Session 文件
5. file 协议
6. PHP 伪协议（php://filter、php://input、data://、phar:// 等）

### PHP 文件包含函数

| 函数 | 说明 |
|------|------|
| `require` | 一般放在 PHP 脚本最前面，执行前先读入指定文件；出错抛出警告并退出 |
| `require_once` | 只包含一次，避免函数重定义和变量重复赋值 |
| `include` | 可放在脚本任意位置，执行到时才包含；出错抛出警告但程序继续 |
| `include_once` | 只包含一次 |

---

## 常见业务逻辑漏洞

- 任意用户密码重置
- 短信轰炸
- 支付漏洞
- 忘记密码绕过
- 验证码复用
- 越权（水平/垂直）

### 支付漏洞

后端与前端检验不严谨，缺乏多重校验。

### 越权原理与分类

**原理**：缺乏对用户身份的严格校验，存在缺陷的验证机制。

**分类**：

- **垂直越权**：用户权限提升/切换（普通用户执行管理员操作）
- **水平越权**：用户身份切换/平权（用户A查看用户B的数据）

---

## 常见未授权访问漏洞

1. MongoDB 未授权访问漏洞
2. Redis 未授权访问漏洞
3. Memcached 未授权访问漏洞
4. JBoss 未授权访问漏洞
5. VNC 未授权访问漏洞
6. Docker 未授权访问漏洞
7. ZooKeeper 未授权访问漏洞
8. Rsync 未授权访问漏洞
9. 阿里 Druid 未授权访问

### Redis 未授权原理与利用

**原理**：

1. 没有设置登录验证导致免密码登录
2. 没有 IP 限制
3. 没有开启安全模式

**利用**：

1. 写入公钥
2. 写 WebShell
3. 计划任务反弹 Shell

---

## 常见中间件漏洞

| 中间件 | 漏洞类型 |
|--------|---------|
| **IIS** | PUT 漏洞、短文件名猜解、远程代码执行、解析漏洞 |
| **Apache** | 解析漏洞、目录遍历 |
| **Nginx** | 文件解析、目录遍历、CRLF注入、目录穿越 |
| **Tomcat** | 远程代码执行、WAR 后门文件部署 |
| **JBoss** | 反序列化漏洞、WAR 后门文件部署 |
| **WebLogic** | 反序列化漏洞、SSRF、任意文件上传、WAR 后门文件部署 |
| **Apache Shiro** | 反序列化漏洞（Shiro-550、Shiro-721） |

### 存在任意文件读取的框架/中间件/组件

- 蓝凌 OA 前台任意文件读取
- Apache
- Apache Tomcat

### 存在 SSRF 的框架/中间件/组件

- WebLogic

### 存在反序列化的中间件

- JBoss
- Shiro
- Apache Tomcat
- WebLogic
- Fastjson

### WebLogic 存在哪些漏洞？

1. 基于 WebLogic T3 协议引起远程代码执行的反序列化漏洞
2. 通过非法字符绕过访问，然后通过 Gadget 调用命令执行
3. 任意文件上传

### Apache Tomcat 存在哪些漏洞？

- CVE-2017-12615：任意写文件漏洞
- CVE-2020-1938：AJP 文件包含漏洞（幽灵猫）
- 后台弱口令 Getshell

---

## 绝对路径获取方法

1. 报错信息
2. Fuzz 探测
3. PHP 探针

## JSON 格式的数据包测哪些漏洞？

Fastjson 反序列化。

## Cookie 字段你会测试什么内容？

- SQL 注入
- 越权
- Log4j2
- Shiro
- Cookie 安全属性
