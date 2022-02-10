from utils import HEADERS, MAP_PATH, window
from utils.image import QImageToCvMat
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import httpx
import os
import json
import numpy as np
import cv2
from queue import Queue
MAP_URL = "https://api-static.mihoyo.com/common/map_user/ys_obc/v1/map/info?map_id=2&app_sn=ys_obc&lang=zh-cn"
STATUS = {1: '正在更新地图'}

class Genshin:
    def __init__(self) -> None:
        self.window_name = '原神'
        if window.FindWindow(self.window_name) is None:
            raise RuntimeError('Genshin is not run.')
        desktop = QApplication.desktop()
        self.size = (desktop.width(), desktop.height())
        self.img = QImage()
        self.status = 0

    def progress(self):
        if window.GetForegroundWindowName() != '原神':
            return False
        self.img = QImageToCvMat(window.grab(text=self.window_name))
        return True

    def update_map(self, *args):
        self.status = 1
        r = httpx.get(MAP_URL, headers=HEADERS)
        data = r.json()['data']
        detail = json.loads(data['info']['detail'])
        all = None
        for i in range(len(detail['slices'][0])):
            r = httpx.get(detail['slices'][0][i]['url'], headers=HEADERS)
            fn = os.path.join(MAP_PATH, f'{i}.png')
            with open(fn, 'wb') as f:
                for data in r.iter_bytes():
                    f.write(data)
            if all is None:
                all = cv2.imdecode(np.fromfile(fn, dtype=np.uint8), -1)
            else:
                all = np.concatenate(
                    [all, cv2.imdecode(np.fromfile(fn, dtype=np.uint8), -1)], axis=1
                )
        A = np.full(all.shape[:2], 255, dtype="uint8")
        all = cv2.merge([all, A])
        print(all.shape)
        cv2.imwrite(os.path.join(MAP_PATH, 'all.png'), all)
        self.map = all
        self.status = 0

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]
