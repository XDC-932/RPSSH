# Copyright (C) 2025 <xdc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
import enum

# 运行状态
class State(enum.Enum):
    run  = "Run"
    stop = "Stop"

# 通道
class Channel(enum.Enum):
    channel1 = "ch1"
    channel2 = "ch2"

# 采集处理后显示的信息
class Info():
    def __init__(self, ip, ch, max, min, freq, divy = -1, state = State.stop.value):
        self.ip    = ip
        self.ch    = ch
        self.max   = max
        self.min   = min
        self.avg   = '-'
        self.freq  = freq
        self.divy  = divy
        self.state = State.stop.value

# 设置按键使能状态，为True时才会执行按钮的回调函数
class BntEnable():
    def __init__(self):
        self.connect = True
        self.start   = False
        self.stop    = False
        self.close   = False

# 格式化Info字符串
def InfoStr(ip, ch, max, min, avg,freq, divy, state):
    return (
        f"DeviceIP  : {ip}\n"
        f"Channel   : {ch}\n"
        f"Max       : {max}(v)\n"
        f"Min       : {min}(v)\n"
        f"AVG       : {avg}(v)\n"
        f"Freq      : {freq}(Hz)\n"
        f"Div       : {divy}(v/div)\n"
        f"Run/Stop  : {state}\n"
    )

# 显示样本数目
class SampleNum():
    def __init__(self, num):
        self.num = num
        self.max = 16384
        self.min = 1024

# 采样率相关设定
class Rate():
    def __init__(self, dec):
        self.max      = 125000000
        self.dec      = dec
        self.interval = 1 / self.max * self.dec