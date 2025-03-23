# YYS-Helper
基于桌面版和pywin32的阴阳师辅助程序(自用，仅分享思路)。

# 前言
小纸人不太够用啊。。有时肝完纸人后，可以再挂一段时间的御魂也比较安逸。三周年了，魂土也正式进入20s时代，代码更新到最新。

这次加入了一些新的features，包括：
* 将代码重构成进一个类
* 使用配置文件config.txt代替代码中的hard-coding坐标
* 将RGB的config设为(-1, -1, -1)来打印相应坐标的RGB值(用于配置config)
* 加入进度条显示
* 将时间限制改为战斗次数限制
* 对同个坐标，依次执行而非只执行第一条config

通过这些改变，我们可以实现一些功能：
* 可自定义每个status的等待时间
* 通过设结算界面战斗次数为1来设定战斗次数限制
* 加入单人战斗(业原火/御魂/御灵)的支持
* 拒绝协作
* 砸百鬼(不智能)
* 更新对新版组队界面的支持
* 更新对某些活动(比如日轮之城爬塔)的支持

2024.12.24 更新：
* 多于一个参数（argv）时，保存截图为screenshot.bmp
* 截图方法改为PrintWindow

2025.03.22 更新：
* config增加一列scope，当scope为1时，同一个pixel有多个匹配时顺序执行
* 例如斗技中将开自动后再绿标右一，scope为0时为随机选择一个点击

注：我使用的客户端分辨率非默认值，config.txt需进行调整，不在此进行提供！

# 展示
在这里展示几张用来判定和点击的效果，大部分自动操作都可以通过配置config.txt来完成。首先是新版的组队界面，判定挑战按钮从灰色变成黄色后，点击挑战附近区域开始战斗。此策略只适用于双人车，三人车可以判定最右边的人物框内的颜色变化。

![image1](https://github.com/jajajag/YYS-Helper/blob/master/results/screen_shot_2.jpg)

当战斗结束时，这里判断的是寮金币加成的颜色。判定成功后，点击区域包括左上中三个区域。每次战斗结束时，依次选择不同区域进行点击。

![image2](https://github.com/jajajag/YYS-Helper/blob/master/results/screen_shot_3.jpg)

单人战斗时，判断框上部叹号区域(同理也可以判断框的颜色，右上角X的颜色等)。点击区域为挑战按钮内部。

![image3](https://github.com/jajajag/YYS-Helper/blob/master/results/screen_shot_5.jpg)

由于业原火我是用大蛇1拖4带狗粮，有概率翻车。战斗失败时，判断白色字体颜色，点击3个区域来跳过失败界面。

![image4](https://github.com/jajajag/YYS-Helper/blob/master/results/screen_shot_7.jpg)

接下来是在百鬼夜行的应用。在选择鬼王阶段，首先判断上方挂饰颜色，点击下方三个区域选择鬼王。之后点击开始按钮进入百鬼夜行。

![image5](https://github.com/jajajag/YYS-Helper/blob/master/results/screen_shot_6.jpg)

百鬼过程中，判断上方吊坠(不被冰冻影响颜色)，点击下方随机区域。可以全区域随机，可以点击左/中/上+上/中/下进行定制组合。

![image6](https://github.com/jajajag/YYS-Helper/blob/master/results/screen_shot_4.jpg)

最后是在本次三周年活动的应用。可以判断上方叹号的颜色，按照箭头方向依次点击进入格子。顺时针旋转可以保证最下一行全部被打开，之后依次从下向上进行点击，可以遍历所有格子。点击进入格子后，依次开始战斗/结束战斗/重新选格子。在本层通关后，可以依次进入下一层/选择御魂/确定进入。该脚本本质是一个有限状态机，因此可以适用于大部分活动中。

![image7](https://github.com/jajajag/YYS-Helper/blob/master/results/screen_shot_1.jpg)


# 思路

下两个部分想起来的时候再更新。

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
在这段代码中，我们先获得这个窗口的DC，然后创建一个BitMap来存储截图。这里参考了[Python Screenshot of inactive window PrintWindow + win32gui](https://stackoverflow.com/questions/19695214/python-screenshot-of-inactive-window-printwindow-win32gui)和[Python实现屏幕截图的两种方式](https://www.cnblogs.com/weiyinfu/p/8051280.html)。使用winapi截图的好处是，可以进行后台截图(但不能最小化)。之后将BitMap转化成ndarray，从而方便后面进行像素判断。释放资源。

```
 # Search white pixels
#for i in range(470):
#    for j in range(850):
#        #if screen[i][j][0] == 255 and screen[i][j][1] == 255 and screen[i][j][2] == 255:
#        #if screen[i][j][0] == 0 and screen[i][j][1] == 0 and screen[i][j][2] == 0:
#        if screen[i][j][0] == screen[400][487][0] \
#                and screen[i][j][1] == screen[400][487][1] \
#                and screen[i][j][2] == screen[400][487][2]:
#            print(i, j)
```
这段注释掉的部分，遍历所有的pixels，判断纯黑，纯白和某些特殊的颜色。比如，结算界面的buff中间有纯白，组队时中间有红色(87, 68, 46)自动开始字样。从而我们可以提取具体像素点，来判断御魂进行到哪一步。

```
# Click if the pixel is white
if screen[468][148][0] == 255 and screen[468][148][1] == 255 and screen[468][148][2] == 255:
    x, y = rand_next(width, height)
# Click the start button if in party
elif screen[400][487][0] == 87 and screen[400][487][1] == 68 and screen[400][487][2] == 46:
    x, y = rand_start(width, height)
else:
    # Sleep for random time
    time.sleep(1.5 + random.random() * 0.8)
    continue
```
这段判断具体像素点，如果是纯白，说明在结算界面；如果是(87, 68, 46)，说明在组队界面，分别点击可选的范围。否则，在战斗过程中，跳过。

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

# 后记

这里仅仅是分享一下自用的脚本。后面如果可以找到做放大镜和御魂导出的dalao是打开桌面版数据的方法，想做一下战斗AI的强化学习方面改进。
