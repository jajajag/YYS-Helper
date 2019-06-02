# -*- coding: utf-8 -*-
import numpy as np
import win32gui, win32con, win32api, win32ui
import time, random
from ctypes import windll
from PIL import Image

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

def main():
    # Define name for the window
    class_name = "Win32Window0"
    title_name = "阴阳师-网易游戏"
    # Find the hwnd of the window
    hwnd = win32gui.FindWindow(class_name, title_name)
    # Get the input for total running time
    print("运行时间：", end="")
    total_time = int(input())
    start_time = time.time()
    
    # Run the main function
    while time.time() - start_time < total_time:
        # Set the program to forground
        #win32gui.SetForegroundWindow(hwnd)
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        # Calculat the size of the window
        width = right - left
        height = bottom - top

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
        
        # Search white pixels
        #for i in range(470):
        #    for j in range(850):
        #        #if screen[i][j][0] == 255 and screen[i][j][1] == 255 and screen[i][j][2] == 255:
        #        #if screen[i][j][0] == 0 and screen[i][j][1] == 0 and screen[i][j][2] == 0:
        #        if screen[i][j][0] == 150 and screen[i][j][1] == 141 and screen[i][j][2] == 131:
        #            print(i, j)

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
        l_param = win32api.MAKELONG(x, y)
        win32api.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, l_param)
        #win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, l_param)
        time.sleep(0.03 + random.random() * 0.02)
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, l_param)
        # Sleep for random time
        time.sleep(1.5 + random.random() * 0.8)

if __name__ == '__main__':
    main()
