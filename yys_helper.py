# -*- coding: utf-8 -*-
import numpy as np
import win32gui, win32con, win32api, win32ui
import time, random, sys
from collections import defaultdict
from ctypes import windll
from PIL import Image
from tqdm import tqdm

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
        print("运行次数：", end="")
        # Initialize progressing bar with the total running times
        self.pbar = tqdm(total=int(input()), ascii=True)
        self.pbar_time = 0

    def __del__(self):
        self.pbar.close()
        # Remove DCs
        win32gui.DeleteObject(self.saveBitMap.GetHandle())
        self.saveDC.DeleteDC()
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)

    def read_file(self, config_file):
        configs = {}
        with open(config_file, 'rb') as fp:
            lines = fp.readlines()
        for line in lines:
            try:
                line = line.strip().split()
                # Comments start with #
                if line[0][0] == '#':
                    continue
                # configs = {xy : {rgb : [n, config1, config2, ...]}}
                xy = tuple([int(i) for i in line[:2]])
                rgb = tuple([int(i) for i in line[2:5]])
                if xy not in configs:
                    configs[xy] = {}
                if rgb not in configs[xy]:
                    # The first element in the list is the current position
                    configs[xy][rgb] = [1]
                # Read configuration from the line
                config = {
                    'x_range': [int(line[5]), int(line[6])],
                    'y_range': [int(line[7]), int(line[8])],
                    'sleep_time': float(line[9]),
                    'battle_count': int(line[10]),
                    # 'verbose': True if len(line) > 10 else False
                }
                configs[xy][rgb].append(config)
            except:
                # If the format is not fit
                continue
        return configs

    # Generate random point of next click and sleeping time
    def rand_point(self, screen):
        # Assign properties
        height, width, _ = screen.shape
        x, y, n = None, None, len(self.configs)
        sleep_time, battle_count = 1.5, 0
        # Everytime  we have 1 / counter chance to pick the new random, point.
        # Thus, the probability of taking one point among all possible points
        # are equal (1 / n).
        # if random.random() < 1.0 / counter:
        # Now we use a rr algorithm instead of probability.
        for xy in self.configs:
            rgb = tuple(screen[xy[1]][xy[0]])
            # Print out the pixel if verbose is true
            # Here we assume three rgb value is (-1, -1, -1)
            if (-1, -1, -1) in self.configs[xy]:
                print(rgb)
            # If the key rgb is in configs[xy], we will iteratively find
            # the config in the list. Thus, the pixel with same coordinate
            # and same rgb value will have equal chance to choose different
            # random area.
            if rgb in self.configs[xy]:
                pos = self.configs[xy][rgb][0]
                x = random.randint(*self.configs[xy][rgb][pos]['x_range'])
                y = random.randint(*self.configs[xy][rgb][pos]['y_range'])
                sleep_time = self.configs[xy][rgb][pos][
                        'sleep_time'] + random.random() * 0.5
                # Count the number of battles. End of battle should be 1.
                # Fail of a battle should have count 0.
                battle_count = self.configs[xy][rgb][pos]['battle_count']
                # Update the current position to the next config
                self.configs[xy][rgb][0] = pos % (len(
                        self.configs[xy][rgb]) - 1) + 1

        return x, y, sleep_time, battle_count

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
        x, y, sleep_time, battle_count = self.rand_point(screen)
        if x != None:
            l_param = win32api.MAKELONG(x, y)
            win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0, l_param)
            #win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
            #        win32con.MK_LBUTTON, l_param)
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 0, l_param)
            time.sleep(0.01 + random.random() * 0.02)
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, l_param)
            sys.stdout.flush()
        # Sleep for random time
        time.sleep(sleep_time)
        # tqdm update cannot take negative input in windows
        # Every two update cannot be within 10s (to detect end of battle)
        if battle_count > 0 and time.time() - self.pbar_time > 10:
            self.pbar.update(battle_count)
            self.pbar_time = time.time()

    def run(self):
        # Run the main function
        #while time.time() < self.end_time:
        while self.pbar.n < self.pbar.total:
            self.screenshot()

if __name__ == '__main__':
    helper = YYS_Helper()
    helper.run()
