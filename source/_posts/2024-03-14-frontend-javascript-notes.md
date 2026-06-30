---
title: 前端JavaScript开发学习笔记
tags: [前端开发, JavaScript, DOM, BOM, Web开发, 学习笔记]
date: 2024-03-14
---

# 前端JavaScript开发学习笔记

本文详细介绍了前端JavaScript开发的核心知识，包括JavaScript基础语法、作用域、数据类型、DOM操作、BOM对象、事件处理等重要内容，为前端开发者提供全面的技术指导。

<!-- more -->

## 1. JavaScript基础

### JavaScript用法

#### 1. 内部文件引用
将脚本代码放于`<script>`标签之间，然后放置在HTML页面的`<body>`和`<head>`部分中，或者body里面的尾部。

```html
<script>
    // JavaScript代码
    document.write("Hello World!");
</script>
```

#### 2. 外部文件引用
```html
<script src="myScript.js"></script>
```

### JavaScript语法基础

#### 基本语法规则
1. **分号**：用于分隔JavaScript语句
2. **换行**：使用`\n`表示换行
3. **注释**：
   - 单行注释：`//`
   - 多行注释：`/* */`
   - HTML注释：`<!-- -->`（用于兼容性检查）

#### 输出方法
JavaScript可以通过不同的方式来输出数据：

| 方法 | 描述 | 用途 |
|------|------|------|
| `window.alert()` | 弹出警告框 | 用户提示 |
| `document.write()` | 写入HTML文档 | 动态内容生成 |
| `innerHTML` | 写入HTML元素 | DOM操作 |
| `console.log()` | 写入浏览器控制台 | 调试输出 |

**注意**：`document.write()`在文档加载后使用会覆盖整个文档。

## 2. 作用域详解

### 作用域类型

#### 1. 块级作用域
任何一对花括号`{}`中的语句集都属于一个块，在这之中定义的所有变量在代码块外都是不可见的。

```javascript
if (true) {
    let blockVar = "块级变量";
    const blockConst = "块级常量";
}
// console.log(blockVar); // 错误：无法访问
```

#### 2. 函数作用域
定义在函数中的参数和变量在函数外部是不可见的。

```javascript
function myFunction() {
    var functionVar = "函数变量";
    return functionVar;
}
// console.log(functionVar); // 错误：无法访问
```

### 变量声明关键字对比

| 关键字 | 作用域 | 变量提升 | 重复声明 | 块级作用域 |
|--------|--------|----------|----------|------------|
| `var` | 函数作用域 | 是 | 允许 | 否 |
| `let` | 块级作用域 | 否 | 不允许 | 是 |
| `const` | 块级作用域 | 否 | 不允许 | 是 |

#### var的问题
- **忽视块级作用域**：在块级作用域中用var定义，外部可以访问
- **变量提升**：声明会被提升到作用域顶部，并被赋值为`undefined`
- **重复声明**：允许重复声明，容易造成变量名冲突

#### 推荐使用let和const
```javascript
// 推荐写法
for (let i = 0; i < 5; i++) {
    // i只在循环内有效
}

const PI = 3.14159; // 常量
let userName = "张三"; // 变量
```

## 3. 数据类型

### 基本数据类型（值类型）

| 类型 | 描述 | 示例 |
|------|------|------|
| **String** | 字符串 | `"Hello World"` |
| **Number** | 数字 | `42`, `3.14` |
| **Boolean** | 布尔值 | `true`, `false` |
| **Null** | 空值 | `null` |
| **Undefined** | 未定义 | `undefined` |
| **Symbol** | 符号（ES6） | `Symbol('id')` |

### 引用数据类型（对象类型）

| 类型 | 描述 | 示例 |
|------|------|------|
| **Object** | 对象 | `{name: "张三", age: 25}` |
| **Array** | 数组 | `[1, 2, 3, 4, 5]` |
| **Function** | 函数 | `function() {}` |
| **RegExp** | 正则表达式 | `/pattern/flags` |
| **Date** | 日期 | `new Date()` |

### 类型检测

#### typeof操作符
```javascript
typeof "Hello";     // "string"
typeof 42;          // "number"
typeof true;        // "boolean"
typeof undefined;   // "undefined"
typeof null;        // "object" (这是一个已知的bug)
typeof {};          // "object"
typeof [];          // "object"
```

#### 数组检测
```javascript
// 方法1：Array.isArray()
if (Array.isArray(cars)) {
    console.log("该对象是一个数组");
}

// 方法2：instanceof操作符
if (cars instanceof Array) {
    console.log("该对象是一个数组");
}
```

### null与undefined的区别

| 特性 | null | undefined |
|------|------|----------|
| **含义** | 表示变量将来可能指向一个对象 | 表示变量声明过但未赋值 |
| **用途** | 主动释放对象引用 | 系统默认值 |
| **类型** | object（历史原因） | undefined |

```javascript
// undefined示例
var a; // a自动被赋值为undefined

// null示例
var emps = ['张三', '李四'];
emps = null; // 释放指向数组的引用
```

## 4. 字符串操作

### 字符串访问

#### 数组索引访问
```javascript
const name = "RUNOOB";
let letter = name[2]; // "N"
```

#### 长度获取
```javascript
let len = name.length; // 6
```

### 模板字符串（ES6）

使用反引号`` ` ``作为字符串分隔符，支持变量和表达式嵌入。

```javascript
// 变量嵌入
const userName = "张三";
const greeting = `你好，${userName}！`;

// 表达式嵌入
const a = 5, b = 10;
const result = `${a} + ${b} = ${a + b}`;

// 函数调用
function getName() {
    return "李四";
}
const message = `欢迎 ${getName()}！`;

// 多行字符串
const multiLine = `
第一行
第二行
第三行
`;
```

### 转义字符

| 转义字符 | 描述 |
|----------|------|
| `\n` | 换行 |
| `\t` | 制表符 |
| `\"` | 双引号 |
| `\'` | 单引号 |
| `\\` | 反斜杠 |

## 5. 函数

### 函数声明

#### 1. 函数声明式
```javascript
function myFunction(param1, param2) {
    var x = 5;
    return x + param1 + param2;
}
```

#### 2. 函数表达式
```javascript
// 匿名函数表达式
var myFunction = function(param1, param2) {
    return param1 + param2;
};

// 命名函数表达式
var myFunction = function namedFunction(param1, param2) {
    return param1 + param2;
};
```

#### 3. 箭头函数（ES6）
```javascript
// 基本语法
const add = (a, b) => a + b;

// 多行函数体
const multiply = (a, b) => {
    const result = a * b;
    return result;
};

// 单参数可省略括号
const square = x => x * x;
```

## 6. 循环和控制结构

### for...in循环
用于遍历对象的属性。

```javascript
var person = {
    fname: "Bill",
    lname: "Gates",
    age: 56
};

var txt = "";
for (x in person) { // x为属性名
    txt = txt + person[x]; // person[x]为属性值
}
```

### break和continue

- **break**：跳出代码块，可用于循环和switch
- **continue**：进入下一个迭代，只能用于循环

```javascript
// break示例
for (let i = 0; i < 10; i++) {
    if (i === 5) {
        break; // 跳出整个循环
    }
    console.log(i);
}

// continue示例
for (let i = 0; i < 10; i++) {
    if (i === 5) {
        continue; // 跳过当前迭代
    }
    console.log(i);
}
```

## 7. 变量提升

### 概念
JavaScript中，函数及变量的声明都将被提升到函数的最顶部。

```javascript
// 这样写是可以的
x = 5; // 变量x设置为5
elem = document.getElementById("demo");
elem.innerHTML = x; // 显示x的值
var x; // 声明x
```

### 重要注意事项

**初始化不会提升**：

```javascript
// 错误示例
console.log(y); // undefined（不是5）
var y = 5;

// 等价于
var y;
console.log(y); // undefined
y = 5;
```

**let和const不存在变量提升**：

```javascript
// 这会报错
console.log(z); // ReferenceError
let z = 10;
```

## 8. 正则表达式

### RegExp对象

正则表达式是描述字符模式的对象，用于字符串模式匹配及检索替换。

#### 创建方式

```javascript
// 方法1：构造函数
var patt = new RegExp(pattern, modifiers);

// 方法2：字面量（推荐）
var patt = /pattern/modifiers;
```

#### 修饰符

| 修饰符 | 描述 |
|--------|------|
| `g` | 全局匹配 |
| `i` | 忽略大小写 |
| `m` | 多行匹配 |

#### 常用方法

```javascript
var pattern = /hello/gi;
var text = "Hello World, hello JavaScript!";

// test()：测试是否匹配
console.log(pattern.test(text)); // true

// exec()：执行搜索
console.log(pattern.exec(text)); // 返回匹配信息

// 字符串方法
console.log(text.match(pattern)); // 返回匹配数组
console.log(text.replace(pattern, "hi")); // 替换匹配内容
```

## 9. 面向对象编程

### 类（ES6）

#### 类定义
```javascript
class ClassName {
    constructor(param1, param2) {
        this.property1 = param1;
        this.property2 = param2;
    }
    
    method1() {
        return this.property1;
    }
    
    method2() {
        return this.property2;
    }
}

// 创建实例
let instance = new ClassName("值1", "值2");
```

#### 类继承
```javascript
class ParentClass {
    constructor(name) {
        this.name = name;
    }
    
    speak() {
        console.log(`${this.name} 正在说话`);
    }
}

class ChildClass extends ParentClass {
    constructor(name, age) {
        super(name); // 调用父类构造函数
        this.age = age;
    }
    
    introduce() {
        console.log(`我是 ${this.name}，今年 ${this.age} 岁`);
    }
}

let child = new ChildClass("小明", 18);
child.speak(); // 继承的方法
child.introduce(); // 自己的方法
```

### 原型链

所有JavaScript对象都会从一个prototype（原型对象）中继承属性和方法。所有JavaScript中的对象都是位于原型链顶端的Object的实例。

```javascript
// 构造函数
function Person(name, age) {
    this.name = name;
    this.age = age;
}

// 原型方法
Person.prototype.sayHello = function() {
    console.log(`你好，我是 ${this.name}`);
};

// 创建实例
let person1 = new Person("张三", 25);
let person2 = new Person("李四", 30);

person1.sayHello(); // "你好，我是 张三"
person2.sayHello(); // "你好，我是 李四"
```

## 10. DOM操作

### DOM概念

DOM（Document Object Model）即文档对象模型，是W3C制定的标准接口规范，是一种处理HTML和XML文件的标准API。

#### 核心概念
- **文档（document）**：一个页面就是一个文档
- **元素（element）**：文档中的所有标签都是元素
- **节点（node）**：文档中所有的内容都是节点（标签、属性、文本）

**关系**：文档包含节点，节点包含元素

### 常用DOM方法

#### 获取元素
```javascript
// 通过ID获取
var element = document.getElementById("myId");

// 通过类名获取
var elements = document.getElementsByClassName("myClass");

// 通过标签名获取
var elements = document.getElementsByTagName("div");

// 通过CSS选择器获取
var element = document.querySelector(".myClass");
var elements = document.querySelectorAll(".myClass");
```

#### 修改内容
```javascript
// 改变HTML内容
document.getElementById("myId").innerHTML = "新的HTML内容";

// 改变文本内容
document.getElementById("myId").textContent = "新的文本内容";
```

#### 修改属性
```javascript
// 改变HTML属性
document.getElementById("myId").src = "new-image.jpg";
document.getElementById("myId").href = "https://example.com";

// 设置自定义属性
document.getElementById("myId").setAttribute("data-value", "123");
```

#### 修改样式
```javascript
// 改变CSS样式
document.getElementById("myId").style.color = "blue";
document.getElementById("myId").style.fontSize = "20px";
document.getElementById("myId").style.display = "none";

// 添加/移除CSS类
element.classList.add("newClass");
element.classList.remove("oldClass");
element.classList.toggle("toggleClass");
```

## 11. BOM对象

### Window对象

Window对象是浏览器的顶级对象，代表浏览器窗口。

#### window.history对象
```javascript
// 后退
history.back();

// 前进
history.forward();

// 跳转到指定页面
history.go(-2); // 后退2页
history.go(1);  // 前进1页
```

#### window.location对象
```javascript
// 获取当前页面信息
console.log(location.hostname); // 域名
console.log(location.pathname); // 路径和文件名
console.log(location.port);     // 端口号
console.log(location.protocol); // 协议
console.log(location.href);     // 完整URL

// 页面跳转
location.assign("https://example.com"); // 跳转到新页面
location.reload(); // 刷新页面
location.replace("https://example.com"); // 替换当前页面
```

#### window.navigator对象
```javascript
// 获取浏览器信息
console.log(navigator.userAgent);   // 用户代理字符串
console.log(navigator.platform);    // 操作系统平台
console.log(navigator.language);    // 浏览器语言
console.log(navigator.cookieEnabled); // 是否启用Cookie
```

### JavaScript弹窗

#### 三种消息框

```javascript
// 1. 警告框
alert("这是一个警告消息！");

// 2. 确认框
var result = confirm("你确定要删除这个文件吗？");
if (result) {
    console.log("用户点击了确定");
} else {
    console.log("用户点击了取消");
}

// 3. 提示框
var userInput = prompt("请输入您的姓名：", "默认值");
if (userInput !== null) {
    console.log("用户输入了：" + userInput);
}
```

**换行设置**：使用`\n`来设置换行
```javascript
alert("Hello\nHow are you?");
```

## 12. Cookie操作

### Cookie基础

Cookie用于存储web页面的用户信息，通过`document.cookie`进行操作。

#### 创建和读取Cookie
```javascript
// 创建Cookie
document.cookie = "username=张三; expires=Thu, 18 Dec 2024 12:00:00 GMT; path=/";

// 读取Cookie
var allCookies = document.cookie;
console.log(allCookies);
```

#### Cookie操作函数

```javascript
// 设置Cookie
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toGMTString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

// 获取Cookie
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

// 删除Cookie
function deleteCookie(cname) {
    document.cookie = cname + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
}

// 使用示例
setCookie("username", "张三", 7); // 设置7天后过期
var username = getCookie("username"); // 获取用户名
deleteCookie("username"); // 删除Cookie
```

## 13. 内存管理

### 栈与堆

#### 基本类型（栈内存）
基本类型的变量存放在栈内存中，包括变量标识符和变量值。

```javascript
var a, b;
a = "张三";
b = a;
console.log(a); // 张三
console.log(b); // 张三
a = "李四";     // 改变a的值，不影响b的值
console.log(a); // 李四
console.log(b); // 张三
```

#### 引用类型（堆内存）
引用类型的值保存在堆内存中，栈内存中保存变量标识符和指向堆内存的指针。

```javascript
var a = {name: "张三"};
var b = a; // b指向同一个对象
a.name = "李四";
console.log(b.name); // 李四（因为指向同一个对象）

b.age = 25;
console.log(a.age); // 25（同样因为指向同一个对象）
```

## 14. 高级特性

### 数值处理

#### toFixed()方法
将浮点数转换为指定小数位数的字符串。

```javascript
var num = 3.14159;
console.log(num.toFixed(2)); // "3.14"
console.log(num.toFixed(0)); // "3"
console.log(num.toFixed(4)); // "3.1416"
```

### 类型转换

```javascript
// 转换为字符串
String(123);        // "123"
(123).toString();   // "123"
123 + "";          // "123"

// 转换为数字
Number("123");      // 123
parseInt("123px");  // 123
parseFloat("3.14"); // 3.14
+"123";            // 123

// 转换为布尔值
Boolean(1);         // true
Boolean(0);         // false
Boolean("");        // false
Boolean("hello");   // true
```

### constructor属性

constructor属性返回所有JavaScript变量的构造函数。

```javascript
"John".constructor;                 // 返回 String()
(3.14).constructor;                 // 返回 Number()
false.constructor;                  // 返回 Boolean()
[1,2,3,4].constructor;             // 返回 Array()
{name:'John', age:34}.constructor;  // 返回 Object()
new Date().constructor;             // 返回 Date()
function () {}.constructor;         // 返回 Function()
```

## 15. CSS布局基础

### 定位（Position）

```css
/* 相对定位：相对于元素正常位置 */
position: relative;
top: 10px;
left: 20px;

/* 绝对定位：相对于最近的已定位祖先元素 */
position: absolute;
top: 0;
right: 0;

/* 固定定位：相对于视口 */
position: fixed;
bottom: 0;
right: 0;
```

### Flexbox布局

```css
/* 容器属性 */
.container {
    display: flex;
    flex-wrap: wrap;              /* 允许换行 */
    justify-content: space-around; /* 水平对齐 */
    align-items: center;          /* 垂直对齐 */
    align-content: space-between; /* 多行对齐 */
}

/* 项目属性 */
.item {
    flex: 1;        /* 弹性增长 */
    flex-grow: 1;   /* 增长比例 */
    flex-shrink: 1; /* 收缩比例 */
    flex-basis: auto; /* 基础大小 */
}
```

### 背景图片

```css
.background {
    background-image: url('image.jpg');
    background-size: cover;    /* 覆盖整个容器 */
    background-size: contain;  /* 完全显示图片 */
    background-size: 100px 200px; /* 指定尺寸 */
    background-repeat: no-repeat;
    background-position: center;
}
```

## 16. 最佳实践

### 代码规范

1. **使用严格模式**
```javascript
"use strict";
```

2. **变量命名**
```javascript
// 使用驼峰命名法
var userName = "张三";
var userAge = 25;

// 常量使用大写
const MAX_COUNT = 100;
const API_URL = "https://api.example.com";
```

3. **函数设计**
```javascript
// 函数应该单一职责
function calculateTotal(price, tax) {
    return price + (price * tax);
}

// 使用默认参数
function greet(name = "朋友") {
    return `你好，${name}！`;
}
```

### 性能优化

1. **避免全局变量**
2. **使用事件委托**
3. **缓存DOM查询结果**
4. **使用文档片段批量操作DOM**

```javascript
// 缓存DOM查询
var container = document.getElementById('container');

// 使用文档片段
var fragment = document.createDocumentFragment();
for (var i = 0; i < 1000; i++) {
    var div = document.createElement('div');
    div.textContent = 'Item ' + i;
    fragment.appendChild(div);
}
container.appendChild(fragment);
```

### 调试技巧

1. **使用console方法**
```javascript
console.log("普通日志");
console.warn("警告信息");
console.error("错误信息");
console.table(arrayData); // 表格形式显示数组
console.time("timer");    // 开始计时
console.timeEnd("timer"); // 结束计时
```

2. **使用debugger语句**
```javascript
function problematicFunction() {
    var x = 10;
    debugger; // 浏览器会在此处暂停
    var y = x * 2;
    return y;
}
```

## 总结

JavaScript是现代Web开发的核心技术，掌握以下要点至关重要：

### 核心概念
1. **作用域和变量提升**：理解var、let、const的区别
2. **数据类型**：区分基本类型和引用类型
3. **函数**：掌握多种函数定义方式
4. **面向对象**：理解原型链和类的概念

### 实用技能
1. **DOM操作**：熟练操作页面元素
2. **事件处理**：响应用户交互
3. **异步编程**：处理网络请求和定时器
4. **调试技巧**：快速定位和解决问题

### 发展方向
1. **ES6+新特性**：箭头函数、解构赋值、模块化等
2. **框架学习**：React、Vue、Angular等
3. **工程化工具**：Webpack、Babel、ESLint等
4. **Node.js**：服务端JavaScript开发

持续学习和实践是掌握JavaScript的关键，建议通过实际项目来巩固所学知识。