import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

import numpy as np
from utils import MAP_PATH, image, window
from utils.genshin import STATUS, Genshin
from queue import Queue

from utils.tips import Tips
import datetime
import cv2
import aircv
import _thread


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("mainWindow")  # 设置窗口名
        self.genshin = Genshin()
        # 引入字体
        self.font = QFont()
        self.font.setFamily("霞鹜文楷")
        self.font.setPointSize(14)
        self.font.setKerning(True)

        # 初始化变量
        self.tips = Tips(
            self, self.font,
            (3, int(self.genshin.size[1] * 0.7)),
            (int(self.genshin.size[0] * 0.2), int(self.genshin.size[1] * 0.2))
        )
        self.state_label = self.label('', (
            3, self.genshin.size[1] - 24,
            int(self.genshin.size[0] * 0.2), 18
        ))
        self.last = datetime.datetime.now()
        #

        self.setGeometry(QRect(0, 0, *self.genshin.size))
        # self.resize(800, 600)  # 重置大小

        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.FramelessWindowHint | Qt.SplashScreen | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("#MainWindow{background-color: transparent}")
        self.setWindowOpacity(0.7)

        self.setContent()
        self.init()

    def init(self):

        # _thread.start_new_thread(self.genshin.update_map, (None, ))
        self.map = cv2.imread(os.path.join(MAP_PATH, 'all.png'), cv2.IMREAD_UNCHANGED)
        # print(self.map.shape)
        pass

    def setContent(self):
        self.state_label.setStyleSheet("font-size: 16px;")

        pass

    def timerEvent(self, *args, **kwargs):
        # 处理tips
        self.tips.progress()
        if self.genshin.status != 0:
            self.state_label.setText(STATUS[self.genshin.status])
            return
        # 截屏
        if not self.genshin.progress():
            self.state_label.setText('『原神』窗口不在最顶层')
            return
        now = datetime.datetime.now()
        self.state_label.setText(
            f'屏幕捕获正常({int((now-self.last).total_seconds()*1000)}ms)')
        self.last = datetime.datetime.now()
        # 处理
        minimap = self.genshin.img[
            int(self.genshin.height * 60 / 1080): int(self.genshin.height * 210 / 1080),
            int(self.genshin.width * 95 / 1920): int(self.genshin.width * 245 / 1920)
        ]
        # 
        minimap = image.mask_circle_transparent(minimap, int(minimap.shape[0] * 30 / 170))
        cv2.imwrite('test.png', minimap)
        print(aircv.find_template(self.map, minimap))
        

    def label(
        self,
        text: 'str',
        geometry: 'tuple[int, int, int, int]',
    ):
        """
        构建label控件
        :param text: 标签文本
        :param geometry: x, y, width, height
        """
        label = QLabel(self)
        if hasattr(self, 'font'):
            label.setFont(self.font)
        label.setText(text)
        label.setGeometry(QRect(*geometry))
        return label


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.showFullScreen()
    main.startTimer(int(1000 / 12))
    sys.exit(app.exec_())
