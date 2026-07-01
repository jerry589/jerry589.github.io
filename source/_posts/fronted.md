---
title: JavaScript 学习笔记
date: 2025-08-25
tags: [JavaScript, 前端开发, 学习笔记]
---

# JavaScript 学习笔记

## Js 用法


<!-- more -->
### 1. 内部文件引用

将脚本代码放于 **\<script>** 标签之间，然后放置在 HTML 页面的 **\<body>** 和 **\<head>** 部分中，或者 body 里面的尾部。

### 2. 外部文件引用

```html
<script src="myScript.js"></script>
```

## Js 语法

1. 分号用于分隔 JavaScript 语句。

2. `document.write("你好 \ 世界!");` /* \*\表示换行 \*\*/

3. 注释/*，//，如果用户不能确定浏览器是否支持 JavaScript 脚本，那么可以应用 HTML 提供的注释符号进行验证。HTML 注释符号是以 **<--** ！开始以 **-->** 结束的

## JS 作用域

最开始只有 var 全局变量和局部变量的概念

### 1. 块级作用域

任何一对花括号 {} 中的语句集都属于一个块，在这之中定义的所有变量在代码块外都是不可见的，我们称之为块级作用域。比如 if(){} ,for(){}中的花括号都是块级作用域

### 2. 函数作用域

很明显是 function(){}的形式，定义在函数中的参数和变量在函数外部是不可见的

而三个变量中 var 是忽视块级作用域的，也就是说在块级作用域中用 var 定义，在外部是可以访问到变量值得，var 只有在函数作用域中声明外部才不能访问。而且 var 声明的变量会被声明提前，被提升到作用域顶部，并被赋值为 undefinded

const 和 let 是有块级作用域概念的，也就是说在块级作用域中用 const 或者 let 定义，外部无法访问变量！且不可以声明提前

### 3. 设置 let 原因(重新定义变量的问题)

![](https://gitee.com/jerry798/xcximg/raw/master/img/af9dc420-7efa-11ee-99c1-9fb38d38c90b.jpeg)

因此在 Function 中局部变量推荐使用 let 变量，避免变量名冲突

相同的作用域或块级作用域中,var,let 不能互相重置，但**let** 关键字在不同作用域，或不同块级作用域中是可以重新声明赋值的

## JS 显示数据

JavaScript 可以通过不同的方式来输出数据：

- 使用 **window.alert()** 弹出警告框。
- 使用 **document.write()** 方法将内容写到 HTML 文档中。/*_使用它相当于添加在原有 html 代码中添加一串 html 代码。而如果在文档加载后使用（如使用函数），会覆盖整个文档 _*/
- 使用 **innerHTML** 写入到 HTML 元素。
- 使用 **console.log()** 写入到浏览器的控制台。

## JS 数据类型

### 值类型(基本类型)：

- 字符串（String）、数字(Number)、布尔(Boolean)、空（Null）、未定义（Undefined）、Symbol。

### 引用数据类型（对象类型）：

- 对象(Object)、数组(Array)、函数(Function)，还有两个特殊的对象：正则（RegExp）和日期（Date）。

### 声明变量类型

当您声明新变量时，可以使用关键词 "new" 来声明其类型：

```javascript
var arr3 = new Array();
```

### 对象内部用键值对来表示

```javascript
var person = {firstname:"John", lastname:"Doe", id:5566};
```

## js 字符串

### 数组索引访问字符串

```javascript
const name = "RUNOOB";
let letter = name[2];
```

### 长度

```javascript
let len = name.length;
```

### 特殊写法

```javascript
document.write("p" + txt.length + "/p");
```

### 转义字符

## JS 类型转换

**String()** 可以将数字转换为字符串

**Number()** 可以将字符串转换为数字

## JS 函数

### 函数声明

```javascript
function myFunction() {
    var x = 5;
    return x; // 单个 return 也可以结束函数
}
```

### 函数表达式

可以将函数表达式存储在变量中然后作为**匿名函数**使用

## JS 循环

```javascript
var person = {fname:"Bill", lname:"Gates", age:56};

for (x in person) { // x 为属性名
    txt = txt + person[x]; // person[x]属性值
}
```

![](https://gitee.com/jerry798/xcximg/raw/master/img/0e4b0820-8063-11ee-ba70-95ea6d5014dc.jpeg)

break 的作用是跳出代码块, 所以 break 可以使用于循环和 switch 等

continue 的作用是进入下一个迭代, 所以 continue 只能用于循环的代码块。

代码块: 基本上是｛｝大括号之间

## js 变量提升

JavaScript 中，函数及变量的声明都将被提升到函数的最顶部。

变量可以在使用后声明，也就是变量可以先使用再声明。

```javascript
x = 5; // 变量 x 设置为 5
e = document.getElementById("demo"); // 查找元素
e.innerHTML = x; // 在元素中显示 x
var x; // 声明 x
```

answer: x=5

**初始化不会提升**

在后面赋值不会被用到前面

![](https://gitee.com/jerry798/xcximg/raw/master/img/5befc610-7f91-11ee-b32b-a1aa6ea31392.jpeg)
![](https://gitee.com/jerry798/xcximg/raw/master/img/a7623240-7f91-11ee-b32b-a1aa6ea31392.jpeg)

## JavaScript 正则表达式

### RegExp 对象

正则表达式是描述字符模式的对象。

正则表达式用于对字符串模式匹配及检索替换，是对字符串执行模式匹配的强大工具。

```javascript
var patt = new RegExp(pattern, modifiers);
// 或者更简单的方式:
var patt = /pattern/modifiers;
```

pattern（模式） 描述了表达式的模式

modifiers(修饰符) 用于指定全局匹配、区分大小写的匹配和多行匹配

### 语法

```javascript
var patt = new RegExp(pattern, modifiers);

// 或者更简单的方式:
var patt = /pattern/modifiers;
```

## JS 模板字符串

JavaScript 中的模板字符串是一种方便的字符串语法，允许你**在字符串中嵌入表达式和变量。**

### 使用反引号 **``** 作为字符串的分隔符

### ${存储变量或者表达式}

变量：![](https://gitee.com/jerry798/xcximg/raw/master/img/16dd18e0-7f94-11ee-b32b-a1aa6ea31392.jpeg)

表达式![](https://gitee.com/jerry798/xcximg/raw/master/img/2287b330-7f94-11ee-b32b-a1aa6ea31392.jpeg)

![](https://gitee.com/jerry798/xcximg/raw/master/img/ad931910-7f94-11ee-b32b-a1aa6ea31392.jpeg)

调用函数 function: ${name()}

### constructor 属性

constructor 属性返回所有 JavaScript 变量的构造函数。

```javascript
"John".constructor                 // 返回函数 String()  { [native code] }
(3.14).constructor                 // 返回函数 Number()  { [native code] }
false.constructor                  // 返回函数 Boolean() { [native code] }
```

## null 与 undefined 的异同点

**共同点**：都是原始类型，保存在栈中变量本地。

**不同点**：

（1）undefined——表示变量声明过但并未赋过值。

它是所有未赋值变量默认值，例如：

```javascript
var a;    // a 自动被赋值为 undefined
```

（2）null——表示一个变量将来可能指向一个对象。

一般用于主动释放指向对象的引用，例如：

```javascript
var emps = ['ss','nn'];
emps = null;     // 释放指向数组的引用
```

## JS 访问对象方法（对象里的函数）

## JS 事件触发

## JS 类

类是用于创建对象的模板。

```javascript
class ClassName { 
    constructor() { 
        ... 
    } 
}
```

```javascript
let site = new ClassName("菜鸟教程", "https://www.runoob.com");
```

![](https://gitee.com/jerry798/xcximg/raw/master/img/6c0a3400-879c-11ee-bfb6-29337c594ac4_20231120200038.jpeg)

new 根据类创造新的对象

类继承 extend 出子类，super 父类的属性

## 原型链

所有的 JavaScript 对象都会从一个 prototype（**原型对象**）中继承属性和方法。

所有 JavaScript 中的对象都是位于原型链顶端的 Object 的**实例**。

![](https://gitee.com/jerry798/xcximg/raw/master/img/1565fb70-87a6-11ee-bfb6-29337c594ac4_20231120210947.jpeg)

## DOM

DOM（Document Object [Model](https://so.csdn.net/so/search?q=Model&spm=1001.2101.3001.7020)）即文档对象模型，是 W3C 制定的标准接口规范，是一种处理 HTML 和 XML 文件的标准 API(应用程序接口)。DOM 提供了对整个文档的访问模型，将文档作为一个树形结构，树的每个结点表示了一个 HTML 标签或标签内的文本项。DOM 树结构精确地描述了 HTML 文档中标签间的相互关联性。将 HTML 或 XML 文档转化为 DOM 树的过程称为解析(parse)。HTML 文档被解析后，转化为 DOM 树，因此对 HTML 文档的处理可以通过对 DOM 树的操作实现。DOM 模型不仅描述了文档的结构，还定义了结点对象的行为，利用对象的方法和属性，可以方便地访问、修改、添加和删除 DOM 树的结点和内容。

- 元素（element）：文档中的都有标签都是元素，元素可以看成是对象
- 节点（node）：文档中都有的内容都是节点：标签，属性，文本
- 文档（document）：一个页面就是一个文档
- 这三者的关系是：文档包含节点，节点包含元素
- 文档（页面）中有一个根（root），这个根标签包含 head 标签与 body 标签，head 标签中又包含 meta 与 title 标签，body 标签中包含 div、p、header、main 等等标签，其中 main 下面又有 article、aside 等等标签，article 标签中又有其它的标签等等，这就组成了树状结构图，也叫 DOM 树。
- 您会经常看到 **document.getElementById("id")**。

这个方法是 HTML DOM 中定义的

### 改变 HTML 内容

```javascript
document.getElementById(id).innerHTML = 新的 HTML;
```

### 改变 HTML 属性

```javascript
document.getElementById(id).attribute = 新属性值;
```

![](https://gitee.com/jerry798/xcximg/raw/master/img/4f029220-838d-11ee-8ba1-c17bd710ad78_20231115160223.jpeg)

### 改变 HTML 样式

```javascript
document.getElementById(id).style.property = 新样式;
```

示例：`document.getElementById("p2").style.color = "blue";`

## 拓展

### snippets 脚本

通过 **typeof()** 来获取 JavaScript 中变量的数据类型./** **typeof **不能用来判断是 Array 还是 Object ****/

```javascript
if (Array.isArray(cars)) {
    document.write("该对象是一个数组。");
}
```

```javascript
if (cars instanceof Array) {
    document.write("该对象是一个数组。");
}
```

使用 isArray 和 instanceof 操作符判断是否是数组

```javascript
console.log(""); // 用于控制台输出
```

### toFixed() 方法

将一个浮点数转换为指定小数位数的字符串

浏览器中的控制台是开发者工具的一部分，可以用来调试 JavaScript 代码、查看网络请求、查看页面元素等。

堆是一种常用的树形结构，是一种特殊的完全二叉树，当且仅当满足所有节点的值总是不大于或不小于其父节点的值的完全二叉树被称之为堆（父节点统一最大或者最小）。插入和删除要改变节点的位置

## 栈与堆

### 基本类型的变量是存放在栈内存（Stack）里的

```javascript
var a, b;
a = "zyj";
b = a;
console.log(a);   // zyj
console.log(b);   // zyj
a = "呵呵";       // 改变 a 的值，并不影响 b 的值
console.log(a);   // 呵呵
console.log(b);   // zyj
```

图解如下：栈内存中包括了变量的标识符和变量的值。

![](https://www.runoob.com/wp-content/uploads/2019/05/3834493100-57c3ff4a5dac7_articlex.png)

### 引用类型的值是保存在堆内存（Heap）中的对象（Object）

```javascript
var a = {name:"percy"};
var b;
b = a;
a.name = "zyj";
console.log(b.name);    // zyj
b.age = 22;
console.log(a.age);     // 22
var c = {
    name: "zyj",
    age: 22
};
```

图解如下：

- 栈内存中保存了**变量标识符**和指向堆内存中该对象的**指针**
- 堆内存中保存了对象的内容

![](https://www.runoob.com/wp-content/uploads/2019/05/3309698956-57c41a89cddc7_articlex.png)

## js 实例

![](https://gitee.com/jerry798/xcximg/raw/master/img/bee6cf50-84f7-11ee-ac40-7f71f2a5eb40_20231117111647.jpeg)

![](https://gitee.com/jerry798/xcximg/raw/master/img/d028fe00-84f7-11ee-ac40-7f71f2a5eb40_20231117111717.jpeg)

## BOM

### window.history 对象

包含浏览器的历史

```javascript
history.back()    // 与在浏览器点击后退按钮相同
history.forward() // 与在浏览器中点击向前按钮相同
```

### window.location 对象

用于获得当前页面的地址 (URL)，并把浏览器重定向到新的页面。

```javascript
location.hostname   // 返回 web 主机的域名
location.pathname   // 返回当前页面的路径和文件名
location.port       // 返回 web 主机的端口 （80 或 443）
location.protocol   // 返回所使用的 web 协议（http: 或 https:）
location.assign()   // 方法加载新的文档
```

### window navigator 对象

![](https://gitee.com/jerry798/xcximg/raw/master/img/8c8600b0-e1b0-11ee-b5a4-e12bedf642ca.jpeg)

### javascript弹窗

可以在 JavaScript 中创建三种消息框：警告框、确认框、提示框。

```javascript
alert()     // 警告框
confirm()   // 确认框
prompt()    // 提示框（可输入）
```

![](https://gitee.com/jerry798/xcximg/raw/master/img/8788d030-e1b3-11ee-b5a4-e12bedf642ca.jpeg)

弹窗使用 反斜杠 + "n"(\n) 来设置换行。

实例: `alert("Hello\nHow are you?");`

## JavaScript Cookie

Cookie 用于存储 web 页面的用户信息。

使用 document.cookie 控制 cookie 的创建读取更改删除

```javascript
var x = document.cookie = "username=huang; ID=123465";
console.log(x); // 创建读取
```

更改 document.cookie 覆盖

您只需要设置 expires 参数为以前的时间即可，如下所示，设置为 Thu, 01 Jan 1970 00:00:00 GMT:

```javascript
document.cookie = "username=; expires=Thu, 01 Jan 1970 00:00:00 GMT"; // 删除GMT国际时间标准
```

### 有关时间

```javascript
var d = new Date();
d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
// settime()设置时间对象的时间，exdays为几天后过期，算毫秒数+1970年到现在的毫秒数都=1970到结束的毫秒数
var expires = "expires=" + d.toGMTString();
```

### 获取指定cookie的脚本

```javascript
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i].trim();
        if (c.indexOf(name) == 0) { // 检查当前 cookie 字符串是否以 `name`（即 `cname + "="`）开始，indexof(寻找的东西)未找到则返回 `-1，找到返回0`
            return c.substring(name.length, c.length); // name.length即`cname + "="` 的长度只取值
            // `substring()` 是 JavaScript 中字符串（`String`）对象的一个方法，用于提取字符串中介于两个指定下标之间的字符。
        }
    }
    return "";
}
```

## CSS 布局与背景

### 标准文档流
标准文档流是指在网页设计中，元素按照默认的布局和排列方式自动流动的过程。在网页中，默认情况下，元素会从上到下按照其在HTML文档中的顺序依次排列，不需要进行特殊的定位或布局设置。

### 定位属性
- `position: relative;` - 元素相对于其正常位置进行定位
- `position: absolute;` - 元素相对于最近的已经定位的祖先元素进行定位

### Flexbox 布局属性
- `flex-wrap: wrap;` - 规定 flex 项目将在必要时进行换行，否则会弹性压缩在一行
- `justify-content: space-around;` - 间距相同，均匀分布的属性
- `justify-content: space-between;` - 首个弹性项目紧贴容器
- `align-items` - 属性用于垂直对齐 flex 项目
- `align-content` - 属性用于对齐弹性线

### background-size 属性
`background-size` 是一个CSS属性，用于控制背景图像的尺寸大小。

该属性可以接受多个参数，最常用的取值包括：

- **auto** - 背景图像的原始尺寸
- **cover** - 保持背景图像的纵横比，使其完全覆盖容器，并可能超出容器的边界
- **contain** - 保持背景图像的纵横比，使其完全适应容器，并且图像的边缘可能会被容器的边界裁剪

此外，还可以使用具体的长度或百分比值来调整背景图像的大小：
```css
background-size: 100px 200px;  /* 宽度100像素，高度200像素 */
background-size: 50% auto;     /* 宽度50%，高度自动 */
```

### 注意事项
1. `background-size` 属性只对使用 `background-image` 设置的背景图像生效，不适用于 `<img>` 等元素的图片
2. 设置 `flex` 属性需要该元素是弹性项目，也就是父元素要设置为 `display: flex` 或 `display: inline-flex`
