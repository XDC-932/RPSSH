import customtkinter as ctk
import data_struct as ds
import cmd
import queue
import paramiko
import thread
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class windows():
    # 初始化cmd
    cmd = cmd.Cmd()

    # 初始化Info
    info = ds.Info("-", ds.Channel.channel1.value, "-", "-", "-", -1)

    # 创建data同于存放ssh接收到的数据
    data = queue.Queue(maxsize=16384)

    # 初始化ssh对象
    ssh = None
    
    # 初始化acquire线程
    acquire_thread = None

    # 初始化disp_thread线程
    disp_thread = None

    # 初始化按钮使能状态
    bnt_en = ds.BntEnable()

    # 初始化运行时消息
    runtime_msg = "The program is running..."

    # 设置一次性显示的数据点的个数
    sample_num = ds.SampleNum(1024)

    # 设置采样率
    rate = ds.Rate(1)
    
    def __init__(self):
        # 初始化配色方案
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # 创建窗口
        self.win = ctk.CTk()
    
        # 初始化软件窗口
        self.__set_window__()

        # 创建收纳base_ctl_frame和info_frame的frame
        self.right_frame = self.__create_frame__(self.win, "right", "y", "ne")

        # 创建基本控件的frame
        self.base_ctl_frame = self.__create_frame__(self.right_frame, "top", "x")

        # 创建信息显示的frame
        self.info_frame = self.__create_frame__(self.right_frame, "top", "x")

        # 创建绘图frame
        self.disp_frame = self.__create_frame__(self.win, "left", "both")

        # 初始化base_ctl_frame的控件
        self.__add_base_ctl_frame__()

        # 初始化info_frame的控件
        self.__init_infor_frame__()

        # 初始化disp_frame的控件
        self.__init__disp_frame__(self.disp_frame)

        # 显示窗口
        self.win.mainloop()


    # 初始化软件的窗口
    def __set_window__(self, title="Upper Computer"):
        # 获取屏幕宽度和高度
        self.screen_width = self.win.winfo_screenwidth()
        self.screen_height = self.win.winfo_screenheight()

        # 设置窗口大小为屏幕的 90% 宽度和高度，并居中显示
        self.window_width  = int(self.screen_width  * 0.9)
        self.window_height = int(self.screen_height * 0.9)
        self.x_position = (self.screen_width - self.window_width) // 2
        self.y_position = (self.screen_height - self.window_height) // 2
        self.win.geometry(f"{self.window_width}x{self.window_height}+\
                                {self.x_position}+{self.y_position}")

        # 设置窗口标题
        self.win.title(title)
    
    # 填充ctl_frame的控件
    def __add_base_ctl_frame__(self):
        # 创建ip输入框
        self.ip_box = self.__create_entry__(self.base_ctl_frame, 0, 0, "IP Address")

        # 创建通道选择框
        val = [channel.value for channel in ds.Channel]
        self.ch_box        = self.__create_optionmenu__(self.base_ctl_frame, val, None, 0, 1)

        # 创建连接按钮
        self.connect_btn   = self.__create_button__(self.base_ctl_frame, "Connect",
                    lambda: self.cmd.connect(self, self.ip_box.get()), 1, 0,)
        self.connect_btn.grid(columnspan = 2)

        # 创建start按钮
        self.start_btn     = self.__create_button__(self.base_ctl_frame, "Start",
                    lambda: self.cmd.start(self, self.ch_box.get()), 2, 0)

        # 创建run/stop按钮
        self.run_stop_btn      = self.__create_button__(self.base_ctl_frame, "Run/Stop",
                    lambda: self.cmd.run_stop(self), 2, 1)

        # 创建divy_plus按钮
        self.divy_plus_btn = self.__create_button__(self.base_ctl_frame, "Divy +",
                    lambda: self.cmd.divy_plus(self), 3, 0)

        # 创建divy_sub按钮
        self.divy_sub_btn  = self.__create_button__(self.base_ctl_frame, "Divy _",
                    lambda: self.cmd.divy_sub(self),  3, 1)

        # 创建divx_plus按钮
        self.divx_plus_btn = self.__create_button__(self.base_ctl_frame, "Divx +",
                    lambda: self.cmd.divx_plus(self), 4, 0)

        # 创建divx_sub按钮
        self.divx_sub_btn  = self.__create_button__(self.base_ctl_frame, "Divx -",
                    lambda: self.cmd.divx_sub(self),  4, 1)

        # 创建close按钮
        self.close_btn = self.__create_button__(self.base_ctl_frame, "Close",
                    lambda: self.cmd.close(self), 5, 0)
        self.close_btn.grid(columnspan = 2)

        # 创建save按钮
        self.save_btn = self.__create_button__(self.base_ctl_frame, "Save",
                    lambda: self.cmd.save(self), 6, 0)
        self.save_btn.grid(columnspan = 2)
    
    # 设置info_frame
    def __init_infor_frame__(self):
        # 创建info的textbox
        self.info_box = self.__create_info_box__(self.info_frame, 0, 0, 400, 200)

        # 启动info刷新线程
        self.info_thread = thread.daemon(self.cmd.__always_refresh_info__, self)

        # 创建stdout和stderr显示的textbox
        self.runtime_box = self.__create_info_box__(self.info_frame, 1, 0, 400, 200)
        self.runtime_box.configure(state="normal")

        # 非阻塞刷新runtime_box
        self.runtime_thread = thread.daemon(self.__refresh_runtime_box__)
    
    # 设置disp_frame用于包含plt绘图
    def __init__disp_frame__(self, parent):
        self.figure = plt.Figure(figsize=(13, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(expand=True, fill="both")

    # 创建textbox用于显示info
    def __create_info_box__(self, parent, row, column, width=200, height=25):
        textbox = ctk.CTkTextbox(parent, width=width, height=height, state="normal")
        textbox.configure(font=("Courier", 12))  # 设置等宽字体
        textbox.grid(row=row, column=column, padx=5, pady=5)
        return textbox

    # 创建按钮宏
    def __create_button__(self, parent, text, command, row, column,
                    width=200, height=25):
        button = ctk.CTkButton(parent, text=text, command=command,
                    width=width, height=height)
        button.grid(row=row, column=column, padx=5, pady=5, sticky="ew")
        return button
    
    # 创建输入框宏
    def __create_entry__(self, parent, row, column, text, width=200, height=25):
        entry = ctk.CTkEntry(parent, width=width,
                    height=height, placeholder_text=text)
        entry.grid(row=row, column=column, padx=5, pady=5)
        return entry
    
    # 创建多选择框宏
    def __create_optionmenu__(self, parent, values, command, row,
                    column, width=200, height=25):
        optionmenu = ctk.CTkOptionMenu(parent, values=values, 
                    command=command, width=width, height=height)
        optionmenu.grid(row=row, column=column, padx=5, pady=5)
        return optionmenu

    # 创建frame宏
    def __create_frame__(self, parent, side, fill, anchor=None):
        frame = ctk.CTkFrame(parent)
        frame.pack(side=side, fill=fill, padx=5, pady=5, anchor="n")
        return frame
    
    # 创建runtime_refresh刷新线程
    def __refresh_runtime_box__(self):
        self.cmd.__auto_refresh_runtime_box__(self)