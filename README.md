# RPSSH

## 介绍

​	本仓库的利用python编程语言实现`red pitaya`开发板上位机的开发，主要功能是实现实时检测开发板上的输入电压并且进行显示。主要使用到的是`ssh`功能实现控制`red pitaya os`执行指定的`bash`命令进行数据的采集，在上位机上实现数据的处理和显示。本项目不会再进行更新，因此想实现更加完备的功能可以自己`fork`代码进行修改。本项目在`red pitaya os 1.04.18`上可以正常运行，低于`1.0`版本的`red pitaya os`会出现不适配现象。

## 发布可执行文件

​	欲使发布的二进制文件不包含不必要的库，建议使用虚拟环境进行打包。可以选择使用`pyinstaller`打包为可执行程序。以下是打包程序需要使用的命令。

- exe和需要的库分开打包

```bash
pyinstaller --noconfirm --onedir --windowed --add-data "Location" ./main.py 
```

- 仅仅打包一个exe文件

```bash
pyinstaller --noconfirm --onefile --windowed --add-data "Location" ./main.py 
```

这里的`Location`替换为实际的`customtkinter`的位置,具体可以使用`pip show customtkinter`进行查看。以下是在`windows`中的查找示例输出。对应`Location : xxxxxxxxxxx`处的信息。

```bash
$ pip show customtkinter
Name: customtkinter
Version: 5.2.2
Summary: Create modern looking GUIs with Python
Home-page: https://customtkinter.tomschimansky.com
Author: Tom Schimansky
Author-email:
License: Creative Commons Zero v1.0 Universal
Location: xxxxxxxxxxx
Requires: darkdetect, packaging
Required-by:
```

