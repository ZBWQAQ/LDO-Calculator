# LDO-Calculator

> **版本**：V1.0.0 | **更新日期**：2024-09-02

LDO（低压差线性稳压器）参数计算工具，使用 Python + tkinter + matplotlib 构建，采用 Aurora 深色主题。

---

## 功能概述

### 1. 输出电压偏差计算（温度系数）

- **公式**：`ΔVout = ±TC × ΔT`（基准温度 25°C）
- **输入参数**：
  | 参数 | 说明 | 单位 | 默认值 |
  |------|------|------|--------|
  | Vout | 标称输出电压 | V | 3.3 |
  | TC | 温度系数 | mV/°C | 0.7 |
  | T_low | 温度范围下限 | °C | -40 |
  | T_high | 温度范围上限 | °C | 85 |
  | T_chip | 当前芯片温度 | °C | 40 |

- **输出**：全温度范围最大偏差（mV / %）、当前芯片温度下的偏差、输出电压范围

- **曲线图**：
  - X轴：温度 (°C)，Y轴：输出电压 (mV)
  - 上偏差曲线（红色虚线）+ 下偏差曲线（蓝色虚线）
  - 标称值曲线（灰色实线）
  - 偏差范围填充区域（紫色）
  - 当前芯片温度高亮点（带数值标注）

- **交互功能**：
  - 左键点击曲线标记 Mark 点（不同颜色区分，Mark 1, Mark 2...）
  - 右键点击取消最近的 Mark 点
  - X/Y 轴缩放滑块（0.2x ~ 5.0x）
  - X/Y 轴平移滑块
  - matplotlib 内置工具栏

### 2. 输入电压范围计算（LDO 压差）

- **公式**：
  - `Vdropout = (Iout / Iout_test) × Vdo_test`（线性估算）
  - `Vin_min = Vout + Vdropout`
  - `Vin_max = Vout + Pd_max / Iout`

- **封装耗散功率计算**：`Pmax = (Tjmax - Ta) / Rθja`

- **输入参数**：
  | 参数 | 说明 | 单位 | 默认值 |
  |------|------|------|--------|
  | Vout | 标称输出电压 | V | 3.3 |
  | Iout | 最大输出电流 | mA | 250 |
  | Vdo_test | 测试条件下压差 | mV | 80 |
  | Iout_test | 测试条件电流 | mA | 40 |
  | Pd_max | 封装耗散功率 | W | 0.3 |

- **输出**：VIN_MIN / VIN_MAX 结果显示、计算过程详情、状态提示（正常/异常）

- **智能提示**：
  - ✅ **结果正常**：VIN_MIN < VIN_MAX，输入电压范围有效
  - ❌ **参数不合理**：VIN_MIN ≥ VIN_MAX，显示详细解释

---

## 运行方式

### 方式一：EXE 运行（推荐）

直接双击 `dist/LDO-Calculator.exe`

### 方式二：源码运行

```bash
cd LDO-Calculator
pip install matplotlib numpy Pillow
python ldo_calculator.py
```

### 方式三：虚拟环境运行

```bash
cd LDO-Calculator
uv venv .venv --python 3.14
.venv\Scripts\activate
uv pip install matplotlib numpy Pillow
python ldo_calculator.py
```

### 方式四：快捷脚本

双击 `run.bat`

### 打包为 EXE

```bash
uv pip install pyinstaller
pyinstaller --onefile --windowed --name "LDO-Calculator" --icon="Logo.ico" ldo_calculator.py
```

---

## 界面设计

### Aurora 深色主题配色

| 元素 | 颜色 |
|------|------|
| 最深背景 | `#0f0f1a` |
| 主背景 | `#151525` |
| 卡片背景 | `#1a1a2e` |
| 输入框背景 | `#252540` |
| 主色调（紫色） | `#7c3aed` |
| 蓝色 | `#3b82f6` |
| 青色 | `#06b6d4` |
| 绿色 | `#10b981` |
| 橙色 | `#f59e0b` |
| 红色 | `#ef4444` |

### 布局
- 顶部标题栏（紫色渐变 + 版本号）
- 选项卡切换（输出电压偏差 / 输入电压范围）
- 窗口大小自动适配屏幕分辨率（85%），居中显示
- 无闪烁启动

---

## 项目文件结构

```
LDO-Calculator/
├── ldo_calculator.py        # 主程序
├── Logo.ico                 # 应用图标
├── Logo.png                 # 原始图标
├── convert_icon.py          # PNG 转 ICO 脚本
├── run.bat                  # Windows 快捷启动脚本
├── README.md                # 本文档
├── 开发文档.md              # 详细开发文档
├── LDO-Calculator.spec      # PyInstaller 配置文件
├── dist/                    # 打包输出目录
│   └── LDO-Calculator.exe   # 可执行文件（约 38.5 MB）
├── build/                   # 构建临时目录
└── .venv/                   # Python 虚拟环境
```

---

## 技术要点

### 图表自适应
```python
def on_chart_resize(event):
    w_inch = event.width / self.temp_fig.dpi
    h_inch = event.height / self.temp_fig.dpi
    self.temp_fig.set_size_inches(w_inch, h_inch)
    self.temp_fig.canvas.draw_idle()
```

### 无闪烁启动
```python
self.root.withdraw()          # 启动时隐藏
# ... 构建所有组件 ...
self.root.deiconify()         # 构建完成后显示
```

### Mark 点颜色区分
```python
mark_colors = ["#f39c12", "#2ecc71", "#9b59b6", "#1abc9c", ...]
for i, (mx, my) in enumerate(self.temp_marks):
    color = mark_colors[i % len(mark_colors)]
```

---

## 参考资料

- LDO 应用技术文档（温度系数、压差计算）
- ME6209A33M3G 数据手册（SOT23-3 封装参数）
- Matplotlib 官方文档
- tkinter 官方文档
