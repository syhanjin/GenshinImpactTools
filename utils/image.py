from PyQt5.QtGui import QImage
import cv2
import numpy as np


def QImageToCvMat(img):
    ptr = img.constBits()
    ptr.setsize(img.byteCount())
    mat = np.array(ptr).reshape(img.height(), img.width(), 4)
    return mat


def mask_circle_transparent(img, r):
    """
    图片截取为环形
    """
    # cv2.IMREAD_COLOR，读取BGR通道数值，即彩色通道，该参数为函数默认值
    # cv2.IMREAD_UNCHANGED，读取透明（alpha）通道数值
    # cv2.IMREAD_ANYDEPTH，读取灰色图，返回矩阵是两维的
    rows, cols, channel = img.shape

    # 创建一张4通道的新图片，包含透明通道，初始化是透明的
    img_new = np.zeros((rows, cols, 4), np.uint8)
    img_new[:, :, 0:3] = img[:, :, 0:3]

    # 创建一张单通道的图片，设置最大内接圆为不透明，注意圆心的坐标设置，cols是x坐标，rows是y坐标
    img_circle = np.zeros((rows, cols, 1), np.uint8)
    img_circle[:, :, :] = 0  # 设置为全透明
    # 设置最大内接圆为不透明
    img_circle = cv2.circle(
        img_circle,
        (int(cols/2), int(rows/2)), int(min(rows, cols)/2), (255),
        -1
    )
    # 设置正中心透明（排除自身三角型的影响）
    img_circle = cv2.circle(
        img_circle, (int(cols/2), int(rows/2)), r, (0),
        -1
    )

    # 图片融合
    img_new[:, :, 3] = img_circle[:, :, 0]
    return img_new
