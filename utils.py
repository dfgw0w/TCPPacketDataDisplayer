from ctypes import windll
from pynput import mouse, keyboard
import packetParser

user32 = windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
screensize = 1280, 720
print(screensize)

debug_name = ""
debug_data = ""

def debug(key):
    try:
        if key.char == "u":
            print("[" + debug_name + "] Debug: " + str(debug_data))
    except AttributeError:
        print("", end="")


keyboard_listener = keyboard.Listener(on_press=debug)
keyboard_listener.start()