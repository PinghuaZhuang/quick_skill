import json
import keyboard
import random
import time
import os
import re
from pynput import mouse
from ctypes import windll
mouseController = mouse.Controller()
user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
# TODO: 后面加一个自动识别游戏窗口的功能，避免在外面误触

class QuickCastManager:
    def __init__(self):
        self.settings = self.load_settings()
        self.quick_casts = self.load_quick_casts()
        self.save_settings()
        self.save_quick_casts()
        self.select_cast = None
        self.mouse_combo = {}
        self.lock = False
        mouse_listener = mouse.Listener(on_click=self.on_click)
        # 启动监听器
        mouse_listener.start()

    # 鼠标按键监听
    def on_click(self, x,y, button, pressed):
        """
        程序启动时就会启动鼠标监听，开始流程后，遍历所有方案，将鼠标相关注册到此处。
        请注意除了输入处都是以汉字存储对应功能的。
        """
        if not pressed:
            return
        # print(self.mouse_combo)
        if button == mouse.Button.x1:
            if 'x1' not in self.mouse_combo:
                return
            self.run_combo(self.mouse_combo['x1'])
        elif button == mouse.Button.x2:
            if 'x2' not in self.mouse_combo:
                return
            self.run_combo(self.mouse_combo['x2'])
        elif button == mouse.Button.left:
            if 'MLeft' not  in self.mouse_combo:
                return
            self.run_combo(self.mouse_combo['MLeft'])
        elif button == mouse.Button.right:
            if 'MRight' not in self.mouse_combo:
                return
            self.run_combo(self.mouse_combo['MRight'])

    def load_settings(self):
        try:
            with open("setting.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"key_up_interval": 0.01, "key_interval": 0.08}

    def load_quick_casts(self):
        try:
            with open("quick.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_quick_casts(self):
        with open("quick.json", "w+") as file:
            json.dump(self.quick_casts, file, indent=2)

    def save_settings(self):
        with open("setting.json", "w+") as file:
            json.dump(self.settings, file, indent=2)

    def change_settings(self, key_interval, key_up_interval):
        self.settings["key_interval"] = key_interval
        self.settings["key_up_interval"] = key_up_interval
        self.save_settings()

    def create_new_cast(self, name, combos):
        self.quick_casts[name] = combos
        self.save_quick_casts()

    def delete_cast(self, name):
        if name not in self.quick_casts:
            return False
        del self.quick_casts[name]
        self.save_quick_casts()
        return True

    def delete_combo_from_cast(self, cast_name,trigger_key):
        if cast_name not in self.quick_casts:
            return False
        find = False
        for combo in self.quick_casts[cast_name]:
            if combo["trigger_key"] == trigger_key:
                self.quick_casts[cast_name].remove(combo)
                find = True
                break
        self.save_quick_casts()
        return find

    def add_combo_to_cast(self, cast_name,trigger_key,sequence, hotkey=False):
        if cast_name in self.quick_casts:
            # 如果存在就覆盖
            find = False
            for combo in self.quick_casts[cast_name]:
                if combo["trigger_key"] == trigger_key:
                    combo["sequence"] = sequence
                    find = True
                    break
            if not find:
                self.quick_casts[cast_name].append({"trigger_key": trigger_key, "sequence": sequence})
        else:
            return
        if hotkey:
            if trigger_key in ["x1","x2","MLeft","MRight"]:
                self.mouse_combo[trigger_key] = {"trigger_key": trigger_key, "sequence": sequence}
            else:
                keyboard.add_hotkey("alt+" + trigger_key, self.run_combo, args=({"trigger_key": trigger_key, "sequence": sequence},))
        self.save_quick_casts()

    def run_listener(self,cast_name):
        # 选择方案
        if cast_name not in self.quick_casts:
            return False
        self.select_cast = cast_name
        for combo in self.quick_casts[cast_name]:
            if combo["trigger_key"] in ["x1","x2","MLeft","MRight"]:
                self.mouse_combo[combo["trigger_key"]] = combo
            else:
                keyboard.add_hotkey(combo["trigger_key"], self.run_combo, args=(combo,))

                keyboard.add_hotkey("a+" + combo["trigger_key"], self.run_combo, args=(combo,))
                keyboard.add_hotkey("s+" + combo["trigger_key"], self.run_combo, args=(combo,))
                keyboard.add_hotkey("d+" + combo["trigger_key"], self.run_combo, args=(combo,))
                keyboard.add_hotkey("w+" + combo["trigger_key"], self.run_combo, args=(combo,))

                keyboard.add_hotkey("a+w+" + combo["trigger_key"], self.run_combo, args=(combo,))
                keyboard.add_hotkey("a+s+" + combo["trigger_key"], self.run_combo, args=(combo,))
                keyboard.add_hotkey("d+w+" + combo["trigger_key"], self.run_combo, args=(combo,))
                keyboard.add_hotkey("d+s+" + combo["trigger_key"], self.run_combo, args=(combo,))
        self.cast_name = cast_name
        return True

    def stop_listener(self):
        self.mouse_combo = {}
        try:
            keyboard.unhook_all_hotkeys()
        except Exception as e:
            find = False
            for combo in self.quick_casts[self.cast_name]:
                if combo["trigger_key"] not in ["x1","x2","MLeft","MRight"]:
                    find = True
                    break
            if find:
                return False
        return True


    def run_combo(self, combo):
        if self.lock:
            return
        self.lock = True
        # self.time_step = 0
        # self.timestamp = time.time()
        # 如果当前存在alt按键被按下，等待按键释放
        while keyboard.is_pressed('alt'):
            time.sleep(0.01)
        # for key in combo['sequence']:
        #     keyboard.press(key)
        #     delay = self.settings["key_interval"] * random.uniform(0.66, 1.33)
        #     time.sleep(delay)
        #     keyboard.release(key)
        #     delay = self.settings["key_up_interval"] * random.uniform(0.66, 1.33)
        #     time.sleep(delay)
        timeline_now = 0
        keys = []
        for key in combo['sequence']:
            if key[0] == "`":
                delay = float(0)
                # 为了提高准确度并且操作更加自然，随机延迟设定如下
                delay += random.uniform(0.95, 1.051) * 0.001 * int(key[1:])
                timeline_now += delay
                continue
            if len(key) >= 3 and (key[:2] == "lp" or key[:2] == "rp" or key[:2] == "x1"  or key[:2] == "x2"):
                delay = float(0)
                delay += random.uniform(0.99, 1.01) * 0.001 * int(key[2:])
                if key[0] == "l":
                    keys.append(("MLeft",True,timeline_now))
                    keys.append(("MLeft",False,timeline_now+delay))
                if key[0] == "r":
                    keys.append(("MRight",True,timeline_now))
                    keys.append(("MRight",False,timeline_now+delay))
                if key[:2] == "x1":
                    keys.append(("x1",True,timeline_now))
                    keys.append(("x1",False,timeline_now+delay))
                if key[:2] == "x2":
                    keys.append(("x2",True,timeline_now))
                    keys.append(("x2",False,timeline_now+delay))
                timeline_now += delay
                continue
            real_key = key
            if key == "上":
                real_key = "up"
            elif key == "下":
                real_key = "down"
            elif key == "左":
                real_key = "left"
            elif key == "右":
                real_key = "right"

            # print("key:", real_key)

            # 添加长按机制
            # 直接修改 quuick.json 文件, 检测用户输入的代码不太好, v1.31没改
            # space: u:200 i
            long_press_time = int(0)
            if (":" in real_key):
                tmp = real_key.split(":")
                combo["long_press_trigger"] = tmp[0]
                if (tmp[1] == ""):
                    tmp[1] = 0
                    combo["long_press"] = "infinity"
                else:
                    combo["long_press_time"] = long_press_time

                real_key = tmp[0]
                long_press_time = random.uniform(0.95, 1.051) * 0.001 * int(tmp[1])

            keys.append((real_key,True,timeline_now))
            delay = self.settings["key_up_interval"] * random.uniform(0.952, 1.05)
            timeline_now += long_press_time
            keys.append((real_key,False, timeline_now+delay))
            timeline_now += self.settings["key_interval"] * random.uniform(0.82, 1.19)

        keys.sort(key=lambda x: x[2])
        for i,key in enumerate(keys):
            if i != 0:
                time.sleep(key[2]-keys[i-1][2])
            if key[0] == "MLeft":
                if key[1]:
                    mouseController.press(mouse.Button.left)
                else:
                    mouseController.release(mouse.Button.left)
                continue
            elif key[0] == "MRight":
                if key[1]:
                    mouseController.press(mouse.Button.right)
                else:
                    mouseController.release(mouse.Button.right)
                continue
            elif key[0] == "x1":
                if key[1]:
                    mouseController.press(mouse.Button.x1)
                else:
                    mouseController.release(mouse.Button.x1)
                continue
            elif key[0] == "x2":
                if key[1]:
                    mouseController.press(mouse.Button.x2)
                else:
                    mouseController.release(mouse.Button.x2)
                continue
            # timestamp = time.time()
            # self.time_step = timestamp - self.timestamp
            # self.timestamp = timestamp
            # print(key[0]+" time_step", self.time_step)
            if key[1]:
                keyboard.press(key[0])
                while keyboard.is_pressed(combo["trigger_key"]) and combo["long_press"] == "infinity" and combo["long_press_trigger"] == key[0]:
                    time.sleep(0.01)
            else:
                keyboard.release(key[0])
        self.lock = False
