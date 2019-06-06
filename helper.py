# -*- coding: utf-8 -*-
import numpy as np
import win32gui, win32con, win32api, win32ui
import time, random, sys
from ctypes import windll
from PIL import Image

# Generate random point of next click and sleeping time
def rand_point(screen):
    # Assign properties
    height, width, _ = screen.shape
    # If we should reject the collaboraiton
    if (screen[123][473] == [179, 146, 118]).all():
        x = random.randint(512, 534)
        y = random.randint(74, 92)
        # If reject, click the button suddenly
        sleep_time = 0.5
    # If we should end this battle
    elif (screen[468][148] == [255, 255, 255]).all():
        while True:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            # Stat area
            if x < 80 and y < 90:
                continue
            # Dialog area
            elif x > 550 and y < 35:
                continue
            # Equip area
            elif x > 160 and x < 710 and y > 100 and y < 600:
                continue
            # Buff area
            elif x > 90 and y > 424 and y < 457:
                continue
            break
        sleep_time = 1.8 + random.random() * 1.5
    # If we are in party
    elif (screen[400][487] == [87, 68, 46]).all():
        x = random.randint(640, 752)
        y = random.randint(384, 418)
        # If we have just start the battle, don't need to check for 10 seconds
        sleep_time = 10
    # If we want to start a single battle
    elif (screen[83][498] == [57, 42, 30]).all():
        x = random.randint(597, 675)
        y = random.randint(316, 347)
        # If we have just start the battle, don't need to check for 10 seconds
        sleep_time = 10
    # If in other cases
    else:
        x, y = None, None
        sleep_time = 1.5

    return x, y, sleep_time

# Generate random point of starting button
def rand_start(width, height):
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
        #for i in range(10, 470):
        #    for j in range(10, 850):
        #        if screen[i][j][0] == 255 and screen[i][j][1] == 255 and screen[i][j][2] == 255:
        #        if screen[i][j][0] == 0 and screen[i][j][1] == 0 and screen[i][j][2] == 0:
        #        if screen[i][j][0] == screen[400][487][0] \
        #                and screen[i][j][1] == screen[400][487][1] \
        #                and screen[i][j][2] == screen[400][487][2]:
        #            print(i, j)
        #break

        # Generate random point and sleep_time from the screenshot
        x, y, sleep_time = rand_point(screen)
        if x != None:
            l_param = win32api.MAKELONG(x, y)
            win32api.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, l_param)
            #win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
            win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, l_param)
            time.sleep(0.03 + random.random() * 0.02)
            win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, l_param)
            print(".", end="")
            sys.stdout.flush()
        # Sleep for random time
        time.sleep(sleep_time)

if __name__ == '__main__':
    main()
