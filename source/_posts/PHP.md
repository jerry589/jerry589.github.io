---
title: PHP代码片段
date: 2023-12-04
tags: [PHP, 代码片段]
---

<html> 
<body> 
<?php
	$z=7;
	$y=3;
$a=<<<EOF
</br>6</br>
EOF;//EOF内部可以解析html格式的内容
define("changliang","123456");//name value
	function quanju()
	{
		global $y,$z,$a;//函数内调用全局变量的声明
		echo $y+$z;
		print $a;
		var_dump($y);//输出类型
		echo changliang;//常量在php中哪里都可以使用
	}
	/*echo - 可以输出一个或多个字符串
	print - 只允许输出一个字符串，返回值总为 1*/
	quanju();
$cars=array("Peter","Ben","Joe");//数组对象
echo "I like ".$cars[0]. ",".$cars[1].",".$cars[2].".";
	//并置运算符 (.) 用于把两个字符串值连接起来。
echo "<br>";
	echo $x;
	$length=count($cars);//count函数计算数组长度
	echo $length;
	echo "<br>";
	for($p=0;$p<$length;$p++)
	{
		echo $cars[$p];
		echo "<br>";
	}
	echo "<br>";
	$age=array("Peter"=>"35","Ben"=>"37","Joe"=>"43");
	//关联数组，给数组元素赋值
	echo "Peter is " . $age['Peter'] . " years old.";
	echo "<br>";
	foreach($age as $x=>$x_value)
	{
	echo "Key=" . $x . ", Value=" . $x_value;
    echo "<br>";
	}
	//遍历关联数组
	sort($cars);
	print_r($cars);
	function one()
	{
		echo "this is one()<br/>";
	}
	function two()
	{
		echo "this is two()<br/>";
	}
	$func = 'one';//变量函数，使用变量作为函数名，任意调用不同函数
	$func();
	$func="two";
	$func();
	?>
</body> 
</html>
