"""
风物之诗琴
"""

"""
## 对于音符解析说明
 - 一个音符分为 `3` 部分，前缀 主体 后缀
 - 前缀规定音高，基准为中音 加 `^` 变为高音 加 `_` 变为低音
 - 后缀规定时长，基准为四分音符 
    不同符号对时长影响不同
     - 每个 `/` 将时长 * `0.5`
     - 每个 `.` 将时长 * `1.5`
     - 每个 `-` 将时长 * `2.0`
 - 主体为键盘符号则没有前缀
 - 可以用括号将多个音符包装 表示同时按下，同时按下的音符时长为组内最短音符时长
"""




import pywinio
import re
import time
import atexit
import json
class Winio:
    winio = None
    # Command port
    KBC_KEY_CMD = 0x64
    # Data port
    KBC_KEY_DATA = 0x60

    def __init__(self) -> None:
        self.winio = pywinio.WinIO()

        def __clear_winio():
            self.winio = None
        atexit.register(__clear_winio)

    def wait_for_buffer_empty(self):
        '''
        Wait keyboard buffer empty
        '''

        dwRegVal = 0x02
        while (dwRegVal & 0x02):
            dwRegVal = self.winio.get_port_byte(self.KBC_KEY_CMD)

    def key_down(self, scancode):
        self.wait_for_buffer_empty()
        self.winio.set_port_byte(self.KBC_KEY_CMD, 0xd2)
        self.wait_for_buffer_empty()
        self.winio.set_port_byte(self.KBC_KEY_DATA, scancode)

    def key_up(self, scancode):
        self.wait_for_buffer_empty()
        self.winio.set_port_byte(self.KBC_KEY_CMD, 0xd2)
        self.wait_for_buffer_empty()
        self.winio.set_port_byte(self.KBC_KEY_DATA, scancode | 0x80)

    def key_press(self, scancode, press_time=0.2):
        self.key_down(scancode)
        time.sleep(press_time)
        self.key_up(scancode)


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
    'M': 0x32, 'N': 0x31, 'O': 0x18, 'P': 0x19, 'Q': 0x10, 'R': 0x13,
    'S': 0x1f, 'T': 0x14, 'U': 0x16, 'V': 0x2f, 'W': 0x11, 'X': 0x2d,
    'Y': 0x15, 'Z': 0x2c
}

# 检测括号匹配
MATCH_BRACKETS = re.compile("(\([^\(\)]+\))*")

# 音符，用音名或数字表示，X或0表示空
RE_NODE = re.compile(
    r'(?P<barket>[\(\)])?(?P<prefix>[\^_])?(?P<mus_alp>[A-G1-7X0])(?P<postfix>[\/\-\.]+)?'
)
RE_NODE_VERIFICATION = re.compile(r'(\(?[\^_]?[A-G1-7X0][\/\-\.]*\)?)+')

# 键盘音符，指键盘上的按键，0表示空
RE_KEYBOARDNODE = re.compile(
    r'(?P<barket>[\(\)])?(?P<key>[QWERTYUASDFGHJZXCVBNM0])(?P<postfix>[\/\-\.]+)?'
)
RE_KEYBOARDNODE_VERIFICATION = re.compile(
    r'(\(?[QWERTYUASDFGHJZXCVBNM0][\/\-\.]*\)?)+')


def make_notes(music: str, speed: int = 76, _type: str = 'note') -> list:
    """
    将字符串解析为音符列表
    :param music: 音乐字符串
    :param speed: 每分钟弹奏，以四分音符为标准
    :param type: 解析类型，note: 使用音名或数字; keyboard: 使用键盘符号
    """
    music = music.upper()
    notes = []
    if _type == 'note':
        if not RE_NODE_VERIFICATION.match(music):
            raise ValueError(f"""音符格式错误\n--> {music}""")
        if not MATCH_BRACKETS.match(music):
            raise ValueError(f"""括号不匹配\n--> {music}""")
        isInGroup = False
        group = [[], 0]
        for note in RE_NODE.finditer(music):
            if note.group('barket') == '(':
                isInGroup = True
                group = [[], 0]
            elif note.group('barket') == ')':
                isInGroup = False
                notes.append(group)
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
            if not isInGroup:
                if mus_alp not in ['0', 'X']:
                    notes.append((
                        INDEX2CODE[pitch][NOTE2INDEX[mus_alp]],
                        # (0.24+170/1920*NOTE2INDEX[mus_alp], 0.125*pitch+2/3),
                        note_time
                    ))
                else:
                    notes.append(
                        (None, note_time)
                    )
            else:
                if mus_alp not in ['0', 'X']:
                    group[0].append(INDEX2CODE[pitch][NOTE2INDEX[mus_alp]])
                group[1] = min(group[1], note_time)
    elif _type == 'keyboard':
        if not RE_KEYBOARDNODE_VERIFICATION.match(music):
            raise ValueError(f"""音符格式错误\n--> {music}""")
        if not MATCH_BRACKETS.match(music):
            raise ValueError(f"""括号不匹配\n--> {music}""")

        isInGroup = False
        group = [[], 0]
        for note in RE_KEYBOARDNODE.finditer(music):
            if note.group('barket') == '(':
                isInGroup = True
                group = [[], 0]
            elif note.group('barket') == ')':
                isInGroup = False
                notes.append(group)
            key = note.group('key')
            postfix = note.group('postfix')
            note_time = 60 / speed
            if postfix:
                note_time = note_time \
                    / (2**postfix.count('/')) \
                    * (2**postfix.count('-')) \
                    * (1.5**postfix.count('.'))
            if not isInGroup:
                if key != '0':
                    notes.append((
                        CHAR2CODE[key],
                        # (0.24+170/1920*NOTE2INDEX[mus_alp], 0.125*pitch+2/3),
                        note_time
                    ))
                else:
                    notes.append(
                        (None, note_time)
                    )
            else:
                if key != '0':
                    group[0].append(CHAR2CODE[key])
                group[1] = min(group[1], note_time)
    return notes


def play(music: str, pre: float, speed: int = 76, _type: str = 'note'):
    """
    弹奏
    :param music: 音乐字符串
    :param pre: 准备时间 s
    :param speed: 每分钟弹奏，以四分音符为标准
    :param type: 解析类型，note: 使用音名或数字; keyboard: 使用键盘符号
    """
    print('解析音符')
    notes = make_notes(music.replace(' ', ''), speed, _type)
    _play(notes, pre)


def _play(notes: list, pre: float):
    """
    弹奏
    :param notes: 已经解析的音符
    :param pre: 准备时间 s
    """
    print('获取键盘对象')
    winio = Winio()
    print(f'演奏倒计时 {pre}s')
    time.sleep(pre)
    print('开始演奏')
    start = time.perf_counter()
    for note in notes:
        if note[0] is not None:
            if type(note[0]) == list:
                for code in note[0]:
                    winio.key_down(code)
                time.sleep(note[1])
                for code in note[0]:
                    winio.key_up(code)
            else:
                winio.key_press(note[0], note[1])
        else:
            time.sleep(note[1])
    print('演奏完毕，用时 {:.2f}s '.format(time.perf_counter()-start))


def play_file(fn: str, pre: int = 2):
    with open(fn, 'r', encoding="utf-8") as f:
        data = json.load(f)
    row_music = data.get('music')
    speed = data.get('speed') or 76
    _type = data.get('type') or 'note'
    if not row_music:
        raise ValueError('json文件未包含music项')
    if type(row_music) == list:
        notes, tmp, repeat = [], [], 1
        for i in row_music:
            if i.startswith('#'):
                if i.startswith('#repeat'):
                    notes += tmp
                    tmp = []
                    repeat = int(i.split(' ')[1])
                elif i.startswith('#endrepeat'):
                    notes += tmp * repeat
                    tmp = []
                    repeat = 1
                continue
            i = i.replace(' ', '')
            tmp += make_notes(i, speed, _type)
        notes += tmp
    else:
        notes = make_notes(row_music, speed, _type)
    _play(
        notes=notes,
        pre=pre
    )


if __name__ == '__main__':
    play_file('WildBeesFlying.json', 5)
