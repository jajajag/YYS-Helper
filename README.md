# YYS-Helper
基于桌面版和pywin32的阴阳师辅助程序(自用，仅提供思路)。

# 前言
肝痒痒鼠这个游戏已经900多天了，六星也有将近80个了，每次活动基本都能前百，但满速招财还是一个都没有，不得不说是一种遗憾。之前写过一个按键精灵的脚本，自己用被鬼使黑疯狂发信，朋友用刷的招财都270还是没什么问题，尴尬。手动肝了很久魂土，感觉还是写一个脚本来节省时间比较好，不然一边肝一边看书实在是容易分心。

这次决定重新用python来实现一遍御魂的挂机，有人猜测wy检查的手段主要是两种：

* 检查后台软件。
* 检查重复点击。

因此，猜想如果用python实现脚本，应该不容易被封。这里主要是发现的比较有意思的用法，分享一下。如果复用代码的话，还是有很多地方要改的。

# 思路

这个脚本的思路就是简单的判断+点击，基于pywin32模块。首先，我通过查找类名获得桌面版的句柄，使用句柄从而可以后台运行，比较方便。然后通过句柄进行截图。使用winapi进行截图的话，效率是非常高的，大概是30ms左右。再通过判断图片某处像素的RGB来检查时候战斗已经结束，或者是在组队开始界面。最后随机出有效的点击位置，通过向句柄发送点击的消息来完成点击，并随机等待一段时间。

# 实现

```
# Define name for the window
class_name = "Win32Window0"
title_name = "阴阳师-网易游戏"
# Find the hwnd of the window
hwnd = win32gui.FindWindow(class_name, title_name)
```
首先，通过名称来获得窗口的句柄。类名等可以通过[WinSpy](http://www.catch22.net/software/winspy)来获取。之后的内容都在while循环中，重复执行：

```
left, top, right, bottom = win32gui.GetClientRect(hwnd)
# Calculat the size of the window
width = right - left
height = bottom - top
```
首先，通过句柄来获得Client的宽度等，注意Client忽略了上方的控制栏。





