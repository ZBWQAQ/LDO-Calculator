# -*- coding: utf-8 -*-
"""将 Logo.png 转换为 ICO 格式"""
from PIL import Image
import os

def convert_png_to_ico(png_path, ico_path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]):
    """将 PNG 转换为 ICO 格式"""
    img = Image.open(png_path)
    
    # 确保图像是 RGBA 模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 保存为 ICO
    img.save(ico_path, format='ICO', sizes=sizes)
    print(f"转换成功: {ico_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    png_path = os.path.join(script_dir, "Logo.png")
    ico_path = os.path.join(script_dir, "Logo.ico")
    
    if os.path.exists(png_path):
        convert_png_to_ico(png_path, ico_path)
    else:
        print(f"错误: 找不到 {png_path}")
