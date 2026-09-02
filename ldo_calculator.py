# -*- coding: utf-8 -*-
"""
LDO-Calculator - LDO参数计算工具
功能：
1. 温度系数计算：随温升的输出电压偏差（含曲线图）
2. 输入电压范围计算：基于压差和封装耗散功率
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np


# ==================== Aurora 深色主题配色 ====================
COLORS = {
    # 背景色
    "bg_dark": "#0f0f1a",        # 最深背景
    "bg_main": "#151525",        # 主背景
    "bg_card": "#1a1a2e",        # 卡片背景
    "bg_input": "#252540",       # 输入框背景
    "bg_hover": "#2a2a45",       # 悬停背景
    
    # 强调色（渐变）
    "accent_purple": "#7c3aed",  # 紫色
    "accent_blue": "#3b82f6",    # 蓝色
    "accent_cyan": "#06b6d4",    # 青色
    "accent_green": "#10b981",   # 绿色
    "accent_orange": "#f59e0b",  # 橙色
    "accent_red": "#ef4444",     # 红色
    
    # 文字色
    "text_primary": "#ffffff",   # 主要文字（白色）
    "text_secondary": "#a0a0b0", # 次要文字（灰色）
    "text_muted": "#6b7280",     # 弱化文字
    
    # 边框色
    "border": "#2d2d4a",         # 边框
    "border_light": "#3d3d5a",   # 浅边框
    
    # 按钮
    "btn_primary": "#7c3aed",    # 主按钮
    "btn_hover": "#6d28d9",      # 主按钮悬停
    "btn_secondary": "#374151",  # 次要按钮
    
    # 滑块
    "slider_trough": "#252540",  # 滑块轨道
    "slider_track": "#7c3aed",   # 滑块轨迹
}

# matplotlib 图表配色
CHART_COLORS = {
    "bg": "#1a1a2e",
    "grid": "#2d2d4a",
    "text": "#ffffff",
    "upper": "#ef4444",
    "lower": "#3b82f6",
    "nominal": "#a0a0b0",
    "fill": "#7c3aed",
}


class LDOCalculator:
    VERSION = "V1.0.0"
    
    def __init__(self, root):
        self.root = root
        self.root.title("LDO-Calculator")
        self.root.resizable(True, True)
        self.root.configure(bg=COLORS["bg_main"])

        # 启动时隐藏窗口，避免闪烁
        self.root.withdraw()

        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        # 获取屏幕分辨率并自适应窗口大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算窗口大小（屏幕的85%）
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)
        
        # 设置最小尺寸
        self.root.minsize(1200, 800)
        
        # 窗口居中显示
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

        # 保存屏幕分辨率用于后续缩放
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scale_factor = min(screen_width / 1920, screen_height / 1080)

        # 配置样式
        self._setup_styles()

        # matplotlib 中文支持和暗色主题
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
        plt.rcParams["axes.unicode_minus"] = False
        plt.rcParams["figure.facecolor"] = CHART_COLORS["bg"]
        plt.rcParams["axes.facecolor"] = CHART_COLORS["bg"]
        plt.rcParams["axes.edgecolor"] = CHART_COLORS["grid"]
        plt.rcParams["axes.labelcolor"] = CHART_COLORS["text"]
        plt.rcParams["xtick.color"] = CHART_COLORS["text"]
        plt.rcParams["ytick.color"] = CHART_COLORS["text"]
        plt.rcParams["text.color"] = CHART_COLORS["text"]

        # 主容器
        self.main_container = tk.Frame(self.root, bg=COLORS["bg_main"])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 顶部标题栏
        self._build_header()

        # 创建 Notebook（选项卡）
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        # 创建两个选项卡
        self.tab_temp = ttk.Frame(self.notebook)
        self.tab_dropout = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_temp, text="  📊 输出电压偏差计算  ")
        self.notebook.add(self.tab_dropout, text="  ⚡ 输入电压范围计算  ")

        # 温度系数 tab 的标记点列表
        self.temp_marks = []

        self._build_temp_tab()
        self._build_dropout_tab()

        # 所有组件构建完成后显示窗口
        self.root.deiconify()

    def _setup_styles(self):
        """配置 Aurora 暗色主题样式"""
        style = ttk.Style()
        style.theme_use("clam")

        # 根据屏幕分辨率计算字体缩放
        base_font = max(9, int(10 * self.scale_factor))
        header_font = max(12, int(14 * self.scale_factor))
        tab_font = max(9, int(10 * self.scale_factor))

        # Notebook 样式
        style.configure("TNotebook", background=COLORS["bg_main"], borderwidth=0)
        style.configure("TNotebook.Tab",
                        font=("Microsoft YaHei", tab_font),
                        padding=[15, 8],
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_muted"],
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", COLORS["accent_purple"]),
                              ("!selected", COLORS["bg_card"])],
                  foreground=[("selected", COLORS["text_primary"]),
                              ("!selected", COLORS["text_muted"])],
                  padding=[("selected", [20, 12]),
                           ("!selected", [15, 8])])

        # LabelFrame 样式
        style.configure("TLabelframe",
                        background=COLORS["bg_card"],
                        borderwidth=1,
                        relief="solid")
        style.configure("TLabelframe.Label",
                        font=("Microsoft YaHei", base_font, "bold"),
                        foreground=COLORS["accent_purple"],
                        background=COLORS["bg_card"])

        # Label 样式
        style.configure("TLabel",
                        font=("Microsoft YaHei", base_font),
                        background=COLORS["bg_card"],
                        foreground=COLORS["text_primary"])
        style.configure("Header.TLabel",
                        font=("Microsoft YaHei", header_font, "bold"),
                        foreground=COLORS["text_primary"],
                        background=COLORS["bg_card"])
        style.configure("SubHeader.TLabel",
                        font=("Microsoft YaHei", base_font + 1),
                        foreground=COLORS["text_secondary"],
                        background=COLORS["bg_card"])
        style.configure("Unit.TLabel",
                        font=("Microsoft YaHei", base_font),
                        foreground=COLORS["text_muted"],
                        background=COLORS["bg_card"])

        # Entry 样式
        style.configure("TEntry",
                        font=("Microsoft YaHei", base_font),
                        fieldbackground=COLORS["bg_input"],
                        foreground=COLORS["text_primary"],
                        borderwidth=1,
                        insertcolor=COLORS["text_primary"],
                        padding=8)
        style.map("TEntry",
                  bordercolor=[("focus", COLORS["accent_purple"])])

        # Button 样式
        style.configure("TButton",
                        font=("Microsoft YaHei", base_font, "bold"),
                        background=COLORS["btn_primary"],
                        foreground=COLORS["text_primary"],
                        borderwidth=0,
                        padding=[20, 10])
        style.map("TButton",
                  background=[("active", COLORS["btn_hover"]),
                              ("pressed", COLORS["accent_purple"])])

        style.configure("Accent.TButton",
                        font=("Microsoft YaHei", base_font, "bold"),
                        background=COLORS["accent_purple"],
                        foreground=COLORS["text_primary"],
                        borderwidth=0,
                        padding=[15, 8])
        style.map("Accent.TButton",
                  background=[("active", COLORS["btn_hover"])])

        style.configure("Small.TButton",
                        font=("Microsoft YaHei", base_font - 1),
                        background=COLORS["btn_secondary"],
                        foreground=COLORS["text_secondary"],
                        padding=[10, 5])
        style.map("Small.TButton",
                  background=[("active", COLORS["bg_hover"])])

        # Scale 样式
        style.configure("Horizontal.TScale",
                        troughcolor=COLORS["slider_trough"],
                        background=COLORS["accent_purple"])

    def _build_header(self):
        """构建顶部标题栏"""
        header_frame = tk.Frame(self.main_container, bg=COLORS["accent_purple"], height=60)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)

        # 渐变效果模拟（使用多个标签）
        gradient_frame = tk.Frame(header_frame, bg=COLORS["accent_purple"])
        gradient_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = tk.Label(gradient_frame,
                               text="📊 LDO-Calculator",
                               font=("Microsoft YaHei", 16, "bold"),
                               bg=COLORS["accent_purple"],
                               fg=COLORS["text_primary"])
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        # 副标题
        subtitle_label = tk.Label(gradient_frame,
                                  text="LDO参数计算工具",
                                  font=("Microsoft YaHei", 11),
                                  bg=COLORS["accent_purple"],
                                  fg="#e0e0ff")
        subtitle_label.pack(side=tk.LEFT, padx=10)

        # 版本号（右上角）
        version_label = tk.Label(gradient_frame,
                                 text=self.VERSION,
                                 font=("Consolas", 10, "bold"),
                                 bg=COLORS["accent_purple"],
                                 fg="#e0e0ff")
        version_label.pack(side=tk.RIGHT, padx=20, pady=10)

    # ==================== 温度系数计算 ====================
    def _build_temp_tab(self):
        # 主容器
        main_frame = tk.Frame(self.tab_temp, bg=COLORS["bg_main"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左右分栏（左侧2份，右侧3份，不使用PanedWindow避免白条）
        content_frame = tk.Frame(main_frame, bg=COLORS["bg_main"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=3)
        content_frame.rowconfigure(0, weight=1)

        left_frame = tk.Frame(content_frame, bg=COLORS["bg_main"])
        right_frame = tk.Frame(content_frame, bg=COLORS["bg_main"])
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # ---------- 左侧：参数输入 + 计算结果 ----------
        # 直接使用 Frame 布局，不使用滚动
        left_inner = tk.Frame(left_frame, bg=COLORS["bg_main"])
        left_inner.pack(fill=tk.BOTH, expand=True)

        # 标题区域
        title_frame = tk.Frame(left_inner, bg=COLORS["bg_main"])
        title_frame.pack(fill=tk.X, pady=(5, 10))
        tk.Label(title_frame, text="输出电压偏差计算", font=("Microsoft YaHei", 14, "bold"),
                 bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W)
        tk.Label(title_frame, text="温度系数 | ΔVout = ±TC × ΔT", font=("Microsoft YaHei", 11),
                 bg=COLORS["bg_main"], fg=COLORS["text_secondary"]).pack(anchor=tk.W, pady=(5, 0))

        # 参数输入
        input_frame = tk.LabelFrame(left_inner, text=" 📝 参数输入 ",
                                     bg=COLORS["bg_card"], fg=COLORS["accent_purple"],
                                     font=("Microsoft YaHei", 10, "bold"),
                                     bd=1, relief="solid", padx=15, pady=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # 参数
        params = [
            ("标称输出电压 Vout", "3.3", "V"),
            ("温度系数 TC", "0.7", "mV/°C", True),  # True = 需要 ±
            ("温度范围下限 T_low", "-40", "°C"),
            ("温度范围上限 T_high", "85", "°C"),
            ("当前芯片温度 T_chip", "40", "°C"),
        ]

        self.temp_entries = {}
        for item in params:
            label, default, unit = item[0], item[1], item[2]
            need_pm = item[3] if len(item) > 3 else False

            row = tk.Frame(input_frame, bg=COLORS["bg_card"])
            row.pack(fill=tk.X, pady=5)

            # 标签
            tk.Label(row, text=f"{label}:", width=20, anchor=tk.W,
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                     font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)

            # ± 前缀
            if need_pm:
                tk.Label(row, text="±", font=("Microsoft YaHei", 11, "bold"),
                         bg=COLORS["bg_card"], fg=COLORS["accent_red"],
                         width=2).pack(side=tk.LEFT)

            # 输入框
            entry = tk.Entry(row, width=10, font=("Microsoft YaHei", 10),
                            bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                            insertbackground=COLORS["text_primary"],
                            bd=1, relief="solid")
            entry.insert(0, default)
            entry.pack(side=tk.LEFT, padx=(0, 5))
            self.temp_entries[label] = entry

            # 单位
            tk.Label(row, text=unit, width=5,
                     bg=COLORS["bg_card"], fg=COLORS["text_muted"],
                     font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)

        # 按钮区域
        btn_frame = tk.Frame(left_inner, bg=COLORS["bg_main"])
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        calc_btn = tk.Button(btn_frame, text="🔍 计算", font=("Microsoft YaHei", 10, "bold"),
                            bg=COLORS["accent_purple"], fg=COLORS["text_primary"],
                            activebackground=COLORS["btn_hover"],
                            bd=0, padx=25, pady=8, width=10, command=self._calc_temp)
        calc_btn.pack(side=tk.LEFT)

        clear_btn = tk.Button(btn_frame, text="🗑️ 清除标记", font=("Microsoft YaHei", 10, "bold"),
                             bg=COLORS["btn_secondary"], fg=COLORS["text_secondary"],
                             activebackground=COLORS["bg_hover"],
                             bd=0, padx=25, pady=8, width=10, command=self._clear_marks)
        clear_btn.pack(side=tk.LEFT, padx=10)

        # 计算结果
        result_frame = tk.LabelFrame(left_inner, text=" 📊 计算过程 ",
                                      bg=COLORS["bg_card"], fg=COLORS["accent_cyan"],
                                      font=("Microsoft YaHei", 10, "bold"),
                                      bd=1, relief="solid", padx=12, pady=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.temp_result_text = tk.Text(result_frame, height=15,
                                        font=("Consolas", 9),
                                        state=tk.DISABLED,
                                        bg=COLORS["bg_input"],
                                        fg=COLORS["text_primary"],
                                        insertbackground=COLORS["text_primary"],
                                        relief=tk.FLAT,
                                        wrap=tk.WORD,
                                        padx=10, pady=10)
        self.temp_result_text.pack(fill=tk.BOTH, expand=True)

        # ---------- 右侧：曲线图 ----------
        chart_outer = tk.Frame(right_frame, bg=COLORS["bg_main"])
        chart_outer.pack(fill=tk.BOTH, expand=True, padx=(5, 5), pady=0)

        # 控制面板（固定在底部，足够大）
        control_frame = tk.Frame(chart_outer, bg=COLORS["bg_card"], height=100)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        control_frame.pack_propagate(False)

        # 图表区域（填充剩余空间）
        chart_frame = tk.LabelFrame(chart_outer, text=" 📈 输出电压 vs 温度曲线 ",
                                     bg=COLORS["bg_card"], fg=COLORS["accent_green"],
                                     font=("Microsoft YaHei", 10, "bold"),
                                     bd=1, relief="solid", padx=2, pady=2)
        chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 创建图表（初始大小由resize事件自动调整）
        self.temp_fig = Figure(dpi=100, facecolor=CHART_COLORS["bg"], figsize=(8, 6))
        self.temp_ax = self.temp_fig.add_subplot(111)
        self.temp_canvas = FigureCanvasTkAgg(self.temp_fig, master=chart_frame)
        canvas_widget = self.temp_canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas_widget.configure(bg=CHART_COLORS["bg"], highlightthickness=0)

        # 绑定窗口大小变化事件，让图表自适应
        def on_chart_resize(event):
            if event.width > 10 and event.height > 10:
                w_inch = event.width / self.temp_fig.dpi
                h_inch = event.height / self.temp_fig.dpi
                self.temp_fig.set_size_inches(w_inch, h_inch)
                self.temp_fig.subplots_adjust(left=0.07, right=0.99, top=0.92, bottom=0.15)
                self.temp_canvas.draw_idle()
        
        canvas_widget.bind("<Configure>", on_chart_resize)

        # 缩放控制
        zoom_frame = tk.LabelFrame(control_frame, text=" 缩放 ",
                                    bg=COLORS["bg_card"], fg=COLORS["accent_blue"],
                                    font=("Microsoft YaHei", 9, "bold"),
                                    bd=1, relief="solid", padx=8, pady=5)
        zoom_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # X轴缩放
        row1 = tk.Frame(zoom_frame, bg=COLORS["bg_card"])
        row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text="X轴:", width=5, bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)
        self.x_zoom_var = tk.DoubleVar(value=1.0)
        self.x_zoom_slider = ttk.Scale(row1, from_=0.2, to=5.0, variable=self.x_zoom_var,
                                        orient=tk.HORIZONTAL, command=self._on_zoom_change)
        self.x_zoom_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.x_zoom_label = tk.Label(row1, text="1.0x", width=5, font=("Consolas", 9),
                                     bg=COLORS["bg_card"], fg=COLORS["accent_cyan"])
        self.x_zoom_label.pack(side=tk.LEFT)

        # Y轴缩放
        row2 = tk.Frame(zoom_frame, bg=COLORS["bg_card"])
        row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text="Y轴:", width=5, bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)
        self.y_zoom_var = tk.DoubleVar(value=1.0)
        self.y_zoom_slider = ttk.Scale(row2, from_=0.2, to=5.0, variable=self.y_zoom_var,
                                        orient=tk.HORIZONTAL, command=self._on_zoom_change)
        self.y_zoom_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.y_zoom_label = tk.Label(row2, text="1.0x", width=5, font=("Consolas", 9),
                                     bg=COLORS["bg_card"], fg=COLORS["accent_cyan"])
        self.y_zoom_label.pack(side=tk.LEFT)

        tk.Button(zoom_frame, text="重置缩放", font=("Microsoft YaHei", 8),
                  bg=COLORS["btn_secondary"], fg=COLORS["text_secondary"],
                  bd=0, padx=10, pady=2, command=self._reset_zoom).pack(pady=(3, 0))

        # 平移控制
        pan_frame = tk.LabelFrame(control_frame, text=" 平移 ",
                                   bg=COLORS["bg_card"], fg=COLORS["accent_orange"],
                                   font=("Microsoft YaHei", 9, "bold"),
                                   bd=1, relief="solid", padx=8, pady=5)
        pan_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # X轴平移
        row3 = tk.Frame(pan_frame, bg=COLORS["bg_card"])
        row3.pack(fill=tk.X, pady=2)
        tk.Label(row3, text="X轴:", width=5, bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)
        self.x_pan_var = tk.DoubleVar(value=0.0)
        self.x_pan_slider = ttk.Scale(row3, from_=-100, to=100, variable=self.x_pan_var,
                                       orient=tk.HORIZONTAL, command=self._on_pan_change)
        self.x_pan_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.x_pan_label = tk.Label(row3, text="0.0", width=6, font=("Consolas", 9),
                                    bg=COLORS["bg_card"], fg=COLORS["accent_orange"])
        self.x_pan_label.pack(side=tk.LEFT)

        # Y轴平移
        row4 = tk.Frame(pan_frame, bg=COLORS["bg_card"])
        row4.pack(fill=tk.X, pady=2)
        tk.Label(row4, text="Y轴:", width=5, bg=COLORS["bg_card"],
                 fg=COLORS["text_primary"], font=("Microsoft YaHei", 9)).pack(side=tk.LEFT)
        self.y_pan_var = tk.DoubleVar(value=0.0)
        self.y_pan_slider = ttk.Scale(row4, from_=-100, to=100, variable=self.y_pan_var,
                                       orient=tk.HORIZONTAL, command=self._on_pan_change)
        self.y_pan_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.y_pan_label = tk.Label(row4, text="0.0", width=6, font=("Consolas", 9),
                                    bg=COLORS["bg_card"], fg=COLORS["accent_orange"])
        self.y_pan_label.pack(side=tk.LEFT)

        tk.Button(pan_frame, text="重置平移", font=("Microsoft YaHei", 8),
                  bg=COLORS["btn_secondary"], fg=COLORS["text_secondary"],
                  bd=0, padx=10, pady=2, command=self._reset_pan).pack(pady=(3, 0))

        # matplotlib 工具栏
        self.temp_toolbar = NavigationToolbar2Tk(self.temp_canvas, chart_frame)
        self.temp_toolbar.update()
        self.temp_toolbar.pack(side=tk.BOTTOM, fill=tk.X, pady=(3, 0))
        # 设置工具栏背景色
        try:
            self.temp_toolbar.configure(bg=COLORS["bg_card"])
            for child in self.temp_toolbar.winfo_children():
                try:
                    child.configure(bg=COLORS["bg_card"])
                except:
                    pass
        except:
            pass

        # 绑定事件
        self.temp_fig.canvas.mpl_connect("pick_event", self._on_temp_pick)
        self.temp_fig.canvas.mpl_connect("button_press_event", self._on_temp_click)

        # 保存数据
        self._temp_temps = None
        self._temp_vout_upper = None
        self._temp_vout_lower = None
        self._x_range_full = None
        self._y_range_full = None
        self._x_range_current = None
        self._y_range_current = None

    def _get_temp_entry(self, key):
        entry = self.temp_entries.get(key)
        if entry:
            return float(entry.get())
        return 0.0

    def _calc_temp(self):
        try:
            vout = self._get_temp_entry("标称输出电压 Vout")
            tc = self._get_temp_entry("温度系数 TC")
            t_low = self._get_temp_entry("温度范围下限 T_low")
            t_high = self._get_temp_entry("温度范围上限 T_high")
            t_chip = self._get_temp_entry("当前芯片温度 T_chip")

            if t_low >= t_high:
                messagebox.showerror("输入错误", "温度下限必须小于温度上限！")
                return
            if tc < 0:
                messagebox.showerror("输入错误", "温度系数不能为负数！")
                return

            T_REF = 25.0

            delta_t_max = max(abs(t_high - T_REF), abs(t_low - T_REF))
            delta_vout_max = tc * delta_t_max

            delta_t_chip = abs(t_chip - T_REF)
            delta_vout_chip = tc * delta_t_chip

            pct_max = (delta_vout_max / (vout * 1000)) * 100
            pct_chip = (delta_vout_chip / (vout * 1000)) * 100

            t_farthest = t_high if abs(t_high - T_REF) >= abs(t_low - T_REF) else t_low

            result = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  基准温度: 25°C (标称值 Vout={vout}V)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"【全温度范围最大偏差】\n"
                f"  范围: {t_low}°C ~ {t_high}°C\n"
                f"  最远端点: {t_farthest}°C\n"
                f"  ΔT = {delta_t_max}°C\n"
                f"  ΔVout = ±{tc} × {delta_t_max}\n"
                f"        = ±{delta_vout_max:.1f} mV ({pct_max:.3f}%)\n"
                f"  范围: {vout*1000 - delta_vout_max:.1f} ~ {vout*1000 + delta_vout_max:.1f} mV\n"
                f"        ({vout - delta_vout_max/1000:.4f} ~ {vout + delta_vout_max/1000:.4f} V)\n\n"
                f"【当前芯片温度 {t_chip}°C】\n"
                f"  ΔT = |{t_chip} - 25| = {delta_t_chip}°C\n"
                f"  ΔVout = ±{tc} × {delta_t_chip}\n"
                f"        = ±{delta_vout_chip:.1f} mV ({pct_chip:.3f}%)\n"
                f"  范围: {vout*1000 - delta_vout_chip:.1f} ~ {vout*1000 + delta_vout_chip:.1f} mV\n"
                f"        ({vout - delta_vout_chip/1000:.4f} ~ {vout + delta_vout_chip/1000:.4f} V)"
            )

            self.temp_result_text.config(state=tk.NORMAL)
            self.temp_result_text.delete("1.0", tk.END)
            self.temp_result_text.insert("1.0", result)
            self.temp_result_text.config(state=tk.DISABLED)

            self._plot_temp_curve(vout, tc, t_low, t_high, t_chip)

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")

    def _plot_temp_curve(self, vout, tc, t_low, t_high, t_chip, reset_sliders=True):
        self.temp_ax.clear()
        T_REF = 25.0

        temps = np.linspace(t_low, t_high, 300)
        vout_nom = vout * np.ones_like(temps)
        vout_upper = vout + tc / 1000.0 * (temps - T_REF)
        vout_lower = vout - tc / 1000.0 * (temps - T_REF)

        self._temp_temps = temps
        self._temp_vout_upper = vout_upper
        self._temp_vout_lower = vout_lower
        self._temp_vout_nom = vout_nom

        # 填充区域
        self.temp_ax.fill_between(temps, vout_lower * 1000, vout_upper * 1000,
                                  alpha=0.2, color=CHART_COLORS["fill"])

        # 曲线
        self.temp_ax.plot(temps, vout_upper * 1000, color=CHART_COLORS["upper"], linewidth=2,
                          linestyle="--", label=f"+ΔVout (±{tc} mV/°C)")
        self.temp_ax.plot(temps, vout_lower * 1000, color=CHART_COLORS["lower"], linewidth=2,
                          linestyle="--", label=f"-ΔVout (±{tc} mV/°C)")
        self.temp_ax.plot(temps, vout_nom * 1000, color=CHART_COLORS["nominal"], linewidth=2,
                          linestyle="-", label=f"标称 Vout={vout}V")

        # 高亮当前芯片温度点
        chip_vout_upper = vout + tc / 1000.0 * (t_chip - T_REF)
        chip_vout_lower = vout - tc / 1000.0 * (t_chip - T_REF)

        self.temp_ax.plot(t_chip, chip_vout_upper * 1000, "o", color=CHART_COLORS["upper"],
                          markersize=10, zorder=5, markeredgecolor="white", markeredgewidth=2)
        self.temp_ax.plot(t_chip, chip_vout_lower * 1000, "o", color=CHART_COLORS["lower"],
                          markersize=10, zorder=5, markeredgecolor="white", markeredgewidth=2)
        self.temp_ax.plot(t_chip, vout * 1000, "s", color=CHART_COLORS["nominal"],
                          markersize=8, zorder=5, markeredgecolor="white", markeredgewidth=2)

        offset = 0.015 * (vout_upper.max() - vout_lower.min()) * 1000
        self.temp_ax.annotate(f"+{chip_vout_upper*1000:.1f}mV",
                              xy=(t_chip, chip_vout_upper * 1000),
                              xytext=(t_chip + 2, chip_vout_upper * 1000 + offset),
                              fontsize=9, color=CHART_COLORS["upper"], fontweight="bold",
                              arrowprops=dict(arrowstyle="->", color=CHART_COLORS["upper"], lw=1))
        self.temp_ax.annotate(f"-{chip_vout_lower*1000:.1f}mV",
                              xy=(t_chip, chip_vout_lower * 1000),
                              xytext=(t_chip + 2, chip_vout_lower * 1000 - offset),
                              fontsize=9, color=CHART_COLORS["lower"], fontweight="bold",
                              arrowprops=dict(arrowstyle="->", color=CHART_COLORS["lower"], lw=1))

        # Mark 点
        mark_colors = ["#f39c12", "#2ecc71", "#9b59b6", "#1abc9c",
                       "#e67e22", "#3498db", "#e91e63", "#00bcd4", "#8bc34a", "#ef4444"]
        for i, (mx, my) in enumerate(self.temp_marks):
            color = mark_colors[i % len(mark_colors)]
            self.temp_ax.plot(mx, my, "^", color=color, markersize=12, zorder=6,
                              markeredgecolor="white", markeredgewidth=1.5,
                              label=f"Mark {i+1} ({mx:.1f}°C, {my:.1f}mV)")

        self.temp_ax.set_xlabel("温度 (°C)", fontsize=11, fontweight="bold")
        self.temp_ax.set_ylabel("输出电压 (mV)", fontsize=11, fontweight="bold")
        self.temp_ax.set_title(f"Vout vs 温度  |  TC=±{tc} mV/°C  |  T_chip={t_chip}°C",
                               fontsize=12, fontweight="bold", pad=15)
        legend = self.temp_ax.legend(fontsize=9, loc="best", framealpha=0.9,
                           facecolor=COLORS["bg_card"], edgecolor=COLORS["border"])
        self.temp_ax.grid(True, alpha=0.3, linestyle="--", color=CHART_COLORS["grid"])

        self._x_range_full = (t_low - 2, t_high + 2)
        y_min = min(vout_lower.min(), vout_upper.min()) * 1000
        y_max = max(vout_lower.max(), vout_upper.max()) * 1000
        y_margin = (y_max - y_min) * 0.1
        self._y_range_full = (y_min - y_margin, y_max + y_margin)

        if reset_sliders:
            self._x_range_current = self._x_range_full
            self._y_range_current = self._y_range_full
            self.temp_ax.set_xlim(self._x_range_full)
            self.temp_ax.set_ylim(self._y_range_full)

            self.x_zoom_var.set(1.0)
            self.y_zoom_var.set(1.0)
            self.x_zoom_label.config(text="1.0x")
            self.y_zoom_label.config(text="1.0x")
            self.x_pan_var.set(0.0)
            self.y_pan_var.set(0.0)
            self.x_pan_label.config(text="0.0")
            self.y_pan_label.config(text="0.0")

            x_half = (self._x_range_full[1] - self._x_range_full[0]) / 2
            y_half = (self._y_range_full[1] - self._y_range_full[0]) / 2
            self.x_pan_slider.config(from_=-x_half, to=x_half)
            self.y_pan_slider.config(from_=-y_half, to=y_half)

        self.temp_fig.subplots_adjust(left=0.07, right=0.99, top=0.92, bottom=0.15)
        self.temp_fig.canvas.draw_idle()

    def _on_temp_pick(self, event):
        pass

    def _on_temp_click(self, event):
        if event.inaxes != self.temp_ax:
            return
        if self._temp_temps is None:
            return

        click_temp = event.xdata
        click_vout = event.ydata

        if event.button == 3:
            if not self.temp_marks:
                return
            min_dist = float('inf')
            min_idx = -1
            for i, (mx, my) in enumerate(self.temp_marks):
                dist = np.sqrt((click_temp - mx) ** 2 + ((click_vout - my) * 0.05) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    min_idx = i
            if min_idx >= 0 and min_dist < 5:
                self.temp_marks.pop(min_idx)
                self._refresh_marks_on_chart()
            return

        if event.button != 1:
            return

        idx = np.argmin(np.abs(self._temp_temps - click_temp))
        nearest_temp = round(self._temp_temps[idx], 1)
        nearest_vout_upper = self._temp_vout_upper[idx] * 1000
        nearest_vout_lower = self._temp_vout_lower[idx] * 1000

        dist_upper = abs(click_vout - nearest_vout_upper)
        dist_lower = abs(click_vout - nearest_vout_lower)
        mark_vout = round(nearest_vout_upper, 1) if dist_upper < dist_lower else round(nearest_vout_lower, 1)

        for mx, my in self.temp_marks:
            if abs(mx - nearest_temp) < 0.5:
                return

        self.temp_marks.append((nearest_temp, mark_vout))
        self._refresh_marks_on_chart()

    def _refresh_marks_on_chart(self):
        if self._temp_temps is None:
            return
        vout = self._get_temp_entry("标称输出电压 Vout")
        tc = self._get_temp_entry("温度系数 TC")
        t_low = self._get_temp_entry("温度范围下限 T_low")
        t_high = self._get_temp_entry("温度范围上限 T_high")
        t_chip = self._get_temp_entry("当前芯片温度 T_chip")
        # 保存当前缩放/平移状态
        saved_zoom_x = self.x_zoom_var.get()
        saved_zoom_y = self.y_zoom_var.get()
        saved_pan_x = self.x_pan_var.get()
        saved_pan_y = self.y_pan_var.get()
        self._plot_temp_curve(vout, tc, t_low, t_high, t_chip, reset_sliders=False)
        # 恢复缩放/平移状态
        self.x_zoom_var.set(saved_zoom_x)
        self.y_zoom_var.set(saved_zoom_y)
        self.x_pan_var.set(saved_pan_x)
        self.y_pan_var.set(saved_pan_y)
        # 重新应用缩放和平移
        self._on_zoom_change()

    def _on_zoom_change(self, value=None):
        if self._x_range_full is None or self._y_range_full is None:
            return
        x_zoom = self.x_zoom_var.get()
        y_zoom = self.y_zoom_var.get()

        self.x_zoom_label.config(text=f"{x_zoom:.1f}x")
        self.y_zoom_label.config(text=f"{y_zoom:.1f}x")

        # 计算当前平移偏移量
        x_pan = self.x_pan_var.get()
        y_pan = self.y_pan_var.get()

        # 以全范围中心 + 平移偏移为基准缩放
        x_center = (self._x_range_full[0] + self._x_range_full[1]) / 2 + x_pan
        y_center = (self._y_range_full[0] + self._y_range_full[1]) / 2 + y_pan
        x_half = (self._x_range_full[1] - self._x_range_full[0]) / 2 / x_zoom
        y_half = (self._y_range_full[1] - self._y_range_full[0]) / 2 / y_zoom

        self.temp_ax.set_xlim(x_center - x_half, x_center + x_half)
        self.temp_ax.set_ylim(y_center - y_half, y_center + y_half)

        self._x_range_current = (x_center - x_half, x_center + x_half)
        self._y_range_current = (y_center - y_half, y_center + y_half)

        # 更新平移滑块范围（不重置值）
        self.x_pan_slider.config(from_=-x_half, to=x_half)
        self.y_pan_slider.config(from_=-y_half, to=y_half)

        self.temp_fig.canvas.draw_idle()

    def _on_pan_change(self, value=None):
        if self._x_range_current is None or self._y_range_current is None:
            return

        x_pan = self.x_pan_var.get()
        y_pan = self.y_pan_var.get()

        self.x_pan_label.config(text=f"{x_pan:.1f}")
        self.y_pan_label.config(text=f"{y_pan:.1f}")

        x_center = (self._x_range_current[0] + self._x_range_current[1]) / 2 + x_pan
        y_center = (self._y_range_current[0] + self._y_range_current[1]) / 2 + y_pan
        x_half = (self._x_range_current[1] - self._x_range_current[0]) / 2
        y_half = (self._y_range_current[1] - self._y_range_current[0]) / 2

        self.temp_ax.set_xlim(x_center - x_half, x_center + x_half)
        self.temp_ax.set_ylim(y_center - y_half, y_center + y_half)
        self.temp_fig.canvas.draw_idle()

    def _reset_zoom(self):
        self.x_zoom_var.set(1.0)
        self.y_zoom_var.set(1.0)
        self.x_zoom_label.config(text="1.0x")
        self.y_zoom_label.config(text="1.0x")
        if self._x_range_full is not None and self._y_range_full is not None:
            # 保持当前平移偏移
            x_pan = self.x_pan_var.get()
            y_pan = self.y_pan_var.get()
            x_center = (self._x_range_full[0] + self._x_range_full[1]) / 2 + x_pan
            y_center = (self._y_range_full[0] + self._y_range_full[1]) / 2 + y_pan
            x_half = (self._x_range_full[1] - self._x_range_full[0]) / 2
            y_half = (self._y_range_full[1] - self._y_range_full[0]) / 2
            self.temp_ax.set_xlim(x_center - x_half, x_center + x_half)
            self.temp_ax.set_ylim(y_center - y_half, y_center + y_half)
            self._x_range_current = (x_center - x_half, x_center + x_half)
            self._y_range_current = (y_center - y_half, y_center + y_half)
            self.x_pan_slider.config(from_=-x_half, to=x_half)
            self.y_pan_slider.config(from_=-y_half, to=y_half)
            self.temp_fig.canvas.draw_idle()

    def _reset_pan(self):
        self.x_pan_var.set(0.0)
        self.y_pan_var.set(0.0)
        self.x_pan_label.config(text="0.0")
        self.y_pan_label.config(text="0.0")
        if self._x_range_current is not None and self._y_range_current is not None:
            x_center = (self._x_range_full[0] + self._x_range_full[1]) / 2
            y_center = (self._y_range_full[0] + self._y_range_full[1]) / 2
            x_half = (self._x_range_current[1] - self._x_range_current[0]) / 2
            y_half = (self._y_range_current[1] - self._y_range_current[0]) / 2
            self.temp_ax.set_xlim(x_center - x_half, x_center + x_half)
            self.temp_ax.set_ylim(y_center - y_half, y_center + y_half)
            self.temp_fig.canvas.draw_idle()

    def _clear_marks(self):
        self.temp_marks.clear()
        if self._temp_temps is not None:
            self._refresh_marks_on_chart()

    # ==================== 输入电压范围计算 ====================
    def _build_dropout_tab(self):
        main_frame = tk.Frame(self.tab_dropout, bg=COLORS["bg_main"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 标题区域
        title_frame = tk.Frame(main_frame, bg=COLORS["bg_main"])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(title_frame, text="LDO输入电压范围计算", font=("Microsoft YaHei", 14, "bold"),
                 bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(anchor=tk.W)
        tk.Label(title_frame, text="公式：Vin_min = Vout + Vdropout，Vin_max = Vout + Pd_max / Iout",
                 font=("Microsoft YaHei", 11), bg=COLORS["bg_main"],
                 fg=COLORS["text_secondary"]).pack(anchor=tk.W, pady=(5, 0))

        # 输入区域
        input_frame = tk.LabelFrame(main_frame, text=" 📝 参数输入 ",
                                     bg=COLORS["bg_card"], fg=COLORS["accent_purple"],
                                     font=("Microsoft YaHei", 10, "bold"),
                                     bd=1, relief="solid", padx=20, pady=15)
        input_frame.pack(fill=tk.X, pady=(0, 15))

        grid_frame = tk.Frame(input_frame, bg=COLORS["bg_card"])
        grid_frame.pack(fill=tk.X)

        self.dn_entries = {}

        # 左列参数
        left_params = [
            ("标称输出电压 Vout", "3.3", "V"),
            ("最大输出电流 Iout", "250", "mA"),
        ]

        left_frame = tk.Frame(grid_frame, bg=COLORS["bg_card"])
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))

        for label, default, unit in left_params:
            row = tk.Frame(left_frame, bg=COLORS["bg_card"])
            row.pack(fill=tk.X, pady=8)
            tk.Label(row, text=f"{label}:", width=25, anchor=tk.W,
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                     font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
            entry = tk.Entry(row, width=12, font=("Microsoft YaHei", 10),
                            bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                            insertbackground=COLORS["text_primary"], bd=1, relief="solid")
            entry.insert(0, default)
            entry.pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(row, text=unit, width=6, bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
            self.dn_entries[label] = entry

        # 右列参数
        right_params = [
            ("测试条件下压差 Vdo_test", "80", "mV"),
            ("测试条件电流 Iout_test", "40", "mA"),
        ]

        right_frame = tk.Frame(grid_frame, bg=COLORS["bg_card"])
        right_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        for label, default, unit in right_params:
            row = tk.Frame(right_frame, bg=COLORS["bg_card"])
            row.pack(fill=tk.X, pady=8)
            tk.Label(row, text=f"{label}:", width=25, anchor=tk.W,
                     bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                     font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
            entry = tk.Entry(row, width=12, font=("Microsoft YaHei", 10),
                            bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                            insertbackground=COLORS["text_primary"], bd=1, relief="solid")
            entry.insert(0, default)
            entry.pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(row, text=unit, width=6, bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
            self.dn_entries[label] = entry

        # 封装耗散功率（带计算按钮）
        pd_row = tk.Frame(right_frame, bg=COLORS["bg_card"])
        pd_row.pack(fill=tk.X, pady=8)
        tk.Label(pd_row, text="封装耗散功率 Pd_max:", width=25, anchor=tk.W,
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"],
                 font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
        self.dn_entries["封装耗散功率 Pd_max"] = tk.Entry(pd_row, width=10, font=("Microsoft YaHei", 10),
                            bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                            insertbackground=COLORS["text_primary"], bd=1, relief="solid")
        self.dn_entries["封装耗散功率 Pd_max"].insert(0, "0.3")
        self.dn_entries["封装耗散功率 Pd_max"].pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(pd_row, text="W", width=3, bg=COLORS["bg_card"],
                 fg=COLORS["text_muted"], font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
        tk.Button(pd_row, text="计算", font=("Microsoft YaHei", 8),
                  bg=COLORS["accent_purple"], fg=COLORS["text_primary"],
                  activebackground=COLORS["btn_hover"],
                  bd=0, padx=8, pady=2, command=self._calc_pd_max).pack(side=tk.LEFT, padx=(5, 0))

        # 说明
        info_frame = tk.Frame(main_frame, bg=COLORS["bg_main"])
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧说明文字
        info_left = tk.Frame(info_frame, bg=COLORS["bg_main"])
        info_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(info_left, text="💡 说明：Vdropout = (Iout / Iout_test) × Vdo_test（线性估算）",
                 font=("Microsoft YaHei", 10), bg=COLORS["bg_main"],
                 fg=COLORS["text_secondary"]).pack(anchor=tk.W)
        tk.Label(info_left, text="   示例：ME6209A33M3G SOT23-3, Vout=3.3V, Iout=250mA → Vin: 3.8V~4.5V",
                 font=("Microsoft YaHei", 10), bg=COLORS["bg_main"],
                 fg=COLORS["text_muted"]).pack(anchor=tk.W)

        # 右侧状态提示
        self.status_frame = tk.Frame(info_frame, bg=COLORS["bg_main"], width=300)
        self.status_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_frame.pack_propagate(False)
        self.status_label = tk.Label(self.status_frame, text="",
                                     font=("Microsoft YaHei", 12, "bold"),
                                     bg=COLORS["bg_main"], fg=COLORS["text_muted"])
        self.status_label.pack(expand=True)

        # 计算按钮
        btn_frame = tk.Frame(main_frame, bg=COLORS["bg_main"])
        btn_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Button(btn_frame, text="🔍 计算", font=("Microsoft YaHei", 10, "bold"),
                  bg=COLORS["accent_purple"], fg=COLORS["text_primary"],
                  activebackground=COLORS["btn_hover"],
                  bd=0, padx=30, pady=10, command=self._calc_dropout).pack(side=tk.LEFT)

        # 计算过程区域（使用pack_side确保不被挤出）
        result_frame = tk.LabelFrame(main_frame, text=" 📊 计算过程 ",
                                      bg=COLORS["bg_card"], fg=COLORS["accent_cyan"],
                                      font=("Microsoft YaHei", 10, "bold"),
                                      bd=1, relief="solid", padx=15, pady=5)
        result_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(0, 8))

        self.dn_result_text = tk.Text(result_frame, height=1,
                                      font=("Consolas", 10),
                                      state=tk.DISABLED,
                                      bg=COLORS["bg_input"],
                                      fg=COLORS["text_primary"],
                                      insertbackground=COLORS["text_primary"],
                                      relief=tk.FLAT,
                                      wrap=tk.WORD,
                                      padx=10, pady=5)
        self.dn_result_text.pack(fill=tk.BOTH, expand=True)

        # 结果显示区域（VIN_MIN 和 VIN_MAX）- 先pack确保不被挤出
        result_display = tk.Frame(main_frame, bg=COLORS["bg_main"])
        result_display.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 5))

        # VIN_MIN
        vin_min_frame = tk.LabelFrame(result_display, text=" VIN_MIN ",
                                       bg=COLORS["bg_card"], fg=COLORS["accent_orange"],
                                       font=("Microsoft YaHei", 11, "bold"),
                                       bd=1, relief="solid", padx=15, pady=8)
        vin_min_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.vin_min_label = tk.Label(vin_min_frame, text="--- V",
                                      font=("Consolas", 18, "bold"),
                                      bg=COLORS["bg_card"], fg=COLORS["accent_orange"])
        self.vin_min_label.pack()

        # VIN_MAX
        vin_max_frame = tk.LabelFrame(result_display, text=" VIN_MAX ",
                                       bg=COLORS["bg_card"], fg=COLORS["accent_green"],
                                       font=("Microsoft YaHei", 11, "bold"),
                                       bd=1, relief="solid", padx=15, pady=8)
        vin_max_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.vin_max_label = tk.Label(vin_max_frame, text="--- V",
                                      font=("Consolas", 18, "bold"),
                                      bg=COLORS["bg_card"], fg=COLORS["accent_green"])
        self.vin_max_label.pack()

    def _calc_pd_max(self):
        """通过热参数计算封装耗散功率 Pmax = (Tjmax - Ta) / Rθja"""
        dialog = tk.Toplevel(self.root)
        dialog.title("计算封装耗散功率")
        dialog.geometry("400x300")
        dialog.configure(bg=COLORS["bg_main"])
        dialog.transient(self.root)
        dialog.grab_set()

        # 设置对话框图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo.ico")
        if os.path.exists(icon_path):
            dialog.iconbitmap(icon_path)

        # 标题
        tk.Label(dialog, text="Pmax = (Tjmax - Ta) / Rθja",
                 font=("Microsoft YaHei", 12, "bold"),
                 bg=COLORS["bg_main"], fg=COLORS["text_primary"]).pack(pady=(15, 10))

        # 参数输入区域
        params_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        params_frame.pack(fill=tk.X, padx=30)

        # Tjmax
        row1 = tk.Frame(params_frame, bg=COLORS["bg_main"])
        row1.pack(fill=tk.X, pady=5)
        tk.Label(row1, text="Tjmax (最大结温):", width=20, anchor=tk.W,
                 bg=COLORS["bg_main"], fg=COLORS["text_primary"],
                 font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
        tjmax_entry = tk.Entry(row1, width=10, font=("Microsoft YaHei", 10),
                              bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                              insertbackground=COLORS["text_primary"], bd=1, relief="solid")
        tjmax_entry.insert(0, "125")
        tjmax_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(row1, text="°C", bg=COLORS["bg_main"],
                 fg=COLORS["text_muted"], font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)

        # Ta
        row2 = tk.Frame(params_frame, bg=COLORS["bg_main"])
        row2.pack(fill=tk.X, pady=5)
        tk.Label(row2, text="Ta (环境温度):", width=20, anchor=tk.W,
                 bg=COLORS["bg_main"], fg=COLORS["text_primary"],
                 font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
        ta_entry = tk.Entry(row2, width=10, font=("Microsoft YaHei", 10),
                           bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                           insertbackground=COLORS["text_primary"], bd=1, relief="solid")
        ta_entry.insert(0, "25")
        ta_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(row2, text="°C", bg=COLORS["bg_main"],
                 fg=COLORS["text_muted"], font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)

        # Rθja
        row3 = tk.Frame(params_frame, bg=COLORS["bg_main"])
        row3.pack(fill=tk.X, pady=5)
        tk.Label(row3, text="Rθja (热阻):", width=20, anchor=tk.W,
                 bg=COLORS["bg_main"], fg=COLORS["text_primary"],
                 font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
        rthja_entry = tk.Entry(row3, width=10, font=("Microsoft YaHei", 10),
                              bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                              insertbackground=COLORS["text_primary"], bd=1, relief="solid")
        rthja_entry.insert(0, "333")
        rthja_entry.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(row3, text="°C/W", bg=COLORS["bg_main"],
                 fg=COLORS["text_muted"], font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)

        # 结果显示
        result_var = tk.StringVar(value="Pmax = --- W")
        tk.Label(dialog, textvariable=result_var,
                 font=("Consolas", 12, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["accent_cyan"],
                 padx=20, pady=8).pack(pady=10, fill=tk.X, padx=30)

        def calc_and_apply():
            try:
                tjmax = float(tjmax_entry.get())
                ta = float(ta_entry.get())
                rthja = float(rthja_entry.get())
                if rthja <= 0:
                    messagebox.showerror("错误", "热阻必须大于0！", parent=dialog)
                    return
                pmax = (tjmax - ta) / rthja
                result_var.set(f"Pmax = {pmax:.4f} W")
                # 填入主界面
                self.dn_entries["封装耗散功率 Pd_max"].delete(0, tk.END)
                self.dn_entries["封装耗散功率 Pd_max"].insert(0, f"{pmax:.4f}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字！", parent=dialog)

        # 按钮
        btn_frame = tk.Frame(dialog, bg=COLORS["bg_main"])
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="计算并应用", font=("Microsoft YaHei", 10, "bold"),
                  bg=COLORS["accent_purple"], fg=COLORS["text_primary"],
                  activebackground=COLORS["btn_hover"],
                  bd=0, padx=20, pady=8, command=calc_and_apply).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", font=("Microsoft YaHei", 10),
                  bg=COLORS["btn_secondary"], fg=COLORS["text_secondary"],
                  activebackground=COLORS["bg_hover"],
                  bd=0, padx=20, pady=8, command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _get_dn_entry(self, key):
        entry = self.dn_entries.get(key)
        if entry:
            return float(entry.get())
        return 0.0

    def _calc_dropout(self):
        try:
            vout = self._get_dn_entry("标称输出电压 Vout")
            iout = self._get_dn_entry("最大输出电流 Iout")
            vdo_test = self._get_dn_entry("测试条件下压差 Vdo_test")
            iout_test = self._get_dn_entry("测试条件电流 Iout_test")
            pd_max = self._get_dn_entry("封装耗散功率 Pd_max")

            if iout <= 0 or iout_test <= 0:
                messagebox.showerror("输入错误", "电流必须大于0！")
                return
            if vout <= 0:
                messagebox.showerror("输入错误", "输出电压必须大于0！")
                return

            vdropout = (iout / iout_test) * vdo_test
            vin_min = vout + vdropout / 1000
            vin_max = vout + (pd_max / (iout / 1000))

            warnings = []
            if vin_min >= vin_max:
                warnings.append("⚠️ Vin_min ≥ Vin_max，参数不合理！请检查输入。")
            if vdropout / 1000 > pd_max / (iout / 1000):
                warnings.append("⚠️ 压差功耗超过封装限制，实际最大带载会降低。")

            pd_at_max = (vin_max - vout) * (iout / 1000)

            result = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  输入电压范围计算过程\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"【压差计算】\n"
                f"  Vdropout = (Iout / Iout_test) × Vdo_test\n"
                f"           = ({iout}mA / {iout_test}mA) × {vdo_test}mV\n"
                f"           = {vdropout:.1f} mV = {vdropout/1000:.4f} V\n\n"
                f"【输入电压范围】\n"
                f"  Vin_min = Vout + Vdropout\n"
                f"          = {vout}V + {vdropout/1000:.4f}V\n"
                f"          = {vin_min:.4f} V\n\n"
                f"  Vin_max = Vout + Pd_max / Iout\n"
                f"          = {vout}V + {pd_max}W / {iout/1000:.3f}A\n"
                f"          = {vout}V + {pd_max/(iout/1000):.4f}V\n"
                f"          = {vin_max:.4f} V\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  ★ 输入电压范围: {vin_min:.4f}V ~ {vin_max:.4f}V\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"【验证】\n"
                f"  Vin_min时功耗: ({vin_min:.4f}-{vout})×{iout/1000:.3f}A\n"
                f"               = {(vin_min-vout)*iout/1000:.4f}W ≤ {pd_max}W ✓\n"
                f"  Vin_max时功耗: ({vin_max:.4f}-{vout})×{iout/1000:.3f}A\n"
                f"               = {pd_at_max:.4f}W = {pd_max}W ✓"
            )

            # 参数不合理的详细解释
            if vin_min >= vin_max:
                vdrop_status = "压差过大" if vdropout / 1000 > 1.0 else "压差偏大"
                pd_status = "封装散热不够" if pd_max < (iout / 1000) * 1.0 else "封装散热限制"
                result += (
                    f"\n\n{'━' * 36}\n"
                    f"  ⚠️ 参数不合理的解释\n"
                    f"{'━' * 36}\n\n"
                    f"【问题参数】\n"
                    f"  · Iout = {iout}mA{' (太大)' if iout > 300 else ''}\n"
                    f"  · Vdropout = {vdropout:.1f}mV = {vdropout/1000:.4f}V\n"
                    f"    {'(' + vdrop_status + ')' if vdropout / 1000 > 0.5 else ''}\n"
                    f"  · Pd_max = {pd_max}W ({pd_status})\n\n"
                    f"【分析结果】\n"
                    f"  · Vin_min = {vout} + {vdropout/1000:.4f} = {vin_min:.4f}V\n"
                    f"    (需要这么高的输入电压才能带载)\n"
                    f"  · Vin_max = {vout} + {pd_max/(iout/1000):.4f} = {vin_max:.4f}V\n"
                    f"    (超过这个电压芯片会过热)\n\n"
                    f"【结论】\n"
                    f"  在 {iout}mA 负载下，需要的最小输入电压\n"
                    f"  ({vin_min:.4f}V) 超过了芯片能承受的最大\n"
                    f"  输入电压 ({vin_max:.4f}V)，说明这个 LDO\n"
                    f"  不适合带这么大的负载。\n"
                    f"{'━' * 36}"
                )
            elif warnings:
                result += "\n\n" + "\n".join(warnings)

            self.dn_result_text.config(state=tk.NORMAL)
            self.dn_result_text.delete("1.0", tk.END)
            self.dn_result_text.insert("1.0", result)
            self.dn_result_text.config(state=tk.DISABLED)

            # 更新 VIN_MIN 和 VIN_MAX 显示及状态提示
            if vin_min >= vin_max:
                # 参数不合理时，显示警告色
                self.vin_min_label.config(text=f"{vin_min:.4f} V", fg=COLORS["accent_red"])
                self.vin_max_label.config(text=f"{vin_max:.4f} V", fg=COLORS["accent_red"])
                self.status_label.config(text="❌ 参数不合理，请查看计算过程",
                                        fg=COLORS["accent_red"])
            else:
                self.vin_min_label.config(text=f"{vin_min:.4f} V", fg=COLORS["accent_orange"])
                self.vin_max_label.config(text=f"{vin_max:.4f} V", fg=COLORS["accent_green"])
                self.status_label.config(text="✅ 结果正常，输入电压范围有效",
                                        fg=COLORS["accent_green"])

        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字！")


if __name__ == "__main__":
    root = tk.Tk()
    app = LDOCalculator(root)
    root.mainloop()
