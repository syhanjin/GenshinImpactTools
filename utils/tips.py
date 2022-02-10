from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Tip:
    def __init__(
        self,
        root: QMainWindow,
        text: str,
        x: int, y: int,
        width: int,
        font,
        frame: int,
    ) -> None:
        self.label = QLabel(root)
        if font is not None:
            self.label.setFont(font)
        self.label.setStyleSheet("color: rgba(0, 0, 0, 255); font-size: 16px;")
        self.label.setText(text)
        self.x = x
        self.y = y
        self.width = width
        self.label.setGeometry(QRect(x, y, width, 25))
        self.frame = frame
        self.max_frame = frame
        self.alpha = 255

    def progress(self):
        self.alpha -= int(self.alpha / self.frame)
        self.y -= int(1 / max(self.max_frame - self.frame, 1) + 0.5)
        self.frame -= 1
        if self.frame == 0:
            self.label.clear()
            return True
        self.label.setGeometry(QRect(self.x, self.y, self.width, 20))
        self.label.setStyleSheet(f"color: rgba(0, 0, 0, {self.alpha}); font-size: 16px;")
        return False


class Tips:
    tips: 'list[Tip]' = []

    def __init__(
        self,
        root: QMainWindow,
        font: QFont,
        pos: 'tuple[int, int]',
        size: 'tuple[int, int]'
    ) -> None:
        self.root = root
        self.font = font
        self.bottom = 100
        self.pos = pos
        self.size = size

    def tip(self, text: str) -> None:
        self.tips.append(Tip(
            self.root, text, self.pos[0],
            self.pos[1] + self.size[1] - self.bottom,
            self.size[0],
            self.font, 72
        ))
        self.bottom -= 25

    def progress(self):
        for i in self.tips:
            if i.progress():
                self.tips.remove(i)
        if len(self.tips) == 0:
            self.bottom = 100
        else:
            self.bottom = self.tips[-1].y - 25
