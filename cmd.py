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
import ssh
import thread
import threading
import time
import data_struct as ds
import numpy as np
import Test.range_num_gen as rng
import os

DEC          = 1  # 采样率分频系数
TITLE        = "WaveForm"
SCAN_NUM     = 8192

class Cmd():
    def __init__(self):
        # 用于控制线程的停止
        self.thread_kill = False
        # 用于线程间的锁定
        self.lock        = threading.Lock()
    
    # 锁定线程锁thread_kill，线程可终止状态
    def __lock_thread_kill__(self):
        with self.lock:
            self.thread_kill = True
    # 解锁线程锁thread_kill，线程可运行状态
    def __unlock_thread_kill__(self):
        with self.lock:
            self.thread_kill = False
    # 获取线程锁thread_kill的值
    def __get_thread_kill__(self):
        with self.lock:
            return self.thread_kill

    # 连接按钮的回调函数
    def connect(self, win, ip):
        try:
            if win.bnt_en.connect:
                ssh.SSH(win, ip)
                win.runtime_msg    = f"Connected to {ip}"
                win.bnt_en.connect = False
                win.bnt_en.close   = True
                win.bnt_en.start   = True
                win.info.ip        = ip
            else:
                pass
        except Exception as e:
            win.runtime_msg        = f"Connection failed: {e}"
    
    # 启动按钮的回调函数
    def start(self, win, ch):
        try:
            if win.bnt_en.start:
                self.__unlock_thread_kill__()
                digit = ch[-1]
                str = f"acquire -{digit} hv -o 8192 {DEC}"
                win.rate.dec = DEC
                win.rate.interval      = 1 / win.rate.max * win.rate.dec
                win.info.state         = ds.State.run.value
                win.runtime_msg        = f"running cmd \"{str}\""
                win.bnt_en.start       = False
                win.bnt_en.stop        = True
                if win.acquire_thread is None:
                    win.acquire_thread = thread.daemon(self.__always__acquire__, win, str)
                if win.disp_thread is None:
                    win.disp_thread    = thread.daemon(self.__auto_refresh_wave__, win)
        except Exception as e:
            win.runtime_msg = f"Start failed: {e}"
    
    # 停止按钮的回调函数
    def run_stop(self, win):
        try:
            if win.bnt_en.stop:
                if win.info.state == ds.State.run.value:
                    win.runtime_msg = "Stop acquiring data now!!!"
                    win.info.state  = ds.State.stop.value
                else:
                    win.runtime_msg = "Continue acquiring data now!!!"
                    win.info.state  = ds.State.run.value
        except Exception as e:
            win.runtime_msg         = f"Stop failed: {e}"
            raise e

    # 关闭连接的回调函数
    def close(self, win):
        try:
            if win.bnt_en.close:
                # 关闭SSH连接
                win.ssh.client.close()
                # 清空信息
                win.runtime_msg    = "Connection closed"
                win.bnt_en.close   = False
                win.bnt_en.start   = False
                win.bnt_en.stop    = False
                win.bnt_en.connect = True
                win.info = ds.Info("-", ds.Channel.channel1.value, "-", "-", "-", -1)
                # 清空绘图
                win.ax.cla()
                win.canvas.draw()
                # 关闭线程
                win.info.state     = ds.State.stop.value
                self.__lock_thread_kill__()
                win.acquire_thread = None
                win.disp_thread    = None
        except Exception as e:
            win.runtime_msg = f"Close failed: {e}"
            raise e
        
    # divy_plus按钮的回调函数
    def divy_plus(self, win):
        if win.info.divy + 0.1 < 5:
            win.info.divy += 0.1
        else:
            win.info.divy = 5

    # divy_sub按钮的回调函数
    def divy_sub(self, win):
        if win.info.divy - 0.1 > 0:
            win.info.divy -= 0.1
        else:
            win.info.divy = 0.1

    # divx_plus按钮的回调函数
    def divx_plus(self, win):
        if win.sample_num.num * 2 < win.sample_num.max:
            win.sample_num.num *= 2
        else:
            win.sample_num.num = win.sample_num.max
    
    # divx_sub按钮的回调函数
    def divx_sub(self, win):
        if win.sample_num.num // 2 > win.sample_num.min:
            win.sample_num.num //= 2
        else:
            win.sample_num.num = win.sample_num.min
    
    # 保存按钮的回调函数
    def save(self, win):
        try:
            if win.info.state == ds.State.stop.value:
                # 获取当前时间作为文件名的一部分
                import datetime
                timestamp       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # 确保 img 文件夹存在
                img_folder      = "img"
                if not os.path.exists(img_folder):
                    os.makedirs(img_folder)
                
                # 保存绘图为图片
                filename_img    = os.path.join(img_folder, f"plot_{timestamp}.png")
                win.figure.savefig(filename_img)
                
                # 保存当前显示的数据为 CSV 文件
                filename_data   = os.path.join(img_folder, f"data_{timestamp}.csv")
                y_data          = win.ax.lines[0].get_ydata()
                np.savetxt(filename_data, y_data, delimiter=",")
                
                # 保存当前绘图到 img 文件夹下
                win.runtime_msg = f"Image saved as {filename_img}, Data saved as {filename_data}"
        except Exception as e:
            win.runtime_msg     = f"Save failed: {e}"

    # 用于一直显示字符串的线程
    def __always_refresh_info__(self, win):
        try:
            while True:
                info_str = ds.InfoStr(
                    win.info.ip,
                    win.info.ch,
                    win.info.max,
                    win.info.min,
                    win.info.avg,
                    win.info.freq,
                    win.info.divy,
                    win.info.state
                )
                win.info_box.configure(state="normal")
                win.info_box.delete(1.0, "end")
                win.info_box.insert("end", info_str)
                win.info_box.configure(state="disabled")
                win.info_frame.update_idletasks()
                time.sleep(0.5)
        except Exception as e:
            win.runtime_msg = f"Error during info refresh: {e}"
            raise e

    # 用于不间断的采集数据
    def __always__acquire__(self, win, cmd):
        try:
            while True:
                if win.info.state == ds.State.stop.value:
                    time.sleep(0.5)
                    continue
                elif self.__get_thread_kill__():
                    win.runtime_msg    = "acquire thread killed"
                    break
                else:
                    output  = win.ssh.tx_cmd(cmd, win)
                    if output:
                        for val in output.splitlines():
                            win.data.put(val)
                    else:
                        win.runtime_msg = "No data received"
                    time.sleep(0.1)
        except Exception as e:
            win.runtime_msg = f"Acquire failed: {e}"
            raise e

    # 设置刷新runtime_box的线程
    def __auto_refresh_runtime_box__(self, win):
        try:
            while True:
                win.runtime_box.configure(state="normal")
                win.runtime_box.delete(1.0, "end")
                win.runtime_box.insert("end", win.runtime_msg)
                win.runtime_box.configure(state="disabled")
                win.runtime_box.update_idletasks()
                time.sleep(0.5)
        except Exception as e:
            win.runtime_msg = f"Error during runtime refresh: {e}"
            raise e
        
    # 创建用于刷新波形数据的线程
    def __auto_refresh_wave__(self, win):
        try:
            sample_num = win.sample_num.num
            x_data     = np.arange(0, sample_num)
            y_data     = np.zeros(sample_num)
            
            # 初始化绘图
            line       = win.ax.plot(x_data, y_data, color="blue")
            win.canvas.draw()

            while True:
                if win.info.state == ds.State.stop.value:
                    time.sleep(0.5)
                    continue

                if self.__get_thread_kill__():
                    win.runtime_msg = "disp thread killed"
                    break
                
                # 检查 sample_num 是否发生变化
                if sample_num != win.sample_num.num:
                    new_sample_num = win.sample_num.num
                    if new_sample_num > sample_num:
                         # 扩展 y_data，使用已有数据循环填充
                        if len(y_data) > 0:
                            # 计算需要填充的长度
                            extra_length = new_sample_num - sample_num
                            # 使用已有数据的最后部分进行循环填充
                            repeat_data  = np.tile(y_data[-sample_num:],
                                (extra_length // sample_num) + 1)
                            y_data = np.concatenate((y_data,
                                repeat_data[:extra_length]))
                        else:
                            # 如果没有已有数据，用 0 填充
                            y_data       = np.zeros(new_sample_num)
                    else:
                        # 裁剪 y_data
                        y_data = y_data[-new_sample_num:]
                    sample_num = new_sample_num
                    x_data     = np.arange(0, sample_num)
                    line.set_xdata(x_data)
                    win.ax.set_xlim(0, sample_num)

                half_sample_num = sample_num // 2
                new_data        = []
                while len(new_data) < half_sample_num:
                    if not win.data.empty():
                        new_data.append(float(win.data.get()))
                    else:
                        # 数据不足时等待
                        time.sleep(0.2)

                # 计算最值、显示区间的范围
                avg = np.mean(new_data)
                win.info.avg = avg
                win.info.max = max(new_data)
                win.info.min = min(new_data)
                mid          = (win.info.max + win.info.min) / 2
                span         = win.info.max - mid

                # 计算频率
                self.__calculate_freq__(win, new_data)

                # 更新 y轴数据 左移并填充新数据
                y_data = np.roll(y_data, -half_sample_num)
                y_data[-half_sample_num:] = new_data

                # 更新绘图
                line.set_ydata(y_data)
                if win.info.divy == -1 or win.info.divy < span:
                    win.info.divy = span
                elif win.info.divy - span > 0.3:
                    win.info.divy = span + 0.1
                win.ax.set_ylim(avg - win.info.divy, avg + win.info.divy)
                win.ax.set_title(TITLE)
                win.ax.set_ylabel("Voltage (V)")
                win.ax.set_xlabel("Sample Points")
                win.canvas.draw()
                time.sleep(0.1)

        except Exception as e:
            win.runtime_msg = f"Wave refresh failed: {e}"
            raise e

    # 计算频率
    def __calculate_freq__(self, win, data):
        try:
            # 使用快速傅里叶变换 (FFT) 计算频率
            fft_result      = np.fft.fft(data)
            # 取幅值
            fft_magnitude   = np.abs(fft_result)
            # 取一半频谱（对称性）
            fft_magnitude   = fft_magnitude[:len(fft_magnitude) // 2]

            # 计算频率对应的索引
            sample_rate     = 1 / win.rate.interval
            freqs           = np.fft.fftfreq(len(data), d=win.rate.interval)
            freqs           = freqs[:len(freqs) // 2]

            # 找到最大幅值对应的频率
            peak_index      = np.argmax(fft_magnitude)
            peak_freq       = freqs[peak_index]

            # 更新频率信息
            win.info.freq   = peak_freq
        except Exception as e:
            win.runtime_msg = f"Frequency calculation failed: {e}"
            raise e