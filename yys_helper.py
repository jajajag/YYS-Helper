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
            config_file='configs/config.txt',
            num_runs=100,
            #class_name="Win32Window0",
            # 新引擎中类名为Win32Window
            class_name="Win32Window",
            title_name="阴阳师-网易游戏"):
        # Find the hwnd of the window
        self.hwnd = win32gui.FindWindow(class_name, title_name)
        # Set the program to forground
        #win32gui.SetForegroundWindow(hwnd)
        #left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
        # JAG: 改截整个窗口
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
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
        print("配置文件config_xxx.txt(默认%s，输入xxx)：" % config_file, end="")
        config_file_input = input()
        config_file = "configs/config_" + config_file_input + ".txt" \
                if config_file_input != "" else config_file
        self.configs = self.read_file(config_file)

        # Get the input for total running time
        print("运行次数(默认%d)：" % num_runs, end="")
        num_runs_input = input()
        num_runs = int(num_runs_input) if num_runs_input != "" else num_runs
        # Initialize progressing bar with the total running times
        self.pbar = tqdm(total=num_runs, ascii=True)
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
                    configs[xy][rgb] = []
                # Read configuration from the line
                config = {
                    'x_range': [int(line[5]), int(line[6])],
                    'y_range': [int(line[7]), int(line[8])],
                    'sleep_time': float(line[9]),
                    'battle_count': int(line[10]),
                    'scope': int(line[11]),
                }
                configs[xy][rgb].append(config)
            except:
                # If the format does not match
                continue
        return configs

    # Generate random point of next click and sleeping time
    def rand_points(self, screen):
        # Initialize two lists
        scope_list, rand_list = [], []
        # Iterate through all the target pixels
        for xy in self.configs:
            rgb = tuple(screen[xy[1]][xy[0]])
            # Print out the pixel if the rgb value is (-1, -1, -1)
            if (-1, -1, -1) in self.configs[xy]:
                print(rgb)
            # If the rgb value matches the target pixel
            if rgb in self.configs[xy]:
                for point in self.configs[xy][rgb]:
                    x = random.randint(*point['x_range'])
                    y = random.randint(*point['y_range'])
                    sleep_time = point['sleep_time'] + random.random() * 0.5
                    # Count the number of battles. End of battle should be 1.
                    battle_count = point['battle_count']
                    # Always click the scope pixel
                    # JAG: 方便斗技开自动接绿标
                    if point['scope'] == 1:
                        scope_list.append((x, y, sleep_time, battle_count))
                    # Randomly click one random pixel
                    else:
                        rand_list.append((x, y, sleep_time, battle_count))

        # Randomly click one pixel if no scope pixel is found
        return scope_list + ([random.choice(rand_list)] if rand_list else [])

    def screenshot(self):
        # Save the screenshot
        #self.saveDC.BitBlt((0, 0), (self.width, self.height), self.mfcDC,
        #        (0, 0), win32con.SRCCOPY)
        # BitBlt失效了，改用PrintWindow
        windll.user32.PrintWindow(self.hwnd, self.saveDC.GetSafeHdc(), 0x2)
        # JAG: 如果多于一个参数，保存截图
        if len(sys.argv) > 1:
            self.saveBitMap.SaveBitmapFile(self.saveDC, 'screenshot.bmp')
        bmpinfo = self.saveBitMap.GetInfo()
        bmpstr = self.saveBitMap.GetBitmapBits(True)
        # Save to image
        im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
        screen = np.array(im)
        
        # Generate random points to click
        points = self.rand_points(screen)
        # Click the points
        for point in points:
            x, y, sleep_time, battle_count = point
            if x != None:
                l_param = win32api.MAKELONG(x, y)
                win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, 0,
                                     l_param)
                #win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN,
                #        win32con.MK_LBUTTON, l_param)
                win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, 0,
                                     l_param)
                time.sleep(0.01 + random.random() * 0.02)
                win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0,
                                     l_param)
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
