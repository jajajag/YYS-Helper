# -*- coding: utf-8 -*-
import numpy as np
import win32gui, win32con, win32api, win32ui
import time, random, sys
from ctypes import windll
from PIL import Image

class YYS_Helper(object):
    def __init__(self,
            config_file='config.txt',
            class_name="Win32Window0",
            title_name="阴阳师-网易游戏"):
        # Find the hwnd of the window
        self.hwnd = win32gui.FindWindow(class_name, title_name)
        # Set the program to forground
        #win32gui.SetForegroundWindow(hwnd)
        left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
        # Calculat the size of the window
        self.width = right - left
        self.height = bottom - top
        # Create DCs
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC  = win32ui.CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        # Create Bit Map
        self.saveBitMap = win32ui.CreateBitmap()
        self.saveBitMap.CreateCompatibleBitmap(self.mfcDC, self.width,
                self.height)
        self.saveDC.SelectObject(self.saveBitMap)

        # Initialize configuration for target pixel and clicking area
        self.configs = self.read_file(config_file)
        # Get the input for total running time
        print("运行时间：", end="")
        self.end_time = time.time() + float(input())
        # Current position of the configuration
        self.pos = -1

    def __del__(self):
        # Remove DCs
        win32gui.DeleteObject(self.saveBitMap.GetHandle())
        self.saveDC.DeleteDC()
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)

    def read_file(self, config_file):
        configs = []
        with open(config_file, 'rb') as fp:
            lines = fp.readlines()
        for line in lines:
            try:
                line = line.strip().split()
                # Comments start with #
                if line[0][0] == '#':
                    continue
                # Read configuration from the line
                config = {
                    'x': int(line[0]),
                    'y': int(line[1]),
                    'rgb': [int(line[2]), int(line[3]), int(line[4])],
                    'x_range': [int(line[5]), int(line[6])],
                    'y_range': [int(line[7]), int(line[8])],
                    'sleep_time': float(line[9]),
                    'verbose': True if len(line) > 10 else False
                }
            except:
                # If the format is not fit
                continue
            configs.append(config)
        return configs

    # Generate random point of next click and sleeping time
    def rand_point(self, screen):
        # Assign properties
        height, width, _ = screen.shape
        x, y, n = None, None, len(self.configs)
        sleep_time = 1.5
        # Everytime  we have 1 / counter chance to pick the new random, point.
        # Thus, the probability of taking one point among all possible points
        # are equal (1 / n).
        # if random.random() < 1.0 / counter:
        # Now we use a rr algorithm instead of probability.
        for pos in range(n):
            pos = (pos + self.pos) % n
            # Print out the pixel if verbose is true
            if self.configs[pos]['verbose']:
                print(screen[self.configs[pos]['y']][self.configs[pos]['x']])
            # If we find the screen_shot satisfies the criterion
            if (screen[self.configs[pos]['y']][
                self.configs[pos]['x']] == self.configs[pos]['rgb']).all():
                x = random.randint(*self.configs[pos]['x_range'])
                y = random.randint(*self.configs[pos]['y_range'])
                sleep_time = self.configs[0]['sleep_time'] + random.random()
                # Update the current position to the next config
                self.pos = (pos + 1) % n
                break

        return x, y, sleep_time

    def screenshot(self):
        # Save the screenshot
        self.saveDC.BitBlt((0, 0), (self.width, self.height), self.mfcDC,
                (0, 0), win32con.SRCCOPY)
        bmpinfo = self.saveBitMap.GetInfo()
        bmpstr = self.saveBitMap.GetBitmapBits(True)
        # Save to image
        im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
        screen = np.array(im)
        
        # Generate random point and sleep_time from the screenshot
        x, y, sleep_time = self.rand_point(screen)
        if x != None:
            l_param = win32api.MAKELONG(x, y)
            win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0, l_param)
            #win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
            #        win32con.MK_LBUTTON, l_param)
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 0, l_param)
            time.sleep(0.03 + random.random() * 0.02)
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, l_param)
            print(".", end="")
            sys.stdout.flush()
        # Sleep for random time
        time.sleep(sleep_time)

    def run(self):
        # Run the main function
        while time.time() < self.end_time:
            self.screenshot()

if __name__ == '__main__':
    helper = YYS_Helper()
    helper.run()
