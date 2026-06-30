---
title: CTF MISC杂项学习笔记
date: 2024-11-05
tags: [MISC, CTF, 隐写术, 文件分析, 学习笔记]
---

## MISC 杂项

### 文件的识别与分离

#### linux 环境下的命令行(in terminal)：

###### 文件的识别

1.file:filename 识别文件的类型（会显示各个文件的后缀名和大小）

2.binwalk:filename 分析文件内部是否还有别的文件然后一一显示出来

3.使用 010-Editior 或别的编译器（Nodepad++（记得装 HEX-editior 插件））以十六进制模式打开图片，查看文件头类型，通过比较文件头类型查看图片

![](学习笔记_md_files/04c99cd0-6961-11ee-8df0-e1bbcbe92c3c_20231013083949.jpeg?v=1\&type=image\&token=V1%3Aa0sAGyD2od6DiUcIvzqXmYEdOBhqxyrmzWjNNLamYEg)

###### 文件的分离

binwalk-e:filename

foremost namein(分析的文件) -o nameout(输出的文件夹)

以上是自动分离

dd if\=源文件 of\=目标文件夹 bs\=块大小(以字节为单位) count(取到第几块) skip 跳到哪一块

（手动分离）

例子：123456ABCDEF 将其分为 4 块 123 456 ABC DEF&#x20;

此时 bs\=3，若要取 123456 则 count\=2

若取 456 则加上 skip\=1(跳过一块)

图片的手动分离也是一样的思路，先用 binwalk 分析文件会显示哪里到哪里是 jpg,哪里到哪里是 zip 然后进行

分割

![](学习笔记_md_files/52669f40-6963-11ee-8df0-e1bbcbe92c3c_20231013085618.jpeg?v=1\&type=image\&token=V1%3ASlq7GlgMQcuw2AoFuALnoO31o8PjBxe7BFtbNZskXSY)

如图示

0 到 40 为第一个 zip

我们可以设置 bs\=1 如果想提取第二个 zip 我们可以这样写

dd if\=源文件 of\=目标文件夹 bs\=1(以字节为单位) count:88 skip40

以上是手动分离

其他 Linux 指令：

cat:filename 查看文件里的东西

cd:url 切换

###### 文件的合并

MD5 确保信息完整的算法

cat:合并的文件，中间用空格隔开>输出文件（以什么形式输出）

md5sum：filename 显示 md5 对比查看信息是否完整

#### windows 环境下的命令行：

###### 文件的合并

copy/B：url(使用时要使用完整的路径，建议直接手拖)

certutil -hashfile filename MD5(还可以监测别的算法)检验完整性

#### 题外:

###### 文件内容的隐写

直接将 flag/key 藏在未转十六进制码的文件当中

软件-》搜索-》查找，以下用 nodepad++举例

![](学习笔记_md_files/fa1799b0-6968-11ee-8df0-e1bbcbe92c3c_20231013093647.jpeg?v=1\&type=image\&token=V1%3APMpZTE4jtzBRei_jTNfb55gMI28P4d2s5iV5bvBRIIs)

### 图片文件的隐写

#### ps 图层问题

使用 ps 工具分开图层查看 flag

#### exif（可交换图像文件的查看）

Exif 可以被附加在 JPEG、TIFF、RIFF 等文件之中，为其增加有关数码相机拍摄信息的内容和缩略图或[图像处理软件](https://www.zhihu.com/search?q=%E5%9B%BE%E5%83%8F%E5%A4%84%E7%90%86%E8%BD%AF%E4%BB%B6\&search_source=Entity\&hybrid_search_source=Entity\&hybrid_search_extra=%7B%22sourceType%22%3A%22answer%22%2C%22sourceId%22%3A920241061%7D)的一些版本信息，是一种可交换图像文件

通常会在生成这张图片的时候附加 flag

图片右键属性查看 exif 信息

linux 环境中 exiftool:filename 也可以查看（caption abstract 标题摘要）

#### LSB 隐写

##### LSB 隐写原理

我们知道，一个像素点是由 R(red)B(blue)G(green)三原色组成的，通过调配这三种颜色，我们可以得到所有的颜色，比如白色(255,255,255)，二进制就是 bin(11111111,11111111,11111111)，黑色(0,0,0)，二进制就是(00000000,00000000,00000000)，既然如此，我们将每个二进制的最后一位给替换成别的，比如将(255,255,255)替换成(254,254,254),bin(11111110,11111110,11111110),肉眼根本分辨不出，因此我们将需要的信息转成二进制，只改变最后一位，便完成了 LSB 隐写。

![](学习笔记-misc_md_files/17f4cb60-6a54-11ee-869b-e5db069cf7af_20231014133948.jpeg?v=1\&type=image\&token=V1%3AEZZAmessTfKKBa2ooCspSLQexClge38EJjPyXVubJMQ)

##### Stegsolve 工具的使用

![](学习笔记-misc_md_files/04105e10-6a55-11ee-869b-e5db069cf7af_20231014134624.jpeg?v=1\&type=image\&token=V1%3AQR_HJ6QCiVfBdaMBucOg26kaUg2uiUq1pmq1-PdKaRo)

###### FIle Format 文件格式

查看图片具体信息，有时图片隐写的 flag 会藏在这

###### Data Extract:数据提取

![](学习笔记-misc_md_files/95f50010-6a55-11ee-869b-e5db069cf7af_20231014135029.jpeg?v=1\&type=image\&token=V1%3AKry7NuwjbAqzbgfkALFjuTwCzMzHGjpNykbTi3qk9GI)

Bit planes 位平面，用二进制位来表示图像的颜色

R,G,B 三层颜色通道构成的图像，位数越高代表该颜色通道中该颜色占比最多

Bit Order 在串行发送多字节数据时，比特层面的数据发送顺序。

###### Steregram Solve:立体试图&#x20;

可以左右控制偏移

###### Frame Browser:帧浏览器

逐帧分解 gif 图片

###### Image Combiner:拼图

图片拼接，将两张图片进行 XOR 异或运算，ADD 加法运算，或者 SUB 减法运算

从而看是否能够得到有效信息

##### zsteg 工具的使用（直接将 LSB 可能出现的多种情况列举出来）

也就是不用像上面那个工具一样手动点

###### 工具安装

[隐写工具 zsteg 安装+使用教程-CSDN 博客](https://blog.csdn.net/Amherstieae/article/details/107512398#:~:text=%E5%AE%89%E8%A3%85gem%EF%BC%88Kali2020%E7%89%88%E9%9C%80%E8%A6%81root%E6%9D%83%E9%99%90%EF%BC%8C%E5%91%BD%E4%BB%A4%E5%89%8D%E6%B7%BB%E5%8A%A0sudo%EF%BC%89%EF%BC%88%E8%BF%99%E4%B8%80%E6%AD%A5%E9%9C%80%E8%A6%81%E7%AD%89%E5%BE%85%E4%B8%80%E4%B8%8B%E4%B8%8B%EF%BC%89%20%EF%BC%88%E5%A6%82%E6%9E%9C%E4%B8%8D%E6%8D%A2%E6%BA%90%E7%9A%84%E8%AF%9D%EF%BC%8C%E4%BC%9A%E7%AD%89%E5%BE%85%E8%80%81%E9%95%BF%E6%97%B6%E9%97%B4%E7%84%B6%E5%90%8E%E6%8A%A5%E4%B8%AA%E9%94%99%EF%BC%88%E7%AD%89%E5%BE%85%EF%BC%8C%E6%B0%B8%E8%BF%9C%E7%9A%84%E7%AD%89%E5%BE%85~%EF%BC%89%20apt-get%20install%20gem,1%20%E5%AE%89%E8%A3%85zsteg%EF%BC%9A%20gem%20install%20zsteg)

###### 使用方式

zsteg filename

##### wbstego4open 工具的使用

[【PDF 隐写】wbStego4open，且还包括 BMP、 TXT、 HTM 文件隐写\_黑色地带(崛起)的博客-CSDN 博客](https://blog.csdn.net/qq_53079406/article/details/123783006?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522169726476916800185862642%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D\&request_id=169726476916800185862642\&biz_id=0\&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-123783006-null-null.142^v96^pc_search_result_base5\&utm_term=wbstego4%E5%B7%A5%E5%85%B7\&spm=1018.2226.3001.4187)

BMP 标准图像文件格式，包含图像信息丰富，几乎不进行压缩

#### 图片的修复

##### 图片宽高的修复

图片宽高显示不全，右键查看属性看高度(tweakpng 查看像素大小)，转化为十六进制再在编译器里面进行更改

// IHDR 文件头数据块

// PHYS:pixelsize 像素大小

当然可以用 python 脚本直接修复源文件问题

##### crc 矫错冗余码修复

crc 错误会让图片显示不出或显示不全

使用 Tweakpng 检验，用编译器查找替换

#### 加密图片的解密

##### SilentEye

该工具可以将文字隐藏在图片中，也可以解密

##### Stegdetect

工具探测加密方式,探测哪些工具加密

##### CQ 二维码扫描工具

扫描转化成十六进制得到 flag

如果扫描不出考虑用 stegsolve 进行运算（彩色的情况），有可能需要取反（黑白反过来）

#### 压缩包分析

##### 基础知识

ZIP 格式：

压缩源文件数据区【文件头（50 4B 03 04）+数据+数据描述符】+压缩源文件目录（50 4B 01 02）+目录结束标记(50 4B 05 06)

压缩源文件数据区 50 4B 03 04：这是头文件标记 &#x20;

14 00：解压文件所需 pkware 版本 &#x20;

00 00：全局方式位标记（判断有无加密）\
08 00：压缩方式\n\
5A 7E：最后修改文件时间\n\
F7 46：最后修改文件日期

压缩源文件目录区（比起压缩源文件数据区只多加了一行）&#x20;

1F 00：压缩使用的 pkware 版本

Rar 格式

分四个文件块（标记块，压缩文件头部块（前两个顺序 1 紧跟 2 其他无顺序），文件块，结束块）

每块都有 headcrc headtype headflages headsize addsize

RAR 的标记块和结束块都是固定的 7 字节序列，

分别为 0x52 61 72 21 1A 07 00（head flags）和 0xC4 3D 7B 00 40 07 00。

文件块这边要注意一下 HEAD\_FLAGS 这个头部，其中 HEAD\_FLAGS 的低三位代表加密标志，此位若被置为 1，则文件使用了基于密钥的加密。

![](学习笔记-misc_md_files/93d0e2b0-7a1b-11ee-9ce6-6111ca1419bd_20231103153535.jpeg?v=1\&type=image\&token=V1%3AIFO4__C77qaGB5LGACb7yCoBKyZLkrACdXSt3qwe4SI)

##### 伪加密

![](学习笔记-misc_md_files/e3a6c580-7a1a-11ee-9ce6-6111ca1419bd_20231103153040.jpeg?v=1\&type=image\&token=V1%3AFZ5SIy0krLT7UmEIkUa1kd3XQYkXOmvag9Xl9NgvcOA)

ZIP 核心目录后有个检验码，数到第九第十位如果不是 00 则说明伪加密

Rar 数到 检验码在第 24 个字节处要改 00

##### 暴力破解

ARCHPR.exe 暴力破解密码

选取选取密码范围，字符集，

攻击类型：

暴力（强行）

字典（存储着常用的密码，需要外源导入）

掩码攻击（知道了密码某几位的构造）

明文攻击

原理是当你不知道一个 zip 的密码，但是你有 zip 中的一个已知文件（文件大小要大于 12Byte）或者已经通过其他手段知道 zip 加密文件中的某些内容时，因为同一个 zip 压缩包里的所有文件都是使用同一个加密密钥来加密的，所以可以用已知文件来找加密密钥，利用密钥来解锁其他加密文件\~

注释：导入明文的时候，该明文要进行同样的压缩算法

CRC32

CRC32:CRC 本身是“冗余校验码”的意思，CRC32 则表示会产生一个 32bit（8 位十六进制数）的校验值。

在产生 CRC32 时，源数据块的每一位都参与了运算，因此即使数据块中只有一位发生改变也会得到不同的 CRC32 值，利用这个原理我们可以直接爆破出加密文件的内容\~

我们可以写出如下脚本：

    #coding=utf=8
    import binascii
    real = 0x56EA988D
    for y in range(1000,9999):
        if real == (binascii.crc32(str(y)) & 0xffffffff):
            print(y)
    print('End')


<!-- more -->
python 环境输入这一串就好了

### 色阶

<https://uyanide.github.io/Mirage_Decode/>

## 结论部分（可以直接使用）

### jpg 辨别

在 010 文件查看的时候，右边看到有 y0ya--->为 jpg 一般来说，都会含有开头和结尾

### 图片大小判断

位图，点阵图，由若干个像素组成

图片的实际大小\=图片高度*图片宽度*3 每个像素点由 3 个字节表示。

bpg 文件类型打开

以下是 PNG 文件中一些常见的块类型：

*   **IHDR**：图像头信息块，包含图像的宽度、高度、位深、颜色类型等基本信息。

*   **PLTE**：调色板块，用于索引颜色图像中的颜色。

*   **IDAT**：图像数据块，包含压缩的图像数据。

*   **IEND**：图像结束块，标志着文件的结束。

    一般同一个图片的 IDAT 块大小都一样，除了最后一个会小一点

`zlib` 压缩被用来减少文件大小，加快传输速度

一种新的隐写方式-------steghide

Steghide‌ 是一种隐写术软件，它允许用户将文件（如文本、图片或音频）隐藏在另一个文件中，通常是图片或音频文件。隐写术是一种将信息隐藏在其它非机密文件中，以避免引起怀疑的方法。Steghide 支持的文件类型包括 JPEG、BMP、WAV 等。使用 Steghide，用户可以通过命令行界面将秘密信息嵌入到图片或音频文件中，而原始文件看起来没有任何变化，从而实现了信息的秘密传输和存储。此外，Steghide 还支持密码保护功能，为用户提供了一定程度的数据安全保障 ‌

用法：

这里提一下使用方式： steghide embed -cf \[载体文件] -ef \[隐藏文件] -p 密码(可以为空) steghide extract -sf \[隐藏信息的文件]

使用 steghide extract -sf ./good-已合并.jpg -p 会提示让你输入密码，直接 enter 跳过，得到了一个文件 ko.txt

出题思路：

还可以用这个工具将两文件合并，用于隐藏信息。
