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

class Cmd():
    def __init__(self):
        self.thread_kill = False     # 用于控制线程的停止
        self.lock = threading.Lock()  # 用于线程间的锁定
    
    # 锁定线程锁thread_kill，线程可运行态
    def __lock_thread_kill__(self):
        with self.lock:
            self.thread_kill = True
    # 解锁线程锁thread_kill，线程终止态
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
                win.runtime_msg = f"Connected to {ip}"
                win.bnt_en.connect = False
                win.bnt_en.close = True
                win.bnt_en.start = True
                win.info.ip = ip
            else:
                pass
        except Exception as e:
            win.runtime_msg = f"Connection failed: {e}"
    
    # 启动按钮的回调函数
    def start(self, win, ch):
        try:
            if win.bnt_en.start:
                digit = ch[-1]
                str = f"acquire -{digit} hv -o 4096 {DEC}"
                win.rate.dec = DEC
                win.rate.interval = 1 / win.rate.max * win.rate.dec
                win.info.state = ds.State.run.value
                win.runtime_msg = f"running cmd \"{str}\""
                win.acquire_thread = thread.daemon(self.__always__acquire__, win, str)
                win.disp_thread = thread.daemon(self.__auto_refresh_wave__, win)
                win.bnt_en.start = False
                win.bnt_en.stop = True
        except Exception as e:
            win.runtime_msg = f"Start failed: {e}"
    
    # 停止按钮的回调函数
    def run_stop(self, win):
        try:
            if win.bnt_en.stop:
                win.runtime_msg = "Stop acquiring data now!!!"
                win.info.state = ds.State.stop.value
            else:
                win.runtime_msg = "Continue acquiring data now!!!"
                win.info.state = ds.State.run.value
        except Exception as e:
            win.runtime_msg = f"Stop failed: {e}"
            raise e

    # 关闭连接的回调函数
    def close(self, win):
        try:
            if win.bnt_en.close:
                # 关闭SSH连接
                win.ssh.client.close()
                win.runtime_msg = "Connection closed"
                win.but_en = ds.BntEnable()
                # 关闭线程
                win.info.state = ds.State.stop.value
                self.__unlock_thread_kill__()
        except Exception as e:
            win.runtime_msg = f"Close failed: {e}"
            raise e
        
    # divy_plus按钮的回调函数
    def divy_plus(self, win):
        if win.info.divy + 0.2 < 10:
            win.info.divy += 0.2
        else:
            win.info.divy = 10

    # divy_sub按钮的回调函数
    def divy_sub(self, win):
        if win.info.divy - 0.2 > 0:
            win.info.divy -= 0.2
        else:
            win.info.divy = 0.2

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
            # 获取当前时间作为文件名的一部分
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 确保 img 文件夹存在
            img_folder = "img"
            if not os.path.exists(img_folder):
                os.makedirs(img_folder)
            
            # 构造文件路径
            filename = os.path.join(img_folder, f"plot_{timestamp}.png")
            
            # 保存当前绘图到 img 文件夹下
            win.figure.savefig(filename)
            win.runtime_msg = f"Image saved as {filename}"
        except Exception as e:
            win.runtime_msg = f"Save failed: {e}"

    # 用于一直显示字符串的线程
    def __always_refresh_info__(self, win):
        try:
            while True:
                info_str = ds.InfoStr(
                    win.info.ip,
                    win.info.ch,
                    win.info.max,
                    win.info.min,
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
                    continue
                elif self.__get_thread_kill__():
                    win.runtime_msg = "acquire thread killed"
                    break
                else:
                    output =  win.ssh.tx_cmd(cmd)
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
            x_data = np.arange(0, sample_num)
            y_data = np.zeros(sample_num)
            
            # 初始化绘图
            line, = win.ax.plot(x_data, y_data, color="blue")
            win.canvas.draw()

            while True:
                if win.info.state == ds.State.stop.value:
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
                            repeat_data = np.tile(y_data[-sample_num:],
                                (extra_length // sample_num) + 1)
                            y_data = np.concatenate((y_data,
                                repeat_data[:extra_length]))
                        else:
                            # 如果没有已有数据，用 0 填充
                            y_data = np.zeros(new_sample_num)
                    else:
                        # 裁剪 y_data
                        y_data = y_data[-new_sample_num:]
                    sample_num = new_sample_num
                    x_data = np.arange(0, sample_num)
                    line.set_xdata(x_data)
                    win.ax.set_xlim(0, sample_num)

                half_sample_num = sample_num // 2
                new_data = []
                while len(new_data) < half_sample_num:
                    if not win.data.empty():
                        new_data.append(float(win.data.get()))
                    else:
                        # 数据不足时等待
                        time.sleep(0.5)

                # 计算最值、显示区间的范围
                win.info.max = max(new_data)
                win.info.min = min(new_data)
                avg  = (win.info.max + win.info.min) / 2
                span = win.info.max - avg

                # 计算频率
                self.__calculate_freq__(win, new_data)

                # 更新 y轴数据 左移并填充新数据
                y_data = np.roll(y_data, -half_sample_num)
                y_data[-half_sample_num:] = new_data

                # 更新绘图
                line.set_ydata(y_data)
                div = max(abs(np.min(y_data)), abs(np.max(y_data)))*1.5
                if wn.info.divy == -1 or win.info.divy < span:
                    win.info.divy = div
                win.ax.set_ylim(avg - win.info.divy, avg + win.info.divy)
                win.ax.set_title(TITLE)
                win.ax.set_ylabel("Voltage (V)")
                win.ax.set_xlabel("Sample Points")
                win.canvas.draw()
                time.sleep(0.5)

        except Exception as e:
            win.runtime_msg = f"Wave refresh failed: {e}"
            raise e

    # 计算频率
    def __calculate_freq__(self, win, data):
        try:
            # 使用快速傅里叶变换 (FFT) 计算频率
            fft_result = np.fft.fft(data)
            # 取幅值
            fft_magnitude = np.abs(fft_result)
            # 取一半频谱（对称性）
            fft_magnitude = fft_magnitude[:len(fft_magnitude) // 2]

            # 计算频率对应的索引
            sample_rate = 1 / win.rate.interval
            freqs = np.fft.fftfreq(len(data), d=win.rate.interval)
            freqs = freqs[:len(freqs) // 2]

            # 找到最大幅值对应的频率
            peak_index = np.argmax(fft_magnitude)
            peak_freq = freqs[peak_index]

            # 更新频率信息
            win.info.freq = peak_freq
        except Exception as e:
            win.runtime_msg = f"Frequency calculation failed: {e}"
            raise e