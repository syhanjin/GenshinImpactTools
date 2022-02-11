"""
风物之诗琴
"""

import json
import win32con
import win32api
import re
import pywinio
import time
import atexit
# region 临时 winio键盘操控

# KeyBoard Commands
# Command port
KBC_KEY_CMD = 0x64
# Data port
KBC_KEY_DATA = 0x60

g_winio = None


def get_winio():
    global g_winio

    if g_winio is None:
        g_winio = pywinio.WinIO()

        def __clear_winio():
            global g_winio
            g_winio = None
        atexit.register(__clear_winio)

    return g_winio


def wait_for_buffer_empty():
    '''
    Wait keyboard buffer empty
    '''

    winio = get_winio()

    dwRegVal = 0x02
    while (dwRegVal & 0x02):
        dwRegVal = winio.get_port_byte(KBC_KEY_CMD)


def key_down(scancode):
    winio = get_winio()

    wait_for_buffer_empty()
    winio.set_port_byte(KBC_KEY_CMD, 0xd2)
    wait_for_buffer_empty()
    winio.set_port_byte(KBC_KEY_DATA, scancode)


def key_up(scancode):
    winio = get_winio()

    wait_for_buffer_empty()
    winio.set_port_byte(KBC_KEY_CMD, 0xd2)
    wait_for_buffer_empty()
    winio.set_port_byte(KBC_KEY_DATA, scancode | 0x80)


def key_press(scancode, press_time=0.2):
    key_down(scancode)
    time.sleep(press_time)
    key_up(scancode)
# endregion


SIZE = (1920, 1080)

# 音符数组 do-ti
NOTE2INDEX = {
    'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6,
    '1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6
}
# 原神不接受windows键盘模拟信号，使用winio驱动级模拟
INDEX2CODE = [
    # G
    [0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16],
    # [81, 87, 69, 82, 84, 89, 85],
    # C
    [0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24],
    # [65, 83, 68, 70, 71, 72, 74],
    # F
    [0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x32]
    # [90, 88, 67, 86, 66, 78, 77]
]
CHAR2CODE = {
    'A': 0x1e, 'B': 0x30, 'C': 0x2e, 'D': 0x20, 'E': 0x12, 'F': 0x21,
    'G': 0x22, 'H': 0x23, 'I': 0x17, 'J': 0x24, 'K': 0x25, 'L': 0x26,
    'M': 0x32, 'N': 0x31, 'O': 0x18, 'P': 0x19, 'R': 0x13, 'S': 0x1f,
    'T': 0x14, 'U': 0x16, 'V': 0x2f, 'W': 0x11, 'X': 0x2d, 'Y': 0x15,
    'Z': 0x2c
}

# 字符串书写谱子 唱名或数字
# 音符
#   无前缀 C调
#   前缀
#       ^ 升调
#       _ 降调
#   后缀
#       / 时长减少一半
#       - 时长变为2倍
#       . 时长变为1.5倍

# 音符列表生成
re_notes = re.compile(
    r'(?P<prefix>[\^_])?(?P<mus_alp>[A-G1-7x0])(?P<postfix>[\/\-\.]+)?'
)
re_notes_verification = re.compile(
    r"([\^_]?[A-G1-7x0][\/\-\.]*)+"
)


def make_notes(music: str, speed: int = 76):
    notes = []
    for note in re_notes.finditer(music):
        mus_alp = note.group('mus_alp')
        pitch = 1
        prefix = note.group('prefix')
        if prefix == '^':
            pitch -= 1
        elif prefix == '_':
            pitch += 1
        postfix = note.group('postfix')
        note_time = 60 / speed
        if postfix:
            note_time = note_time \
                / (2**postfix.count('/')) \
                * (2**postfix.count('-')) \
                * (1.5**postfix.count('.'))
        if mus_alp not in ['0', 'x']:
            notes.append((
                INDEX2CODE[pitch][NOTE2INDEX[mus_alp]],
                # (0.24+170/1920*NOTE2INDEX[mus_alp], 0.125*pitch+2/3),
                note_time
            ))
        else:
            notes.append(
                (None, note_time)
            )

    return notes


# 弹奏程序
def play(music: str, pre: float, speed: int = 76):

    notes = make_notes(music, speed)
    time.sleep(pre)
    for note in notes:
        # print(note)
        # win32api.keybd_event(note[0],win32api.MapVirtualKey(note[0],0),0,0)
        # time.sleep(note[1]-0.1)
        # win32api.keybd_event(note[0], win32api.MapVirtualKey(note[0], 0), win32con.KEYEVENTF_KEYUP, 0)
        # windll.user32.SetCursorPos(
        #     int(note[0][0] * SIZE[0]), int(note[0][1] * SIZE[1]))
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        # time.sleep(note[1]-0.1)
        # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        if note[0]:
            key_press(note[0], note[1])
        else:
            time.sleep(note[1])


def play_file(fn: str, pre: int = 2):
    with open(fn, 'r', encoding="utf-8") as f:
        data = json.load(f)
    row_music = data.get('music')
    if not row_music:
        raise ValueError('json文件未包含music项')
    if type(row_music) == list:
        music, tmp, repeat = '', '', 1
        for i in row_music:
            if i.startswith('#'):
                if i.startswith('#repeat'):
                    music += tmp
                    tmp = ''
                    repeat = int(i.split(' ')[1])
                elif i.startswith('#endrepeat'):
                    music += tmp * repeat
                    tmp = ''
                    repeat = 1
                continue
            i = i.replace(' ', '')
            if not re_notes_verification.match(i):
                raise ValueError(f"""
                    音符解析错误
                    --> {i}
                """)
            tmp += i
        music += tmp
    else:
        music = row_music
    speed = data.get('speed') or 76
    play(
        music=music,
        pre=pre,
        speed=speed
    )


if __name__ == '__main__':
    play_file('WildBeesFlying.json')
    # play_file('canon.json')
