---
title: Java编程基础学习笔记
tags: [Java, 编程基础, 面向对象, 异常处理, 集合框架, GUI编程]
date: 2024-03-11
---

# Java编程基础学习笔记

本文整理了Java编程的核心概念和基础知识，涵盖了从环境配置到高级特性的全面内容。

<!-- more -->

## 1. Java环境配置

### 系统变量与环境变量
- **系统变量**：用作文件路径快捷键的标识符
- **环境变量**：用来找可执行文件路径，可以用标识符快捷表示

### Java程序执行流程
1. Java源代码(.java) → javac编译器 → 字节码文件(.class)
2. 字节码文件 → JVM(Java虚拟机) → 各平台运行
3. 实现"一次编写，到处运行"的跨平台特性

### 核心工具
- **编译器**：javac.exe
- **解释器**：java.exe执行字节码文件
- **JAR文件**：类似zip，将class文件打包
  - 包含META-INF/MANIFEST.MF文件作为"详情单"
  - 可执行JAR包通过`java -jar`命令运行

## 2. Java基础语法

### 位运算符
- **按位或运算符（|）**：两个数中任一为1，结果为1
- **异或运算符（^）**：两个相应位不同时结果为1，相同时为0
  - 例：2 ^ 4 = 6（00000010 ^ 00000100 = 00000110）

### 常用包
| 包名 | 简介 |
|------|------|
| `java.lang` | 基础类，如String、Math、System等 |
| `java.io` | 输入输出功能，文件读写和网络通信 |
| `java.net` | 网络编程相关类，如URL、Socket |
| `java.nio` | 高效的I/O操作方法 |
| `java.sql` | JDBC数据库连接功能 |
| `java.awt` | 图形用户界面（GUI）功能 |
| `java.swing` | 基于awt的扩展GUI组件 |
| `java.security` | 安全性和加密功能 |
| `java.time` | 日期和时间处理（Java 8+） |

## 3. 异常处理

### 健壮性（Robust）
指系统能够良好处理异常、错误或意外情况的能力。

### 异常层次结构
```
Throwable
├── Error（系统错误，无法捕获）
└── Exception（一般异常）
    ├── RuntimeException（运行异常，非检查异常）
    └── IOException（编译异常，检查异常）
```

### 异常类型
- **RuntimeException**：运行时异常，编译时不强制处理
  - 如：NullPointerException、ArrayIndexOutOfBoundsException
- **IOException**：检查异常，编译时强制要求处理
  - 如：文件不存在异常

### 自定义异常
```java
// 检查性异常
class MyException extends Exception { }

// 运行时异常
class MyRuntimeException extends RuntimeException { }
```

## 4. 面向对象编程

### 接口（Interface）
- 完全抽象的结构，只包含未实现的方法声明
- 方法默认是`public abstract`，变量默认是`public static final`
- 一个类可以实现多个接口
- Java 8开始支持默认方法和静态方法

```java
interface Flyable {
    void fly();
}

interface Swimmable {
    void swim();
}

class Duck implements Flyable, Swimmable {
    public void fly() { /* 实现 */ }
    public void swim() { /* 实现 */ }
}
```

### 抽象类（Abstract Class）
- 不能实例化的类，提供概念模板
- 可包含抽象方法和具体方法
- 有抽象方法的类必须声明为抽象类
- 子类必须实现所有抽象方法

### 访问修饰符
- **public**：任何地方都可访问
- **protected**：同包或子类可访问
- **private**：仅本类内部可访问

### 命名规范
1. 项目名：全部小写
2. 包名：全部小写
3. 类名：首字母大写（驼峰命名）
4. 变量名、方法名：首字母小写（驼峰命名）

## 5. 数据类型与包装类

### 基本数据类型与包装类
| 基本类型 | 包装类 |
|----------|--------|
| byte | Byte |
| short | Short |
| int | Integer |
| long | Long |
| float | Float |
| double | Double |
| char | Character |
| boolean | Boolean |

### 装箱与拆箱
- **装箱**：基本类型 → 包装类
- **拆箱**：包装类 → 基本类型
- 用于集合框架和泛型编程

## 6. String类

### 特性
- **不可变性**：一旦创建，长度和内容不能更改
- **String池**：运行时维护字符串缓冲池，避免重复

### 创建方式
```java
String str1 = "123";           // 仅在缓冲池
String str2 = new String("123"); // 缓冲池 + 堆栈区
```

### 比较方法
- `equals()`：比较内容
- `==`：比较内存地址

### 常用方法
- `substring(start)`：从指定位置截取到末尾
- `substring(start, end)`：截取指定范围
- `indexOf(str)`：查找子字符串位置

### StringBuffer vs StringBuilder
- **StringBuffer**：线程安全，内容可变
- **StringBuilder**：非线程安全，性能更好

## 7. 集合框架

### 集合 vs 数组
- **集合**：长度可变，存储多种类型，只能存储对象
- **数组**：长度固定，单一类型，可存储基本类型和对象

### 主要接口
- **List**：有序，允许重复
  - `ArrayList`：动态数组，查询快
  - `LinkedList`：链表，增删快
- **Set**：无序，不允许重复
  - `HashSet`：基于HashMap，无序
  - `TreeSet`：基于二叉树，有序
- **Map**：键值对存储
  - `HashMap`：无序
  - `TreeMap`：有序

### 迭代器（Iterator）
用于遍历集合的对象，提供统一的遍历方式。

## 8. GUI编程

### 包结构
- **java.awt**：抽象窗口工具包，重量级控件，依赖操作系统
- **javax.swing**：基于AWT，轻量级控件，纯Java实现

### GUI设计步骤
1. **创建容器**：载体组件
2. **添加组件**：交互控件
3. **安排组件**：布局管理器
4. **处理事件**：事件监听

### 容器类型
- **顶层容器**：JFrame（窗口）、JDialog（对话框）、JApplet（小程序）
- **中间容器**：JPanel、JToolBar等

### 容器特点
- **JFrame**：可独立存在，有标题栏和边框，默认BorderLayout
- **JPanel**：必须包含在其他容器中，无标题边框，默认FlowLayout

## 9. 常见易错点

1. **文件结构**：一个文件只能有一个public主类
2. **构造方法**：无返回值，类名相同，系统提供默认无参构造
3. **参数传递**：
   - 基本类型：传值
   - 引用类型：传地址
4. **重载vs重写**：
   - 重载：方法名相同，参数不同
   - 重写：子类覆盖父类方法
5. **Scanner使用**：注意清空缓冲区，使用`nextLine()`清除换行符
6. **继承规则**：
   - 父类需要无参构造函数
   - 子类构造函数中使用`super()`调用父类构造
7. **接口实现**：方法默认public，实现类必须实现所有方法
8. **数据类型**：
   - 单引号：字符
   - 双引号：字符串
   - 数组也是对象

## 10. 最佳实践

### 代码规范
- 遵循命名规范
- 合理使用访问修饰符
- 及时关闭资源
- 异常处理要具体

### 性能优化
- 选择合适的集合类型
- 使用StringBuilder处理字符串拼接
- 避免不必要的对象创建

### 设计原则
- 面向接口编程
- 单一职责原则
- 开闭原则
- 依赖倒置原则

## 总结

Java作为面向对象的编程语言，具有"一次编写，到处运行"的特性。掌握其基础语法、面向对象特性、异常处理、集合框架等核心概念，是进行Java开发的基础。通过不断实践和学习，可以逐步提高Java编程能力。