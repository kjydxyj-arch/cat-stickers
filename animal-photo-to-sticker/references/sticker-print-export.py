"""
AnimalPhoto2Sticker 印刷导出后处理脚本
功能：将透明底PNG处理为印刷级PSD文件
  1. 调整尺寸：最长边 5cm @ 300DPI
  2. RGB → CMYK 色彩转换
  3. 导出 PSD 格式
使用方法：python3 sticker-print-export.py 输入图.png 输出图.psd
依赖：Pillow, ImageMagick
"""
import sys
import os
import subprocess
from PIL import Image, ImageCms

# 印刷参数
TARGET_DPI = 300
MAX_SIZE_CM = 5  # 最长边 5cm
MAX_SIZE_PX = int(MAX_SIZE_CM / 2.54 * TARGET_DPI)  # ≈ 591px


def export_for_print(input_path, output_path):
    """将透明底PNG导出为印刷级PSD"""
    # 1. 用Pillow调整尺寸和DPI
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    # 计算缩放比例（最长边不超过 MAX_SIZE_PX）
    scale = min(1.0, MAX_SIZE_PX / max(w, h))
    new_w, new_h = int(w * scale), int(h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # 先保存中间PNG（带DPI信息）
    temp_png = "/tmp/_sticker_temp.png"
    img.save(temp_png, dpi=(TARGET_DPI, TARGET_DPI))

    # 2. 用ImageMagick转CMYK + PSD
    cmd = [
        "convert",
        temp_png,
        "-colorspace", "CMYK",
        "-units", "PixelsPerInch",
        "-density", str(TARGET_DPI),
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️ ImageMagick 警告: {result.stderr}")

    # 清理临时文件
    os.remove(temp_png)

    # 验证输出
    out = Image.open(output_path)
    print(f"✅ 印刷文件已输出: {output_path}")
    print(f"   尺寸: {new_w}x{new_h}px (最长边{MAX_SIZE_CM}cm @ {TARGET_DPI}DPI)")
    print(f"   色彩模式: {out.mode}")
    print(f"   格式: PSD")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 sticker-print-export.py <输入图.png> <输出图.psd>")
        print("示例: python3 sticker-print-export.py input.png sticker_output.psd")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    export_for_print(input_file, output_file)
