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

御魂战斗我们可以当做有几个阶段：

* 组队界面，需要点击开始才能进行战斗。
* 战斗状态，不需要进行额外的操作。
* 结算界面，需要多次点击才能结束，其中buff图标可以当做是一个标志。

因此，我们可以判断buff颜色和开始按钮的颜色，来进行组队界面和结算界面的跳过。

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
通过句柄来获得Client的宽度等，注意Client忽略了上方的控制栏。

```
# Create DCs
hwndDC = win32gui.GetWindowDC(hwnd)
mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
saveDC = mfcDC.CreateCompatibleDC()
# Create Bit Map
saveBitMap = win32ui.CreateBitmap()
saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
saveDC.SelectObject(saveBitMap)
# Save the screenshot
saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
bmpinfo = saveBitMap.GetInfo()
bmpstr = saveBitMap.GetBitmapBits(True)
# Save to image
im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), 
        bmpstr, 'raw', 'BGRX', 0, 1)
screen = np.array(im)
# Remove DCs
win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hwnd, hwndDC)
```
在这段代码中，我们先获得这个窗口的DC，然后创建一个BitMap来存储截图。这里参考了[Python Screenshot of inactive window PrintWindow + win32gui](https://stackoverflow.com/questions/19695214/python-screenshot-of-inactive-window-printwindow-win32gui)和[Python实现屏幕截图的两种方式](https://www.cnblogs.com/weiyinfu/p/8051280.html)。使用winapi截图的好处是，可以进行后台截图。之后将BitMap转化成ndarray，从而方便后面进行像素判断。释放资源。

```
# Search white pixels
#for i in range(470):
#    for j in range(850):
#        #if screen[i][j][0] == 255 and screen[i][j][1] == 255 and screen[i][j][2] == 255:
#        #if screen[i][j][0] == 0 and screen[i][j][1] == 0 and screen[i][j][2] == 0:
#        if screen[i][j][0] == 150 and screen[i][j][1] == 141 and screen[i][j][2] == 131:
#            print(i, j)
```
这段注释掉的部分，遍历所有的pixels，判断纯黑，纯白和某些特殊的颜色。比如，结算界面的buff中间有纯白，组队按钮中间有纯色(150, 141, 131)。从而我们可以提取具体像素点，来判断御魂进行到哪一步。

```
# Click if the pixel is white
if screen[468][148][0] == 255 and screen[468][148][1] == 255 and screen[468][148][2] == 255:
    x, y = rand_next(width, height)
# Click the start button if in party
elif screen[395][600][0] == 150 and screen[395][600][1] == 141 and screen[395][600][2] == 131:
    x, y = rand_start(width, height)
else:
    # Sleep for random time
    time.sleep(1.5 + random.random() * 0.8)
    continue
```
这段判断具体像素点，如果是纯白，说明在结算界面；如果是(150, 141, 131)，说明在组队界面，分别点击可选的范围。否则，在战斗过程中，跳过。

```
# Generate random point of next click
def rand_next(width, height):
    while True:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if x < 80 and y < 90:
            continue
        elif x > 550 and y < 35:
            continue
        elif x > 160 and x < 710 and y > 100 and y < 600:
            continue
        elif x > 90 and y > 427 and y < 457:
            continue
        return x, y

# Generate random point of starting button
def rand_start(width, height):
    x = random.randint(640, 752)
    y = random.randint(384, 418)
    return x, y
```
额外写了两个函数来进行简单的坐标计算，组队界面需要点击的是开始战斗Button，结算界面要点击除了buff，御魂，聊天栏和战斗数据的其他位置。这里简单的对不符合要求的坐标进行重新随机。

```
l_param = win32api.MAKELONG(x, y)
win32api.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, l_param)
#win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, l_param)
time.sleep(0.03 + random.random() * 0.02)
win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, l_param)
# Sleep for random time
time.sleep(1.5 + random.random() * 0.8)
```
对句柄调用SendMessage，将鼠标移动到指定坐标，点击，随机设定延迟后释放。最后，设定随机延迟，来进行下一次点击。
