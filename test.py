from utils import window
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window.grab(hwnd=window.GetForegroundWindow()).save('test.png')
    sys.exit(app.exec_())
