---
title: Apache配置笔记
date: 2024-05-23
tags: [PHP, Apache, 配置]
---


htdocs Apache默认的主机地址（网络根目录）
modules模块可以加载到conf里面
右下角绿色表示开启成功，黄色表示端口被占用
ab.exe压力测试，多少人能够承载

static静态加载
shared只有使用的时候才会加载
httpd.exe -t 检查配置文件是否能够使用
syntax ok证明没有语法错误
网站名字用010打开conf配置文件进行更改httpd.conf文件
端口可以单独实现Servername localhost:80
listen进行监听listen 80可以进行更改
lib（Library）静态链接库
dll文件是Dynamic Link Library（动态链接库）文件的缩写，它是一种共享库文件，包含了程序所需的代码和数据。与静态链接库不同，动态链接库可以在程序运行时动态加载，使得程序的内存占用更小，同时也方便了程序的更新和维护。


php的底层是c语言
c语言是编译语言 vc9代表编译环境
php dev device设备驱动 
ext扩展（extra）php很多功能通过扩展来实现
配置文件
php-ini-development开发版
php-ini-production生产版
php.exe -f ...php 解析php

apache加载php
LoadModule php_5 ''
分配任务给php
AddType applocation/x-httpd-php .php
加载配置文件
PHPIniDir ''
PHP的配置文件以及加入到Apache的配置项中，这意味着php.ini修改需要Apache重启以后才能生效

C/S用户需要客户端才能访问服务器 
B/S浏览器直接访问
Development开发环境，占用资源少
server 服务器环境，占用资源多


php加载mysql
php.ini为php的配置文件
extension=php_mysql.dll加载配置文件
phpinfo()检测php环境的一个函数
php所有的扩展都在ext文件夹里面
由于更换路径了（把php文件加载到了Apache中，则需要重新更改）
extension dir = " E : / server / php5 / ext
更改php的默认时区为当前时区（china
date.timezone=PRC
一点点积累，回头看一眼就懂
势必会受到很大的压力，因为我先学基础，人家先学拔高部分
人家慢慢巩固基础，而我到后期直接拔高，忘了最多回头看一眼，整理好自己的笔记，把
