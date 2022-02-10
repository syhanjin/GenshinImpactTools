from PyQt5.QtWidgets import QApplication
import win32gui
import win32con


def grab(hwnd=None, text: str = None):
    if hwnd is not None:
        screen = QApplication.primaryScreen()
        return screen.grabWindow(hwnd).toImage()
    elif text is not None:
        screen = QApplication.primaryScreen()
        hwnd = win32gui.FindWindow(None, text)
        return screen.grabWindow(hwnd).toImage()
    else:
        return None


def FindWindow(name):
    return win32gui.FindWindow(None, name)


def GetForegroundWindowName():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)


def GetForegroundWindow():
    return win32gui.GetForegroundWindow()


def GetWindowRect(hwnd=None, text: str = None):
    if hwnd is not None:
        return win32gui.GetWindowRect(hwnd)
    elif text is not None:
        hwnd = win32gui.FindWindow(None, text)
        return win32gui.GetWindowRect(hwnd)
    else:
        return None
